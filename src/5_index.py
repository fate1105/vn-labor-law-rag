"""
TUẦN 7 — XÂY DỰNG CHỈ MỤC FAISS & TÌM KIẾM NGỮ NGHĨA
----------------------------------------------------
Input:  data/processed/chunk_embeddings.npy, chunk_metadata.parquet (từ embed.py)
Output: data/index/faiss.index

Kết quả dự kiến: hệ thống có khả năng truy hồi các Điều, Khoản liên quan
đến câu hỏi.

Cách chạy:
    python src/index.py                         # xây chỉ mục
    python src/index.py "câu hỏi cần tra cứu"    # xây chỉ mục xong, tìm kiếm thử
"""

import os
import sys
import faiss
import numpy as np
import pandas as pd
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer

MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
EMBEDDINGS_PATH = "data/processed/chunk_embeddings.npy"
METADATA_PATH = "data/processed/chunk_metadata.parquet"
INDEX_DIR = "data/index"
TOP_K = 5


def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)
    embeddings = np.load(EMBEDDINGS_PATH)
    dim = embeddings.shape[1]

    # IndexFlatIP: Inner Product trên vector đã normalize = cosine similarity.
    # Với vài nghìn chunk, Flat index đủ nhanh, chưa cần IVF/HNSW.
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    index_path = os.path.join(INDEX_DIR, "faiss.index")
    faiss.write_index(index, index_path)
    print(f"Đã lập chỉ mục: {index.ntotal:,} vector -> {index_path}")
    return index


def search(index, query: str, top_k: int = TOP_K):
    meta = pd.read_parquet(METADATA_PATH)
    model = SentenceTransformer(MODEL_NAME)

    q_seg = ViTokenizer.tokenize(query)
    q_vec = model.encode([q_seg], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    scores, indices = index.search(q_vec, top_k)

    print(f"\nCâu hỏi: {query}")
    print(f"Top {top_k} kết quả truy xuất:\n")
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        row = meta.iloc[idx]
        khoan = f" Khoản {row['khoan_so']}" if pd.notna(row.get("khoan_so")) else ""
        print(f"[{rank}] score={score:.4f} | {row['doc_title']} — Điều {row['dieu_so']}{khoan}")
        print(f"    {row['text'][:150]}...\n")


def main():
    index = build_index()
    if len(sys.argv) > 1:
        query = sys.argv[1]
        search(index, query)


if __name__ == "__main__":
    main()
