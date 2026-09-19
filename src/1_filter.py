"""
TUẦN 3 — LỌC DỮ LIỆU THEO PHẠM VI ĐỀ TÀI
----------------------------------------------------
Input:  data/raw/metadata.parquet, content.parquet
Output: data/raw/filtered_documents.csv

Mục tiêu: từ ~171.000 văn bản, lọc ra các văn bản thuộc 3 nhóm nội dung:
hợp đồng lao động, tiền lương/đãi ngộ, bảo hiểm xã hội — ưu tiên Bộ luật
Lao động và Luật Bảo hiểm xã hội (gốc + văn bản liên quan).

CHIẾN LƯỢC LỌC (3 tầng, ưu tiên từ cao xuống thấp):
  Tầng 1 — EXACT_TITLE: khớp tiêu đề chính xác với các bộ luật gốc quan trọng
            (Bộ luật Lao động 2012/2019, Luật BHXH 2006/2014/2024...).
            Đây là văn bản PHẢI CÓ trong dataset, không phụ thuộc MAX_DOCS.
  Tầng 2 — PRIORITY: tiêu đề hoặc linh_vuc khớp từ khóa lao động/BHXH
  Tầng 3 — KEYWORD: nội dung HTML thô khớp keyword 3 nhóm nội dung

SAU KHI LỌC: sắp xếp theo thứ tự ưu tiên trước khi cắt MAX_DOCS, đảm bảo
văn bản quan trọng (exact_title > bao_hiem_xa_hoi > hop_dong_lao_dong > ...)
luôn nằm trong top.

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

# Quota tối thiểu cho mỗi nhóm nội dung (đảm bảo phân bố đủ đều)
GROUP_QUOTA = {
    "exact_title":        999,   # không giới hạn — phải lấy hết
    "bao_hiem_xa_hoi":   150,
    "hop_dong_lao_dong": 200,
    "tien_luong":        350,
    "priority_doc":      100,
}

# Tầng 1: văn bản gốc quan trọng — loại văn bản là Bộ luật/Luật và tiêu đề liên quan lao động/BHXH
# Bảo đảm các văn bản gốc (Bộ luật LDD 2019, Luật BHXH...) luôn có mặt trong dataset
EXACT_LOAI_VAN_BAN = ["bộ luật", "luật"]  # giá trị thực tế trong cột loai_van_ban (có dấu)
EXACT_TITLE_KEYWORDS = [
    "lao động", "bảo hiểm xã hội", "việc làm", "bảo hiểm thất nghiệp",
    "an toàn.*vệ sinh lao động",
]

KEYWORDS = {
    "hop_dong_lao_dong": [
        "hợp đồng lao động", "chấm dứt hợp đồng", "thử việc",
        "sa thải", "kỷ luật lao động", "thời hạn báo trước",
        "trợ cấp thôi việc", "trợ cấp mất việc",
    ],
    "tien_luong": [
        "tiền lương", "lương tối thiểu", "phụ cấp", "thưởng",
        "trả lương", "làm thêm giờ", "tăng ca", "mức lương",
        "thang lương", "bảng lương",
    ],
    "bao_hiem_xa_hoi": [
        "bảo hiểm xã hội", "bảo hiểm y tế", "bảo hiểm thất nghiệp",
        "hưu trí", "thai sản", "ốm đau", "tai nạn lao động",
        "chế độ hưu", "quỹ bảo hiểm",
    ],
}

PRIORITY_TITLES = ["bộ luật lao động", "luật bảo hiểm xã hội", "luật việc làm",
                   "luật lao động", "luật an toàn"]
PRIORITY_LINH_VUC = ["lao động", "bảo hiểm xã hội", "tiền lương"]

# Thứ tự ưu tiên để sort trước khi head(MAX_DOCS)
PRIORITY_ORDER = {
    "exact_title": 0,
    "bao_hiem_xa_hoi": 1,
    "hop_dong_lao_dong": 2,
    "tien_luong": 3,
    "priority_doc": 4,
}


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
    linh_vuc_l = df.get("linh_vuc", pd.Series([""] * len(df), index=df.index)).fillna("").str.lower()
    content_l = df["content_html"].fillna("").str.lower()

    # Tầng 1: EXACT — văn bản loại Bộ luật/Luật có nội dung liên quan lao động/BHXH
    loai_l = df["loai_van_ban"].fillna("").str.lower()
    is_boluat_type = loai_l.isin([x.lower() for x in EXACT_LOAI_VAN_BAN])
    exact_kw_pattern = "|".join(EXACT_TITLE_KEYWORDS)
    is_exact_content = title_l.str.contains(exact_kw_pattern, regex=True)
    is_exact_title = is_boluat_type & is_exact_content

    print(f"Tim thay {is_exact_title.sum()} van ban la Bo luat/Luat goc lien quan de tai:")
    for title in df[is_exact_title]["title"].tolist():
        print(f"  - {title[:80]}")

    # Tầng 2: PRIORITY — tiêu đề hoặc linh_vuc có từ khóa lao động/BHXH
    is_priority = (
        title_l.str.contains("|".join(PRIORITY_TITLES), regex=True) |
        linh_vuc_l.str.contains("|".join(PRIORITY_LINH_VUC), regex=True)
    ) & ~is_exact_title

    # Tầng 3: KEYWORD — nội dung khớp keyword 3 nhóm
    matched_group = pd.Series([None] * len(df), index=df.index, dtype=object)
    for group, kw_list in KEYWORDS.items():
        pattern = "|".join(kw_list)
        hit = content_l.str.contains(pattern, regex=True) & matched_group.isna()
        matched_group[hit] = group

    # Gán nhãn tầng 1 & 2
    matched_group[is_exact_title] = "exact_title"
    matched_group[is_priority & matched_group.isna()] = "priority_doc"

    keep_mask = matched_group.notna()
    filtered = df[keep_mask].copy()
    filtered["matched_group"] = matched_group[keep_mask]
    print(f"Lọc từ khóa xong: {len(filtered):,} văn bản thỏa điều kiện ({time.time() - t2:.1f}s)")
    print("Phân bố trước khi cắt:")
    print(filtered["matched_group"].value_counts().to_string())

    # ---- SẮP XẾP ƯU TIÊN trước khi cắt MAX_DOCS ----
    # Đảm bảo exact_title luôn được giữ lại, tiếp theo là BHXH (ít nhất), rồi HĐLĐ, tiền lương
    filtered["_priority_order"] = filtered["matched_group"].map(PRIORITY_ORDER).fillna(99)
    filtered = filtered.sort_values("_priority_order").drop(columns=["_priority_order"])

    # Áp dụng quota cho từng nhóm để đảm bảo phân bố đủ đều
    parts = []
    remaining = MAX_DOCS
    for group in ["exact_title", "bao_hiem_xa_hoi", "hop_dong_lao_dong", "tien_luong", "priority_doc"]:
        quota = GROUP_QUOTA.get(group, 0)
        group_df = filtered[filtered["matched_group"] == group]
        take = min(len(group_df), quota, remaining)
        if take > 0:
            parts.append(group_df.head(take))
            remaining -= take
        if remaining <= 0:
            break

    # Nếu còn chỗ, lấy thêm từ nhóm lớn nhất (tien_luong)
    if remaining > 0:
        already_taken = set(pd.concat(parts).index) if parts else set()
        extra = filtered[~filtered.index.isin(already_taken)].head(remaining)
        if len(extra) > 0:
            parts.append(extra)

    out_filtered = pd.concat(parts).drop_duplicates()
    print(f"\nSau khi áp dụng quota ({MAX_DOCS} văn bản):")
    print(out_filtered["matched_group"].value_counts().to_string())

    # ---- PARSE HTML ĐẦY ĐỦ — chỉ cho các văn bản đã lọc ----
    t3 = time.time()
    print(f"\nĐang parse HTML -> text cho {len(out_filtered)} văn bản đã lọc...")
    out_filtered = out_filtered.copy()
    out_filtered["content"] = out_filtered["content_html"].apply(html_to_text)
    print(f"  -> Parse xong ({time.time() - t3:.1f}s)")

    out = out_filtered.rename(columns={
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
    print("\nPhân bố matched_group:")
    print(out["matched_group"].value_counts().to_string())
    print("\nPhân bố effect_status_source:")
    print(out["effect_status_source"].value_counts().to_string())

    # Kiểm tra bộ luật gốc có mặt không
    exact = out[out["matched_group"] == "exact_title"]
    print(f"\nVăn bản exact_title ({len(exact)} văn bản):")
    for _, row in exact.iterrows():
        print(f"  [{row['effect_status_source']}] {row['title'][:80]}")

    print(f"\nKết quả lưu tại: {OUTPUT_PATH}")
    print(f"Tổng thời gian chạy: {time.time() - t0:.1f}s")


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