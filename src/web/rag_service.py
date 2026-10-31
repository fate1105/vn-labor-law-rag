"""
RAG Service Layer — Quản lý thống nhất các mô hình & logic cho Web / API
Hỗ trợ cả Baseline RAG và Effect-Aware RAG, có so sánh song song.
"""

import os
import sys
import time
import sqlite3
import pathlib
import importlib.util
from typing import Optional, Dict, Any, List

import faiss
import pandas as pd
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Đảm bảo PROJECT_ROOT luôn đúng
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Thêm PROJECT_ROOT vào sys.path nếu chưa có
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import EffectChecker từ src/9_effect_checker.py
_spec = importlib.util.spec_from_file_location(
    "effect_checker",
    PROJECT_ROOT / "src" / "9_effect_checker.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
get_checker = _mod.get_checker

# Đường dẫn tài nguyên
INDEX_PATH = PROJECT_ROOT / "data" / "index" / "faiss.index"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "chunk_metadata.parquet"
GRAPH_DB_PATH = PROJECT_ROOT / "data" / "graph" / "legal_graph.db"
DEFAULT_EMBED_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"
DEFAULT_LLM_MODEL = "gemini-2.5-flash"

BASELINE_SYSTEM_PROMPT = """Bạn là trợ lý tra cứu pháp luật lao động Việt Nam.
Nhiệm vụ của bạn là giải đáp câu hỏi của người dùng dựa trên các đoạn văn bản pháp luật được cung cấp trong ngữ cảnh.
- Trả lời đầy đủ, chi tiết, không tóm tắt quá ngắn làm mất thông tin quan trọng.
- Với mỗi ý trả lời, phải trích dẫn rõ nguồn theo định dạng: (Nguồn: <tên văn bản>, Điều <số>, Khoản <số> nếu có).
- Dùng gạch đầu dòng, chia đoạn rõ ràng, dễ đọc."""

EFFECT_AWARE_SYSTEM_PROMPT = """Bạn là trợ lý tra cứu pháp luật lao động Việt Nam có chuyên môn cao.
Nhiệm vụ của bạn là trả lời chính xác, đầy đủ và rõ ràng câu hỏi của người dùng dựa trên các đoạn văn bản pháp luật được cung cấp trong ngữ cảnh.

QUY TẮC QUAN TRỌNG VỀ HIỆU LỰC VĂN BẢN:
1. VĂN BẢN [OK] VÀ [WARNING] (CÒN HIỆU LỰC HOẶC HẾT HIỆU LỰC MỘT PHẦN / SỬA ĐỔI):
   - Các văn bản có nhãn [OK] hoặc [WARNING] (như Bộ luật Lao động 2019, các Luật, Nghị định hiện hành) LÀ CĂN CỨ PHÁP LÝ ĐANG CÓ HIỆU LỰC THI HÀNH.
   - Bạn PHẢI trả lời đầy đủ, chi tiết quy định từ các đoạn này. TUYỆT ĐỐI KHÔNG từ chối trả lời khi thấy nhãn [WARNING].
   - Nếu đoạn trích có nhãn [WARNING], hãy trả lời nội dung câu hỏi trước, sau đó ghi chú ngắn ở cuối: "(Lưu ý: Văn bản này có một số điều khoản đã được sửa đổi/bổ sung theo quy định mới)".

2. VĂN BẢN [DANGER] (HẾT HIỆU LỰC TOÀN BỘ / BỊ THAY THẾ HOÀN TOÀN):
   - Nếu trong ngữ cảnh có cả văn bản [OK]/[WARNING] và văn bản [DANGER], bạn HÃY ƯU TIÊN dùng văn bản [OK]/[WARNING] để trả lời.
   - Nếu TẤT CẢ các đoạn trong ngữ cảnh đều là [DANGER] (nghĩa là chỉ tìm thấy văn bản cũ đã hết hiệu lực, ví dụ các Nghị định lương tối thiểu cũ):
     → Bạn VẪN TRÌNH BÀY nội dung quy định cũ đó để người dùng nắm được thông tin, NHƯNG BẮT BUỘC phải đưa ra CẢNH BÁO RÕ RÀNG ngay đầu câu trả lời:
       "⚠️ CẢNH BÁO PHÁP LÝ: Căn cứ pháp lý tìm thấy ([Tên văn bản]) ĐÃ HẾT HIỆU LỰC / ĐÃ BỊ THAY THẾ. Dưới đây là thông tin theo quy định cũ mang tính chất tham khảo, không còn giá trị áp dụng thực tế hiện nay."

3. HÌNH THỨC CÂU TRẢ LỜI:
   - Trả lời trọn vẹn, không cắt ngang lưng chừng ý nghĩa.
   - Với mỗi ý, bắt buộc trích dẫn rõ ràng: (Nguồn: <tên văn bản>, Điều <số>).
   - Trình bày mạch lạc, có cấu trúc gạch đầu dòng rõ ràng."""


def _call_gemini_with_retry(
    client: genai.Client,
    model: str,
    contents: str,
    config: types.GenerateContentConfig,
    max_retries: int = 3,
) -> Any:
    """Gọi Gemini API với cơ chế retry thông minh khi gặp 503 spike hoặc 429 quota."""
    last_err = None
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            last_err = e
            err_str = str(e)
            # Nếu gặp 503 (quá tải tạm thời) hoặc 429 (vượt quota tạm thời)
            if any(code in err_str for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]):
                wait_time = 2.0 * (attempt + 1)
                time.sleep(wait_time)
            else:
                time.sleep(1.0)
    raise last_err


