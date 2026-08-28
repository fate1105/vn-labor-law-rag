"""
BƯỚC 1.1 — LỌC DỮ LIỆU THEO PHẠM VI ĐỀ TÀI
----------------------------------------------------
Input:  data/raw/metadata.parquet, content.parquet
Output: data/raw/filtered_documents.csv

Mục tiêu: từ ~153.420 văn bản, lọc ra các văn bản thuộc 3 nhóm nội dung:
hợp đồng lao động, tiền lương/đãi ngộ, bảo hiểm xã hội — ưu tiên Bộ luật
Lao động và Luật Bảo hiểm xã hội.

TỐI ƯU TỐC ĐỘ: bước lọc theo từ khóa chạy trên HTML thô bằng thao tác
vector hóa của pandas (str.contains), KHÔNG parse HTML bằng BeautifulSoup
cho toàn bộ 150k+ văn bản. Việc parse HTML tốn thời gian (BeautifulSoup)
chỉ thực hiện cho khoảng 800 văn bản ĐÃ được lọc — nhanh hơn rất nhiều
so với parse rồi mới lọc.

Thời gian ước tính (máy thường, SSD, 8-16GB RAM):
- Đọc content.parquet (~3.6GB): 1-3 phút
- Lọc theo từ khóa (vector hóa, chưa parse HTML): dưới 1 phút
- Parse HTML cho ~800 văn bản đã lọc: vài giây - 1 phút
- Tổng: khoảng 3-6 phút

Lưu ý RAM: content.parquet nặng ~3.6GB, khi load vào pandas có thể chiếm
6-10GB RAM. Nếu máy bạn dưới 8GB RAM, cân nhắc đọc theo batch (xem ghi
chú BATCHED MODE ở cuối file).
"""

import time
import pandas as pd
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
OUTPUT_PATH = "data/raw/filtered_documents.csv"
MAX_DOCS = 800  # theo phạm vi đề cương (300-800 văn bản)

KEYWORDS = {
    "hop_dong_lao_dong": [
        "hợp đồng lao động", "chấm dứt hợp đồng", "thử việc",
        "sa thải", "kỷ luật lao động", "thời hạn báo trước",
    ],
    "tien_luong": [
        "tiền lương", "lương tối thiểu", "phụ cấp", "thưởng",
        "trả lương", "làm thêm giờ", "tăng ca",
    ],
    "bao_hiem_xa_hoi": [
        "bảo hiểm xã hội", "bảo hiểm y tế", "bảo hiểm thất nghiệp",
        "hưu trí", "thai sản", "ốm đau", "tai nạn lao động",
    ],
}

PRIORITY_TITLES = ["bộ luật lao động", "luật bảo hiểm xã hội"]
PRIORITY_LINH_VUC = ["lao động", "bảo hiểm xã hội", "tiền lương"]


def html_to_text(html: str) -> str:
    if not isinstance(html, str) or not html.strip():
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n")


def main():
    t0 = time.time()
    print("Đang đọc metadata.parquet...")
    meta = pd.read_parquet(f"{RAW_DIR}/metadata.parquet")

    print("Đang đọc content.parquet (file lớn, có thể mất 1-3 phút)...")
    content = pd.read_parquet(f"{RAW_DIR}/content.parquet")
    print(f"  -> Đọc xong sau {time.time() - t0:.1f}s")
    print(f"Metadata: {len(meta):,} văn bản | Content: {len(content):,} văn bản")

    t1 = time.time()
    df = meta.merge(content, on="id", how="inner")
    print(f"Sau khi ghép: {len(df):,} văn bản ({time.time() - t1:.1f}s)")

    # ---- LỌC VECTOR HÓA (nhanh) — chạy trên HTML thô, chưa parse ----
    t2 = time.time()
    title_l = df["title"].fillna("").str.lower()
    linh_vuc_l = df.get("linh_vuc", pd.Series([""] * len(df))).fillna("").str.lower()
    content_l = df["content_html"].fillna("").str.lower()

    is_priority = (
        title_l.str.contains("|".join(PRIORITY_TITLES), regex=True) |
        linh_vuc_l.str.contains("|".join(PRIORITY_LINH_VUC), regex=True)
    )

    matched_group = pd.Series([None] * len(df), index=df.index, dtype=object)
    for group, kw_list in KEYWORDS.items():
        pattern = "|".join(kw_list)
        hit = content_l.str.contains(pattern, regex=True) & matched_group.isna()
        matched_group[hit] = group

    keep_mask = is_priority | matched_group.notna()
    filtered = df[keep_mask].copy()
    filtered["matched_group"] = matched_group[keep_mask].fillna("priority_doc")
    filtered = filtered.head(MAX_DOCS)
    print(f"Lọc từ khóa xong: giữ {len(filtered)} văn bản ({time.time() - t2:.1f}s)")

    # ---- PARSE HTML ĐẦY ĐỦ — chỉ cho các văn bản đã lọc ----
    t3 = time.time()
    print("Đang parse HTML -> text cho các văn bản đã lọc...")
    filtered["content"] = filtered["content_html"].apply(html_to_text)
    print(f"  -> Parse xong ({time.time() - t3:.1f}s)")

    out = filtered.rename(columns={
        "id": "doc_id",
        "ngay_ban_hanh": "issue_date",
        "ngay_co_hieu_luc": "effect_date",
        "ngay_het_hieu_luc": "expiry_date",
        "tinh_trang_hieu_luc": "effect_status_source",
    })
    cols = ["doc_id", "title", "content", "issue_date", "effect_date",
            "expiry_date", "effect_status_source", "matched_group"]
    if "linh_vuc" in out.columns:
        cols.insert(-1, "linh_vuc")
    out = out[[c for c in cols if c in out.columns]]

    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\nGiữ lại {len(out)} văn bản phù hợp phạm vi đề tài.")
    print(out["matched_group"].value_counts())
    print(f"Kết quả lưu tại: {OUTPUT_PATH}")
    print(f"\nTổng thời gian chạy: {time.time() - t0:.1f}s")


# ---- BATCHED MODE (dùng nếu máy dưới 8GB RAM, content.parquet gây tràn RAM) ----
# Thay vì pd.read_parquet(...) đọc toàn bộ 1 lần, dùng pyarrow.parquet đọc theo
# row-group để xử lý từng phần, ví dụ:
#
#   import pyarrow.parquet as pq
#   pf = pq.ParquetFile(f"{RAW_DIR}/content.parquet")
#   for batch in pf.iter_batches(batch_size=20000):
#       chunk_df = batch.to_pandas()
#       # ... lọc keyword trên chunk_df, gom kết quả lại ...
#
# Nếu chạy 01 mà máy bạn bị đơ/hết RAM, báo lại để mình viết bản batched này.


if __name__ == "__main__":
    main()