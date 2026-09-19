"""
TUẦN 11 — MÔ-ĐUN KIỂM TRA TRẠNG THÁI HIỆU LỰC & TRUY VẾT CHUỖI QUAN HỆ
----------------------------------------------------
Input:  data/graph/legal_graph.gpickle     (đồ thị NetworkX từ Tuần 10)
        data/graph/legal_graph.db          (SQLite để truy vấn nhanh)
        data/processed/chunk_metadata.parquet

Output: Module Python — không tạo file, được import bởi 10_effect_aware_rag.py

Chức năng chính:
  1. check_effect_status(doc_id)
     → Trả về trạng thái hiệu lực tổng hợp của một văn bản:
       • Lấy effect_status_source từ metadata gốc
       • Truy vết đồ thị: có văn bản nào THAY_THE / BAI_BO nó không?
       • Trả về EffectStatus(level, message, related_docs)

  2. check_chunks(chunks)
     → Nhận danh sách chunk đã truy xuất (từ FAISS), gắn thêm thông tin
       hiệu lực cho mỗi chunk, sắp xếp lại theo mức độ tin cậy.

  3. build_warning(chunk, status)
     → Sinh chuỗi cảnh báo hiệu lực cho LLM biết để đưa vào câu trả lời.

Mức độ cảnh báo (EffectLevel):
  OK        — còn hiệu lực, không bị tác động
  WARNING   — hết hiệu lực một phần HOẶC bị sửa đổi bởi văn bản khác
  DANGER    — hết hiệu lực toàn bộ HOẶC bị thay thế / bãi bỏ hoàn toàn
  UNKNOWN   — trạng thái chưa xác định

Cách chạy độc lập (demo):
    python src/9_effect_checker.py "<doc_id>"
"""

import pickle
import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import pandas as pd
import networkx as nx

GRAPH_PICKLE = "data/graph/legal_graph.gpickle"
GRAPH_DB = "data/graph/legal_graph.db"
METADATA_PATH = "data/processed/chunk_metadata.parquet"

# ── Trạng thái hiệu lực từ metadata gốc ──────────────────────────────────────
# Ánh xạ giá trị chuỗi → mức độ cảnh báo
STATUS_SOURCE_MAP = {
    "Còn hiệu lực":            "OK",
    "Hết hiệu lực một phần":   "WARNING",
    "Ngưng hiệu lực một phần": "WARNING",
    "Ngưng hiệu lực":          "DANGER",
    "Hết hiệu lực toàn bộ":    "DANGER",
    "Không còn phù hợp":       "DANGER",
    "Chưa có hiệu lực":        "WARNING",
    "Chưa xác định":           "UNKNOWN",
}

# Loại quan hệ ảnh hưởng hiệu lực (cần cảnh báo)
EFFECT_REL_TYPES = {"THAY_THE", "BAI_BO", "SUA_DOI"}


class EffectLevel(str, Enum):
    OK      = "OK"
    WARNING = "WARNING"
    DANGER  = "DANGER"
    UNKNOWN = "UNKNOWN"


@dataclass
class RelatedDoc:
    doc_id: str
    title: str
    rel_type: str       # THAY_THE / BAI_BO / SUA_DOI
    direction: str      # OUTGOING (ta tác động) / INCOMING (ta bị tác động)
    effect_status: str


@dataclass
class EffectStatus:
    doc_id: str
    title: str
    source_status: str                          # trạng thái gốc từ metadata
    level: EffectLevel                          # mức cảnh báo tổng hợp
    message: str                                # chuỗi cảnh báo ngắn gọn cho LLM
    affecting_docs: list[RelatedDoc] = field(default_factory=list)   # văn bản tác động vào doc này
    affected_docs:  list[RelatedDoc] = field(default_factory=list)   # văn bản bị doc này tác động