class RAGService:
    _instance: Optional["RAGService"] = None

    def __init__(self):
        print("🔄 [RAGService] Khởi tạo tài nguyên hệ thống...")
        t0 = time.time()
        
        self.index = faiss.read_index(str(INDEX_PATH))
        self.meta = pd.read_parquet(str(METADATA_PATH))
        self.embed_model = SentenceTransformer(DEFAULT_EMBED_MODEL)
        self.effect_checker = get_checker()
        self.gemini_client = genai.Client()
        
        # SQLite connection để tra cứu nhanh thông tin văn bản
        self.db_conn = sqlite3.connect(str(GRAPH_DB_PATH), check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row

        print(f"✅ [RAGService] Khởi tạo thành công ({time.time() - t0:.2f}s) — Index: {self.index.ntotal:,} vectors")

    @classmethod
    def get_instance(cls) -> "RAGService":
        if cls._instance is None:
            cls._instance = RAGService()
        return cls._instance

    # ── 1. Retrieval ─────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 7) -> List[Dict[str, Any]]:
        """Truy xuất top_k chunks từ FAISS theo cosine similarity."""
        q_seg = ViTokenizer.tokenize(query)
        q_vec = self.embed_model.encode(
            [q_seg], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")

        scores, indices = self.index.search(q_vec, top_k)

        chunks = []
        for score, idx in zip(scores[0], indices[0]):
            row = self.meta.iloc[idx]
            chunks.append({
                "score": float(score),
                "doc_id": str(row["doc_id"]),
                "doc_title": str(row["doc_title"]),
                "dieu_so": str(row["dieu_so"]),
                "khoan_so": row.get("khoan_so") if pd.notna(row.get("khoan_so")) else None,
                "text": str(row["text"]),
                "matched_group": str(row.get("matched_group", "")),
                "issue_date": str(row.get("issue_date", "")),
                "effect_status_source": str(row.get("effect_status_source", "Chưa xác định")),
            })
        return chunks

    # ── 2. Baseline RAG ──────────────────────────────────────────────────────

    def build_baseline_context(self, chunks: List[Dict[str, Any]]) -> str:
        parts = []
        for i, c in enumerate(chunks, start=1):
            khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""
            parts.append(
                f"[Đoạn {i}] Nguồn: {c['doc_title']}, Điều {c['dieu_so']}{khoan}\n{c['text']}"
            )
        return "\n\n".join(parts)

    def run_baseline(
        self,
        query: str,
        top_k: int = 5,
        model_name: str = DEFAULT_LLM_MODEL,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Thực thi pipeline Baseline RAG (không kiểm tra hiệu lực)."""
        t0 = time.time()
        chunks = self.retrieve(query, top_k=top_k)
        context = self.build_baseline_context(chunks)

        user_message = f"""Ngữ cảnh (các đoạn văn bản pháp luật liên quan):
{context}

Câu hỏi: {query}"""

        try:
            response = _call_gemini_with_retry(
                client=self.gemini_client,
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=BASELINE_SYSTEM_PROMPT,
                    temperature=temperature,
                    max_output_tokens=3072,  # Tăng lên 3072 để không bị cắt chữ
                ),
            )
            answer = response.text or "(Không có phản hồi từ LLM)"
        except Exception as e:
            err_str = str(e)
            if "429" in err_str:
                answer = "⚠️ Hệ thống đang đạt giới hạn số lượng câu hỏi/phút của gói Gemini miễn phí (5 requests/phút). Vui lòng đợi khoảng 15-30 giây rồi thử lại."
            elif "503" in err_str:
                answer = "⚠️ Máy chủ Google Gemini tạm thời quá tải trong giây lát. Vui lòng bấm thử lại câu hỏi."
            else:
                answer = f"⚠️ Lỗi khi gọi Gemini API ({model_name}): {err_str}"

        elapsed = time.time() - t0
        return {
            "mode": "baseline",
            "query": query,
            "answer": answer,
            "chunks": chunks,
            "latency": elapsed,
        }

    # ── 3. Effect-Aware RAG ──────────────────────────────────────────────────

    def run_effect_aware(
        self,
        query: str,
        top_k_retrieve: int = 7,
        top_k_llm: int = 5,
        model_name: str = DEFAULT_LLM_MODEL,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Thực thi pipeline Effect-Aware RAG (có gắn nhãn hiệu lực & rerank)."""
        t0 = time.time()
        raw_chunks = self.retrieve(query, top_k=top_k_retrieve)
        
        # Gắn thông tin hiệu lực và rerank (OK > WARNING > UNKNOWN > DANGER)
        enriched_chunks = self.effect_checker.check_chunks(raw_chunks)
        top_for_llm = enriched_chunks[:top_k_llm]

        # Xây dựng ngữ cảnh kèm cảnh báo hiệu lực
        context = self.effect_checker.build_context_with_warning(top_for_llm)

        user_message = f"""Ngữ cảnh (các đoạn văn bản pháp luật liên quan, kèm trạng thái hiệu lực):
{context}

Câu hỏi: {query}"""

        try:
            response = _call_gemini_with_retry(
                client=self.gemini_client,
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=EFFECT_AWARE_SYSTEM_PROMPT,
                    temperature=temperature,
                    max_output_tokens=3072,  # Tăng lên 3072 để không bị cắt chữ
                ),
            )
            answer = response.text or "(Không có phản hồi từ LLM)"
        except Exception as e:
            err_str = str(e)
            if "429" in err_str:
                answer = "⚠️ Hệ thống đang đạt giới hạn số lượng câu hỏi/phút của gói Gemini miễn phí (5 requests/phút). Vui lòng đợi khoảng 15-30 giây rồi thử lại."
            elif "503" in err_str:
                answer = "⚠️ Máy chủ Google Gemini tạm thời quá tải trong giây lát. Vui lòng bấm thử lại câu hỏi."
            else:
                answer = f"⚠️ Lỗi khi gọi Gemini API ({model_name}): {err_str}"

        # Thống kê phân bố hiệu lực
        stats = {"OK": 0, "WARNING": 0, "DANGER": 0, "UNKNOWN": 0}
        for c in enriched_chunks:
            lvl = c.get("effect_level", "UNKNOWN")
            stats[lvl] = stats.get(lvl, 0) + 1

        llm_stats = {"OK": 0, "WARNING": 0, "DANGER": 0, "UNKNOWN": 0}
        for c in top_for_llm:
            lvl = c.get("effect_level", "UNKNOWN")
            llm_stats[lvl] = llm_stats.get(lvl, 0) + 1

        elapsed = time.time() - t0
        return {
            "mode": "effect_aware",
            "query": query,
            "answer": answer,
            "all_chunks": enriched_chunks,
            "llm_chunks": top_for_llm,
            "stats_all": stats,
            "stats_llm": llm_stats,
            "latency": elapsed,
        }

    # ── 4. Comparison (Side-by-side) ─────────────────────────────────────────

    def compare(
        self,
        query: str,
        top_k_retrieve: int = 7,
        top_k_llm: int = 5,
        model_name: str = DEFAULT_LLM_MODEL,
    ) -> Dict[str, Any]:
        """Chạy so sánh đối chứng giữa Baseline RAG và Effect-Aware RAG."""
        t0 = time.time()
        
        # 1. Chạy Baseline RAG
        baseline_res = self.run_baseline(query, top_k=top_k_llm, model_name=model_name)
        
        # Nghỉ 1 giây để tránh spike đồng thời gây rate limit 429 trên Gemini Free
        time.sleep(1.0)
        
        # 2. Chạy Effect-Aware RAG
        effect_res = self.run_effect_aware(
            query, top_k_retrieve=top_k_retrieve, top_k_llm=top_k_llm, model_name=model_name
        )

        # Phát hiện sự khác biệt mấu chốt
        baseline_danger_count = 0
        for c in baseline_res["chunks"]:
            st = self.effect_checker.check_effect_status(c["doc_id"])
            if st.level.value in ("DANGER", "WARNING"):
                baseline_danger_count += 1

        has_diff = (baseline_danger_count > 0) or (
            effect_res["stats_llm"]["WARNING"] + effect_res["stats_llm"]["DANGER"] > 0
        )

        return {
            "query": query,
            "baseline": baseline_res,
            "effect_aware": effect_res,
            "has_diff": has_diff,
            "baseline_risky_chunks": baseline_danger_count,
            "total_latency": time.time() - t0,
        }

    # ── 5. Tiện ích tra cứu quan hệ & văn bản ────────────────────────────────

    def search_docs(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Tìm kiếm văn bản theo tiêu đề hoặc doc_id từ SQLite."""
        cur = self.db_conn.execute(
            """
            SELECT doc_id, title, effect_status FROM documents
            WHERE title LIKE ? OR doc_id = ?
            LIMIT ?
            """,
            (f"%{keyword}%", keyword, limit),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_doc_relations(self, doc_id: str) -> Dict[str, Any]:
        """Tra cứu chi tiết trạng thái hiệu lực & chuỗi quan hệ của 1 văn bản."""
        status = self.effect_checker.check_effect_status(doc_id)
        
        cur = self.db_conn.execute(
            """
            SELECT * FROM relationships
            WHERE doc_id = ? OR other_doc_id = ?
            ORDER BY importance DESC
            """,
            (str(doc_id), str(doc_id)),
        )
        rels = []
        for r in cur.fetchall():
            row = dict(r)
            target_id = row["other_doc_id"] if row["doc_id"] == str(doc_id) else row["doc_id"]
            t_cur = self.db_conn.execute("SELECT title FROM documents WHERE doc_id = ?", (target_id,))
            t_row = t_cur.fetchone()
            row["counterpart_title"] = t_row["title"] if t_row else f"(Văn bản ngoài scope ID: {target_id})"
            rels.append(row)

        return {
            "doc_id": status.doc_id,
            "title": status.title,
            "level": status.level.value,
            "source_status": status.source_status,
            "message": status.message,
            "relationships": rels,
        }
