"""
TUẦN 6 — LỰA CHỌN MÔ HÌNH EMBEDDING & TẠO VECTOR
----------------------------------------------------
Input:  data/processed/segmented_chunks.csv   (từ segment.py)
Output: data/processed/chunk_embeddings.npy    (ma trận vector, dùng cho tuần 7)
        data/processed/chunk_metadata.parquet  (map thứ tự vector -> chunk gốc)

Model đã chọn: bkai-foundation-models/vietnamese-bi-encoder
- Backbone PhoBERT-base-v2.
- Đã huấn luyện một phần trên Legal Text Retrieval Zalo 2021 (bài toán
  truy xuất văn bản pháp lý tiếng Việt) -> phù hợp trực tiếp, không cần
  train from scratch.
- Yêu cầu văn bản đã tách từ (word-segmented) trước khi encode -> dùng
  thư viện `pyvi`.

Kết quả dự kiến: hoàn thành bộ vector embedding của dữ liệu pháp luật
(chưa lập chỉ mục tìm kiếm — việc đó thuộc tuần 7 trong index.py).
"""

import numpy as np
import pandas as pd
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer

MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
INPUT_PATH = "data/processed/segmented_chunks.csv"
EMBEDDINGS_OUT = "data/processed/chunk_embeddings.npy"
METADATA_OUT = "data/processed/chunk_metadata.parquet"
BATCH_SIZE = 64


def word_segment(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    return ViTokenizer.tokenize(text)


def main():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig").reset_index(drop=True)
    print(f"Số chunk cần encode: {len(df):,}")

    print(f"Đang tải model: {MODEL_NAME} (lần đầu sẽ tự tải ~500MB)...")
    model = SentenceTransformer(MODEL_NAME)

    print("Đang tách từ (word segmentation) bằng pyvi...")
    segmented_texts = [word_segment(t) for t in df["text"].tolist()]

    print("Đang tạo embedding...")
    embeddings = model.encode(
        segmented_texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,   # để tuần 7 dùng Inner Product ~ Cosine similarity
        convert_to_numpy=True,
    ).astype("float32")

    np.save(EMBEDDINGS_OUT, embeddings)
    df.to_parquet(METADATA_OUT, index=True)

    print(f"\nĐã tạo {embeddings.shape[0]:,} vector, dim={embeddings.shape[1]}")
    print(f"Lưu tại: {EMBEDDINGS_OUT} và {METADATA_OUT}")


if __name__ == "__main__":
    main()