class EffectChecker:
    """Mô-đun kiểm tra hiệu lực văn bản pháp luật."""

    def __init__(self):
        self._graph: Optional[nx.DiGraph] = None
        self._db_conn: Optional[sqlite3.Connection] = None
        self._meta: Optional[pd.DataFrame] = None

    # ── Lazy loading ─────────────────────────────────────────────────────────

    @property
    def graph(self) -> nx.DiGraph:
        if self._graph is None:
            with open(GRAPH_PICKLE, "rb") as f:
                self._graph = pickle.load(f)
        return self._graph

    @property
    def db(self) -> sqlite3.Connection:
        if self._db_conn is None:
            self._db_conn = sqlite3.connect(GRAPH_DB, check_same_thread=False)
            self._db_conn.row_factory = sqlite3.Row
        return self._db_conn

    @property
    def meta(self) -> pd.DataFrame:
        if self._meta is None:
            self._meta = pd.read_parquet(METADATA_PATH)
        return self._meta

    # ── Core methods ──────────────────────────────────────────────────────────

    def _get_doc_info(self, doc_id: str) -> dict:
        """Lấy thông tin văn bản từ SQLite (nhanh hơn đọc parquet)."""
        cur = self.db.execute(
            "SELECT * FROM documents WHERE doc_id = ?", (str(doc_id),)
        )
        row = cur.fetchone()
        if row:
            return dict(row)
        return {"doc_id": doc_id, "title": "", "effect_status": "Chưa xác định"}

    def _get_relations(self, doc_id: str) -> list[dict]:
        """Lấy tất cả quan hệ THAY_THE/BAI_BO/SUA_DOI liên quan đến doc_id."""
        cur = self.db.execute(
            """
            SELECT * FROM relationships
            WHERE (doc_id = ? OR other_doc_id = ?)
              AND rel_type IN ('THAY_THE', 'BAI_BO', 'SUA_DOI')
            ORDER BY importance DESC
            """,
            (str(doc_id), str(doc_id)),
        )
        return [dict(r) for r in cur.fetchall()]

    def check_effect_status(self, doc_id: str) -> EffectStatus:
        """
        Kiểm tra trạng thái hiệu lực tổng hợp của một văn bản.

        Logic:
          1. Đọc effect_status_source từ DB (giá trị gốc vbpl.vn)
          2. Tra đồ thị: có văn bản nào THAY_THE/BAI_BO nó không?
          3. Tổng hợp → EffectLevel và message cảnh báo
        """
        doc_id = str(doc_id)
        info = self._get_doc_info(doc_id)
        title = info.get("title", "")
        source_status = info.get("effect_status", "Chưa xác định")

        # Mức cảnh báo ban đầu từ metadata gốc
        base_level_str = STATUS_SOURCE_MAP.get(source_status, "UNKNOWN")

        relations = self._get_relations(doc_id)
        affecting = []   # văn bản khác tác động LÊN doc_id
        affected  = []   # doc_id tác động LÊN văn bản khác

        for r in relations:
            other_id = r["other_doc_id"] if r["doc_id"] == doc_id else r["doc_id"]
            other_info = self._get_doc_info(other_id)
            rel_doc = RelatedDoc(
                doc_id=other_id,
                title=other_info.get("title", ""),
                rel_type=r["rel_type"],
                direction=r["direction"],
                effect_status=other_info.get("effect_status", ""),
            )

            # Nếu doc_id là nguồn phát quan hệ (OUTGOING) → ta tác động lên other
            if r["doc_id"] == doc_id and r["direction"] == "OUTGOING":
                affected.append(rel_doc)
            # Nếu other_doc_id là ta, và other là OUTGOING → ta bị tác động
            elif r["other_doc_id"] == doc_id and r["direction"] == "OUTGOING":
                affecting.append(rel_doc)

        # Nâng cấp mức cảnh báo nếu bị tác động bởi THAY_THE hoặc BAI_BO
        final_level = EffectLevel(base_level_str)
        for a in affecting:
            if a.rel_type in {"THAY_THE", "BAI_BO"}:
                final_level = EffectLevel.DANGER
                break
            elif a.rel_type == "SUA_DOI" and final_level == EffectLevel.OK:
                final_level = EffectLevel.WARNING

        # Sinh message cảnh báo
        message = self._build_status_message(
            source_status, final_level, affecting, doc_id, title
        )

        return EffectStatus(
            doc_id=doc_id,
            title=title,
            source_status=source_status,
            level=final_level,
            message=message,
            affecting_docs=affecting,
            affected_docs=affected,
        )

    def _build_status_message(
        self,
        source_status: str,
        level: EffectLevel,
        affecting: list[RelatedDoc],
        doc_id: str,
        title: str,
    ) -> str:
        """Sinh chuỗi cảnh báo ngắn gọn cho LLM đưa vào câu trả lời."""
        short_title = title[:60] + "..." if len(title) > 60 else title

        if level == EffectLevel.OK and not affecting:
            return f"[CÒN HIỆU LỰC] {short_title}"

        parts = [f"[{level.value}]"]

        if source_status not in {"Còn hiệu lực", "Chưa xác định"}:
            parts.append(f"Trạng thái gốc: {source_status}.")

        for a in affecting[:2]:  # chỉ hiện tối đa 2 văn bản tác động
            verb = {
                "THAY_THE": "đã bị thay thế bởi",
                "BAI_BO":   "đã bị bãi bỏ/đình chỉ bởi",
                "SUA_DOI":  "đã bị sửa đổi bởi",
            }.get(a.rel_type, "bị tác động bởi")
            a_title = a.title[:50] + "..." if len(a.title) > 50 else a.title
            parts.append(f"Văn bản {verb} {a_title} (doc_id={a.doc_id}).")

        if len(affecting) > 2:
            parts.append(f"(và {len(affecting) - 2} văn bản khác)")

        return " ".join(parts)

    def check_chunks(self, chunks: list[dict]) -> list[dict]:
        """
        Nhận danh sách chunk từ FAISS retrieval, gắn thêm thông tin hiệu lực.

        Input:  [{"doc_id": ..., "score": ..., "text": ..., ...}, ...]
        Output: danh sách chunk đã bổ sung {"effect_status": EffectStatus, ...}
                sắp xếp: chunk OK lên trước, DANGER xuống sau
        """
        results = []
        for chunk in chunks:
            doc_id = str(chunk.get("doc_id", ""))
            status = self.check_effect_status(doc_id)
            enriched = dict(chunk)
            enriched["effect_status"] = status
            enriched["effect_level"] = status.level.value
            enriched["effect_message"] = status.message
            results.append(enriched)

        # Sắp xếp: OK > WARNING > UNKNOWN > DANGER (theo mức tin cậy)
        level_order = {"OK": 0, "WARNING": 1, "UNKNOWN": 2, "DANGER": 3}
        results.sort(key=lambda x: level_order.get(x["effect_level"], 99))
        return results

    def build_context_with_warning(self, chunks: list[dict]) -> str:
        """
        Ghép context cho LLM — giống build_context() của baseline_rag nhưng
        kèm cảnh báo hiệu lực cho mỗi đoạn văn bản.

        Dùng trong Effect-Aware RAG (Tuần 12).
        """
        parts = []
        for i, c in enumerate(chunks, start=1):
            status: EffectStatus = c.get("effect_status")
            khoan = f", Khoản {c['khoan_so']}" if pd.notna(c.get("khoan_so")) else ""
            source_line = f"Nguồn: {c['doc_title']}, Điều {c['dieu_so']}{khoan}"

            if status:
                warning = f"⚠️  {status.message}" if status.level != EffectLevel.OK else ""
            else:
                warning = ""

            block = f"[Đoạn {i}] {source_line}\n"
            if warning:
                block += f"{warning}\n"
            block += c["text"]
            parts.append(block)

        return "\n\n".join(parts)


