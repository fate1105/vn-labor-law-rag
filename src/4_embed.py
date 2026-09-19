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
import torch
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer

MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
INPUT_PATH = "data/processed/segmented_chunks.csv"
EMBEDDINGS_OUT = "data/processed/chunk_embeddings.npy"
METADATA_OUT = "data/processed/chunk_metadata.parquet"
# CPU: 128 vừa đủ RAM, tăng throughput so với 64.
# Nếu có GPU sẽ tự động dùng; tăng lên 256+ khi GPU có ≥ 6GB VRAM.
BATCH_SIZE = 128


def word_segment(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    return ViTokenizer.tokenize(text)


def main():
    import time
    t0 = time.time()

    # Tối ưu CPU threads (nếu không có GPU)
    if not torch.cuda.is_available():
        torch.set_num_threads(torch.get_num_threads())
        device_info = f"CPU ({torch.get_num_threads()} threads)"
    else:
        device_info = f"GPU: {torch.cuda.get_device_name(0)}"

    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig").reset_index(drop=True)
    n = len(df)
    n_batches = (n + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Số chunk cần encode: {n:,} | Batch size: {BATCH_SIZE} | Số batch: {n_batches}")
    print(f"Device: {device_info}")
    if not torch.cuda.is_available():
        print(f"  (Không có GPU — ước tính {n_batches * 2 // 60 + 1}–10 phút trên CPU)")
    print()

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

    elapsed = time.time() - t0
    print(f"\nĐã tạo {embeddings.shape[0]:,} vector, dim={embeddings.shape[1]}")
    print(f"Lưu tại: {EMBEDDINGS_OUT} và {METADATA_OUT}")
    print(f"Tổng thời gian: {elapsed/60:.1f} phút")


if __name__ == "__main__":
    main()
