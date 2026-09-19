"""
TUẦN 10 — XÂY DỰNG ĐỒ THỊ QUAN HỆ VĂN BẢN (NetworkX) + LƯU TRỮ SQLite
----------------------------------------------------
Input:  data/processed/relationships_clean.csv  (từ 7_relationships.py)
        data/raw/filtered_documents.csv         (metadata văn bản)
Output: data/graph/legal_graph.gpickle          (đồ thị NetworkX)
        data/graph/legal_graph.db               (SQLite — truy vấn nhanh)

Kiến trúc đồ thị:
  - Node: mỗi văn bản pháp luật (doc_id)
    Attributes: title, effect_status_source, matched_group, issue_date
  - Edge: quan hệ giữa hai văn bản
    Attributes: rel_type, direction, importance, relationship (tên gốc)

Tính năng truy vấn:
  - Lấy tất cả văn bản THAY_THE / BAI_BO / SUA_DOI một văn bản
  - Truy vết chuỗi: A thay thế B → B thay thế C → ... (BFS)
  - Kiểm tra nhanh: văn bản này có bị tác động bởi văn bản nào không?

Cách chạy:
    python src/8_build_graph.py                       # xây đồ thị
    python src/8_build_graph.py "doc_id_cần_truy vết" # xây + demo truy vết
"""

import os
import sys
import sqlite3
import pickle
import pandas as pd
import networkx as nx

REL_PATH = "data/processed/relationships_clean.csv"
DOCS_PATH = "data/raw/filtered_documents.csv"
GRAPH_DIR = "data/graph"
GRAPH_PICKLE = os.path.join(GRAPH_DIR, "legal_graph.gpickle")
GRAPH_DB = os.path.join(GRAPH_DIR, "legal_graph.db")

# Loại quan hệ ảnh hưởng hiệu lực — dùng để cảnh báo trong Effect-Aware RAG
EFFECT_REL_TYPES = {"THAY_THE", "BAI_BO", "SUA_DOI"}


def build_graph(docs: pd.DataFrame, rels: pd.DataFrame) -> nx.DiGraph:
    """Xây dựng DiGraph: node là văn bản, edge là quan hệ có chiều."""
    G = nx.DiGraph()

    # Thêm nodes — tất cả văn bản trong filtered_documents
    for _, row in docs.iterrows():
        G.add_node(
            str(row["doc_id"]),
            title=str(row.get("title", "")),
            effect_status=str(row.get("effect_status_source", "Chưa xác định")),
            matched_group=str(row.get("matched_group", "")),
            issue_date=str(row.get("issue_date", "")),
            in_scope=True,
        )

    # Thêm edges từ relationships_clean
    for _, row in rels.iterrows():
        src = str(row["doc_id"])
        dst = str(row["other_doc_id"])

        # Đảm bảo node tồn tại (có thể other_doc_id không trong filtered_docs)
        if src not in G:
            G.add_node(src, in_scope=False)
        if dst not in G:
            G.add_node(dst, in_scope=False)

        G.add_edge(
            src, dst,
            rel_type=row["rel_type"],
            direction=row["direction"],
            importance=int(row["importance"]),
            relationship_raw=row.get("relationship", ""),
        )

    return G


def save_to_sqlite(G: nx.DiGraph, rels: pd.DataFrame, docs: pd.DataFrame):
    """Lưu graph vào SQLite để truy vấn nhanh không cần load NetworkX."""
    conn = sqlite3.connect(GRAPH_DB)
    c = conn.cursor()

    # Bảng documents
    c.execute("DROP TABLE IF EXISTS documents")
    c.execute("""
        CREATE TABLE documents (
            doc_id TEXT PRIMARY KEY,
            title TEXT,
            effect_status TEXT,
            matched_group TEXT,
            issue_date TEXT,
            in_scope INTEGER DEFAULT 1
        )
    """)
    for _, row in docs.iterrows():
        c.execute(
            "INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)",
            (
                str(row["doc_id"]),
                str(row.get("title", "")),
                str(row.get("effect_status_source", "")),
                str(row.get("matched_group", "")),
                str(row.get("issue_date", "")),
                1,
            )
        )

    # Bảng relationships
    c.execute("DROP TABLE IF EXISTS relationships")
    c.execute("""
        CREATE TABLE relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            other_doc_id TEXT NOT NULL,
            rel_type TEXT NOT NULL,
            direction TEXT NOT NULL,
            importance INTEGER DEFAULT 1,
            relationship_raw TEXT,
            both_in_scope INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_rel_doc ON relationships(doc_id);
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_rel_other ON relationships(other_doc_id);
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(rel_type);
    """)

    for _, row in rels.iterrows():
        c.execute(
            "INSERT INTO relationships (doc_id, other_doc_id, rel_type, direction, importance, relationship_raw, both_in_scope) VALUES (?,?,?,?,?,?,?)",
            (
                str(row["doc_id"]),
                str(row["other_doc_id"]),
                row["rel_type"],
                row["direction"],
                int(row["importance"]),
                str(row.get("relationship", "")),
                int(bool(row.get("both_in_scope", False))),
            )
        )

    conn.commit()
    conn.close()
    print(f"SQLite lưu tại: {GRAPH_DB}")