# ── Singleton instance (import và dùng trực tiếp) ────────────────────────────
_checker: Optional[EffectChecker] = None


def get_checker() -> EffectChecker:
    """Trả về singleton EffectChecker (lazy-loaded)."""
    global _checker
    if _checker is None:
        _checker = EffectChecker()
    return _checker


# ── CLI demo ─────────────────────────────────────────────────────────────────
def _demo():
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    checker = get_checker()

    # Nếu không truyền doc_id, lấy mẫu ngẫu nhiên từ metadata
    if len(sys.argv) > 1:
        doc_ids = [sys.argv[1]]
    else:
        meta = checker.meta
        # Lấy vài doc_id mẫu: ưu tiên exact_title, còn hiệu lực
        sample = meta[meta.get("matched_group", pd.Series()) == "exact_title"] if "matched_group" in meta.columns else meta
        doc_ids = sample["doc_id"].astype(str).drop_duplicates().head(3).tolist()
        if not doc_ids:
            doc_ids = meta["doc_id"].astype(str).drop_duplicates().head(3).tolist()

    print("=" * 60)
    print("DEMO: Kiểm tra hiệu lực văn bản")
    print("=" * 60)

    for doc_id in doc_ids:
        status = checker.check_effect_status(doc_id)
        print(f"\nDoc ID: {doc_id}")
        print(f"  Tiêu đề    : {status.title[:70]}")
        print(f"  Trạng thái gốc: {status.source_status}")
        print(f"  Mức cảnh báo : {status.level.value}")
        print(f"  Message      : {status.message}")
        if status.affecting_docs:
            print(f"  Văn bản tác động lên nó ({len(status.affecting_docs)}):")
            for a in status.affecting_docs[:3]:
                print(f"    [{a.rel_type}] {a.doc_id}: {a.title[:60]}")
        if status.affected_docs:
            print(f"  Văn bản nó tác động ({len(status.affected_docs)}):")
            for a in status.affected_docs[:3]:
                print(f"    [{a.rel_type}] {a.doc_id}: {a.title[:60]}")


if __name__ == "__main__":
    _demo()
