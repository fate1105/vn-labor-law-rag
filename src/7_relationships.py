"""
TUẦN 9 — CHUẨN HÓA DỮ LIỆU RELATIONSHIPS
----------------------------------------------------
Input:  data/raw/relationships.parquet          (1,033,255 quan hệ giữa văn bản)
        data/raw/filtered_documents.csv         (800 văn bản trong phạm vi đề tài)
Output: data/processed/relationships_clean.csv  (quan hệ đã chuẩn hóa, chỉ giữ
                                                 quan hệ liên quan văn bản đề tài)

Các việc thực hiện:
1. Đọc relationships.parquet — 3 cột: doc_id, other_doc_id, relationship
2. Chuẩn hóa loại quan hệ thành 5 nhóm tiêu chuẩn:
     THAY_THE      — văn bản thay thế/hợp nhất văn bản khác
     SUA_DOI       — sửa đổi, bổ sung, đính chính
     BAI_BO        — bãi bỏ, đình chỉ, tạm ngưng hiệu lực
     DAN_CHIEU     — dẫn chiếu, căn cứ, giải thích
     HUONG_DAN     — hướng dẫn thi hành, quy định chi tiết
3. Xác định chiều quan hệ (direction):
     OUTGOING  — doc_id TÁC ĐỘNG LÊN other_doc_id
                 (doc_id thay thế / sửa đổi / bãi bỏ other_doc_id)
     INCOMING  — other_doc_id TÁC ĐỘNG LÊN doc_id
                 (other_doc_id là văn bản bị doc_id tác động)
4. Lọc: chỉ giữ quan hệ có ít nhất 1 đầu là văn bản trong filtered_documents.csv
   → Thu gọn từ 1M+ quan hệ xuống còn liên quan đề tài
5. Loại bỏ quan hệ trùng lặp

Kết quả dự kiến: tập quan hệ sửa đổi/thay thế/bãi bỏ/dẫn chiếu đã chuẩn hóa,
sẵn sàng để xây đồ thị NetworkX (Tuần 10).

Ghi chú về 5 nhóm:
- THAY_THE và BAI_BO là quan hệ "chết người" — ảnh hưởng trực tiếp hiệu lực
- SUA_DOI ảnh hưởng một phần — cần cảnh báo "hết hiệu lực một phần"
- DAN_CHIEU và HUONG_DAN cần để truy vết chuỗi liên quan
"""

import pandas as pd

RAW_REL_PATH = "data/raw/relationships.parquet"
FILTERED_DOCS_PATH = "data/raw/filtered_documents.csv"
OUTPUT_PATH = "data/processed/relationships_clean.csv"

# ---- MAPPING CHUẨN HÓA LOẠI QUAN HỆ ----
# Ánh xạ từ giá trị gốc trong dataset → nhóm chuẩn hóa
# Chiều OUTGOING: doc_id là văn bản CHỦ ĐỘNG tác động
# Chiều INCOMING: doc_id là văn bản BỊ ĐỘNG (bị tác động)
REL_MAP = {
    # === THAY_THE ===
    "Thay thế":                              ("THAY_THE",   "OUTGOING"),
    "Hợp nhất":                              ("THAY_THE",   "OUTGOING"),

    # === SUA_DOI ===
    "Sửa đổi, bổ sung":                     ("SUA_DOI",    "OUTGOING"),
    "Đính chính":                            ("SUA_DOI",    "OUTGOING"),
    "Văn bản được sửa đổi":                 ("SUA_DOI",    "INCOMING"),  # doc_id bị sửa đổi
    "Văn bản sửa đổi":                      ("SUA_DOI",    "OUTGOING"),  # doc_id đi sửa đổi
    "Văn bản được bổ sung":                 ("SUA_DOI",    "INCOMING"),  # doc_id bị bổ sung
    "Văn bản bổ sung":                      ("SUA_DOI",    "OUTGOING"),  # doc_id đi bổ sung

    # === BAI_BO (bãi bỏ / đình chỉ / hết hiệu lực) ===
    "Bãi bỏ":                               ("BAI_BO",     "OUTGOING"),
    "Văn bản quy định hết hiệu lực":        ("BAI_BO",     "OUTGOING"),
    "Văn bản hết hiệu lực":                 ("BAI_BO",     "INCOMING"),  # doc_id bị hết hiệu lực
    "Văn bản quy định hết hiệu lực 1 phần": ("BAI_BO",     "OUTGOING"),
    "Văn bản bị hết hiệu lực 1 phần":      ("BAI_BO",     "INCOMING"),
    "Đình chỉ thi hành":                    ("BAI_BO",     "OUTGOING"),
    "Tạm ngưng hiệu lực":                   ("BAI_BO",     "OUTGOING"),
    "Văn bản đình chỉ":                     ("BAI_BO",     "OUTGOING"),
    "Văn bản đình chỉ 1 phần":             ("BAI_BO",     "OUTGOING"),
    "Văn bản bị đình chỉ":                 ("BAI_BO",     "INCOMING"),
    "Văn bản bị đình chỉ 1 phần":          ("BAI_BO",     "INCOMING"),

    # === DAN_CHIEU ===
    "Dẫn chiếu":                            ("DAN_CHIEU",  "OUTGOING"),
    "Căn cứ":                               ("DAN_CHIEU",  "OUTGOING"),
    "Văn bản dẫn chiếu":                    ("DAN_CHIEU",  "OUTGOING"),
    "Văn bản căn cứ":                       ("DAN_CHIEU",  "INCOMING"),
    "Hướng dẫn áp dụng":                    ("DAN_CHIEU",  "OUTGOING"),
    "Giải thích":                           ("DAN_CHIEU",  "OUTGOING"),
    "Công bố":                              ("DAN_CHIEU",  "OUTGOING"),
    "Bản dịch":                             ("DAN_CHIEU",  "INCOMING"),
    "Văn bản liên quan khác":               ("DAN_CHIEU",  "OUTGOING"),

    # === HUONG_DAN ===
    "Quy định chi tiết, hướng dẫn thi hành": ("HUONG_DAN", "OUTGOING"),
    "Văn bản HD, QĐ chi tiết":             ("HUONG_DAN",  "OUTGOING"),
    "Văn bản được HD, QĐ chi tiết":        ("HUONG_DAN",  "INCOMING"),
}