def query_affected_by(G: nx.DiGraph, doc_id: str, rel_types=None) -> list:
    """Tìm tất cả văn bản TÁC ĐỘNG LÊN doc_id (predecessors theo rel_type)."""
    if rel_types is None:
        rel_types = EFFECT_REL_TYPES
    result = []
    for src, _, data in G.in_edges(doc_id, data=True):
        if data.get("rel_type") in rel_types:
            result.append({
                "doc_id": src,
                "rel_type": data["rel_type"],
                "title": G.nodes[src].get("title", ""),
                "effect_status": G.nodes[src].get("effect_status", ""),
            })
    return result


def trace_chain(G: nx.DiGraph, doc_id: str, rel_types=None, max_depth: int = 5) -> list:
    """Truy vết chuỗi quan hệ từ doc_id (BFS theo chiều outgoing).

    Ví dụ: Luật A sửa đổi Luật B → Luật B sửa đổi Luật C → ...
    """
    if rel_types is None:
        rel_types = {"THAY_THE", "BAI_BO"}

    visited = set()
    queue = [(doc_id, 0, [])]
    chains = []

    while queue:
        node, depth, path = queue.pop(0)
        if depth >= max_depth or node in visited:
            continue
        visited.add(node)

        for _, dst, data in G.out_edges(node, data=True):
            if data.get("rel_type") in rel_types:
                new_path = path + [{"from": node, "to": dst,
                                     "rel_type": data["rel_type"]}]
                chains.append(new_path)
                queue.append((dst, depth + 1, new_path))

    return chains


def print_graph_stats(G: nx.DiGraph):
    print(f"\n{'='*55}")
    print("THỐNG KÊ ĐỒ THỊ QUAN HỆ VĂN BẢN")
    print(f"{'='*55}")
    print(f"Số node (văn bản): {G.number_of_nodes():,}")
    print(f"Số edge (quan hệ): {G.number_of_edges():,}")

    in_scope = [n for n, d in G.nodes(data=True) if d.get("in_scope")]
    print(f"Node trong phạm vi đề tài: {len(in_scope):,}")

    # Phân bố edge theo rel_type
    type_counts = {}
    for _, _, d in G.edges(data=True):
        t = d.get("rel_type", "UNKNOWN")
        type_counts[t] = type_counts.get(t, 0) + 1
    print("\nPhân bố edge theo rel_type:")
    for t, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t:<12}: {cnt:,}")

    # Top 5 node có nhiều quan hệ nhất
    degrees = sorted(G.degree(), key=lambda x: -x[1])[:5]
    print("\nTop 5 văn bản có nhiều quan hệ nhất:")
    for node_id, deg in degrees:
        title = G.nodes[node_id].get("title", "")[:60]
        print(f"  [{deg:>4} edges] {node_id}: {title}")


def main():
    os.makedirs(GRAPH_DIR, exist_ok=True)

    print("Đang đọc relationships_clean.csv...")
    rels = pd.read_csv(REL_PATH, encoding="utf-8-sig")
    print(f"Quan hệ: {len(rels):,}")

    print("Đang đọc filtered_documents.csv...")
    docs = pd.read_csv(DOCS_PATH, encoding="utf-8-sig")
    print(f"Văn bản: {len(docs):,}")

    print("\nĐang xây dựng đồ thị NetworkX...")
    G = build_graph(docs, rels)
    print_graph_stats(G)

    # Lưu đồ thị
    print(f"\nĐang lưu đồ thị (pickle)...")
    with open(GRAPH_PICKLE, "wb") as f:
        pickle.dump(G, f)
    print(f"Đồ thị lưu tại: {GRAPH_PICKLE}")

    print("Đang lưu vào SQLite...")
    save_to_sqlite(G, rels, docs)

    # Demo truy vết nếu truyền doc_id qua command line
    if len(sys.argv) > 1:
        doc_id = sys.argv[1]
        print(f"\n{'='*55}")
        print(f"DEMO: Truy vết quan hệ cho doc_id={doc_id}")
        print(f"{'='*55}")

        affected = query_affected_by(G, doc_id)
        if affected:
            print(f"\nVăn bản TÁC ĐỘNG LÊN {doc_id}:")
            for a in affected:
                print(f"  [{a['rel_type']}] {a['doc_id']}: {a['title'][:60]}")
        else:
            print(f"\nKhông có văn bản nào tác động lên {doc_id}")

        chains = trace_chain(G, doc_id)
        if chains:
            print(f"\nChuỗi quan hệ từ {doc_id}:")
            for chain in chains[:5]:
                path_str = " → ".join([f"{s['from']}-[{s['rel_type']}]->{s['to']}" for s in chain])
                print(f"  {path_str}")

    print("\nTuần 10 hoàn thành.")


if __name__ == "__main__":
    main()