# Trọng số ưu tiên cho Effect-Aware RAG (số càng cao = quan hệ càng quan trọng)
REL_IMPORTANCE = {
    "THAY_THE":  5,
    "BAI_BO":    4,
    "SUA_DOI":   3,
    "HUONG_DAN": 2,
    "DAN_CHIEU": 1,
}


def main():
    print("Đang đọc relationships.parquet...")
    rel = pd.read_parquet(RAW_REL_PATH)
    print(f"Tổng quan hệ gốc: {len(rel):,}")
    print(f"Loại quan hệ gốc: {rel['relationship'].nunique()} loại")

    print("\nĐang đọc filtered_documents.csv...")
    docs = pd.read_csv(FILTERED_DOCS_PATH, encoding="utf-8-sig")
    doc_ids = set(docs["doc_id"].astype(str))
    print(f"Văn bản trong phạm vi đề tài: {len(doc_ids)}")

    # ---- CHUẨN HÓA LOẠI QUAN HỆ ----
    print("\nĐang chuẩn hóa loại quan hệ...")
    rel["doc_id"] = rel["doc_id"].astype(str)
    rel["other_doc_id"] = rel["other_doc_id"].astype(str)

    rel["rel_type"] = rel["relationship"].map(
        lambda x: REL_MAP.get(x, (None, None))[0]
    )
    rel["direction"] = rel["relationship"].map(
        lambda x: REL_MAP.get(x, (None, None))[1]
    )

    # Báo cáo quan hệ không được map (nếu có loại mới trong dataset)
    unknown = rel[rel["rel_type"].isna()]["relationship"].value_counts()
    if len(unknown) > 0:
        print(f"  [!] {len(unknown)} loại quan hệ chưa được map (sẽ bị loại bỏ):")
        for rel_name, cnt in unknown.items():
            print(f"      - {rel_name}: {cnt:,}")

    # Loại bỏ quan hệ không nhận diện được
    rel = rel[rel["rel_type"].notna()].copy()

    # ---- LỌC QUAN HỆ LIÊN QUAN ĐỀ TÀI ----
    print("\nĐang lọc quan hệ liên quan đến văn bản trong phạm vi đề tài...")
    mask_in_scope = (
        rel["doc_id"].isin(doc_ids) |
        rel["other_doc_id"].isin(doc_ids)
    )
    rel_filtered = rel[mask_in_scope].copy()
    print(f"Quan hệ sau lọc: {len(rel_filtered):,} (từ {len(rel):,})")

    # Thêm cờ: cả 2 đầu có trong dataset hay chỉ 1 đầu
    rel_filtered["both_in_scope"] = (
        rel_filtered["doc_id"].isin(doc_ids) &
        rel_filtered["other_doc_id"].isin(doc_ids)
    )

    # Thêm trọng số quan trọng
    rel_filtered["importance"] = rel_filtered["rel_type"].map(REL_IMPORTANCE)

    # ---- LOẠI BỎ TRÙNG LẶP ----
    before_dedup = len(rel_filtered)
    rel_filtered = rel_filtered.drop_duplicates(
        subset=["doc_id", "other_doc_id", "rel_type"]
    )
    print(f"Sau dedup: {len(rel_filtered):,} (loại {before_dedup - len(rel_filtered):,} trùng)")

    # ---- SẮP XẾP CỘT OUTPUT ----
    output_cols = [
        "doc_id", "other_doc_id",
        "rel_type", "direction", "importance",
        "both_in_scope", "relationship",   # relationship gốc giữ lại để tham chiếu
    ]
    rel_out = rel_filtered[output_cols].sort_values(
        ["importance", "doc_id"], ascending=[False, True]
    )

    rel_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    # ---- BÁO CÁO KẾT QUẢ ----
    print(f"\n{'='*55}")
    print("KẾT QUẢ CHUẨN HÓA RELATIONSHIPS")
    print(f"{'='*55}")
    print(f"\nPhân bố theo rel_type:")
    type_counts = rel_out["rel_type"].value_counts()
    for t, cnt in type_counts.items():
        imp = REL_IMPORTANCE[t]
        both = rel_out[(rel_out["rel_type"] == t) & rel_out["both_in_scope"]].shape[0]
        print(f"  {t:<12} {cnt:>6,} quan hệ  (importance={imp}, "
              f"cả 2 trong phạm vi={both:,})")

    print(f"\nPhân bố theo direction:")
    print(rel_out["direction"].value_counts().to_string())

    print(f"\nQuan hệ có cả 2 đầu trong phạm vi đề tài: "
          f"{rel_out['both_in_scope'].sum():,}")
    print(f"Quan hệ chỉ 1 đầu trong phạm vi: "
          f"{(~rel_out['both_in_scope']).sum():,}")

    print(f"\nQuan hệ quan trọng nhất (THAY_THE + BAI_BO + SUA_DOI):")
    critical = rel_out[rel_out["rel_type"].isin(["THAY_THE", "BAI_BO", "SUA_DOI"])]
    print(f"  Tổng: {len(critical):,}")
    print(f"  Cả 2 trong phạm vi: {critical['both_in_scope'].sum():,}")

    print(f"\nKết quả lưu tại: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
