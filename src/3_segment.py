"""
TUẦN 5 — CHUNK HÓA THEO ĐIỀU / KHOẢN / ĐIỂM
----------------------------------------------------
Input:  data/processed/cleaned_documents.csv   (từ 2_clean.py)
Output: data/processed/segmented_chunks.csv

Kết quả dự kiến: tạo được tập chunk văn bản pháp luật kèm metadata và
thông tin nguồn (doc_id, tiêu đề, Chương/Điều/Khoản, ngày ban hành,
trạng thái hiệu lực, nhóm nội dung).

Mỗi chunk gồm:
- doc_id, doc_title       : văn bản gốc
- matched_group           : nhóm nội dung (hop_dong_lao_dong / tien_luong /
                            bao_hiem_xa_hoi / exact_title / priority_doc)
- chuong                  : số/tên Chương (nếu có)
- dieu_so, dieu_tieu_de   : số & tiêu đề Điều
- khoan_so                : số Khoản (nếu tách được ở cấp Khoản)
- text                    : nội dung chunk — dùng để tạo embedding ở tuần 6
- effect_status_source    : trạng thái hiệu lực gốc từ vbpl.vn (đi kèm mọi chunk
                            của văn bản đó, dùng cho Effect-Aware RAG)

CHIẾN LƯỢC PARSE "Điều":
  1. Thử regex chuẩn: "Điều" ở đầu dòng (^Điều\\s+N)
  2. Nếu không tìm thấy: thử regex mềm hơn — "Điều" không cần đầu dòng
     (dùng cho văn bản HTML parse ra bị mất newline)
  3. Nếu vẫn không tìm thấy: giữ toàn văn bản làm 1 chunk fallback
"""

import re
import pandas as pd

INPUT_PATH = "data/processed/cleaned_documents.csv"
OUTPUT_PATH = "data/processed/segmented_chunks.csv"

# Regex chuẩn: "Điều" ở đầu dòng
CHUONG_RE = re.compile(r"(?m)^Chương\s+([IVXLCDM\d]+)\.?\s*(.*)$")
DIEU_RE_STRICT = re.compile(r"(?m)^Điều\s+(\d+)\.?\s*(.*)$")
# Regex mềm: "Điều" không cần đầu dòng (fallback cho văn bản bị mất newline)
DIEU_RE_LOOSE = re.compile(r"Điều\s+(\d+)[.:\s]\s*([^\n]*)")
KHOAN_RE = re.compile(r"(?m)^\s*(\d+)\.\s+(.{20,})")


def split_by_dieu(content: str):
    """Tách văn bản thành chunks theo Điều/Khoản.

    Thử regex strict trước; nếu không tìm được Điều, thử regex loose;
    nếu vẫn không thấy, trả về list rỗng (caller sẽ tạo fallback chunk).
    """
    # Thử strict trước
    matches = list(DIEU_RE_STRICT.finditer(content))

    # Nếu không có Điều ở đầu dòng, thử loose (văn bản HTML parse bị mất newline)
    if not matches:
        matches = list(DIEU_RE_LOOSE.finditer(content))
        # Loại trùng lặp: chỉ giữ lại nếu khoảng cách giữa 2 Điều đủ lớn
        if matches:
            deduped = [matches[0]]
            for m in matches[1:]:
                if m.start() - deduped[-1].start() > 50:
                    deduped.append(m)
            matches = deduped

    if not matches:
        return []

    chunks = []
    for i, m in enumerate(matches):
        dieu_so = m.group(1)
        dieu_tieu_de = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        dieu_text = content[start:end].strip()

        chuong_matches = [c for c in CHUONG_RE.finditer(content) if c.start() < m.start()]
        chuong = chuong_matches[-1].group(0).strip() if chuong_matches else None

        chunks.append({
            "chuong": chuong, "dieu_so": dieu_so, "dieu_tieu_de": dieu_tieu_de,
            "khoan_so": None, "text": f"Điều {dieu_so}. {dieu_tieu_de}\n{dieu_text}",
        })

        for km in KHOAN_RE.finditer(dieu_text):
            khoan_so, khoan_text = km.group(1), km.group(2).strip()
            if len(khoan_text) > 20:
                chunks.append({
                    "chuong": chuong, "dieu_so": dieu_so, "dieu_tieu_de": dieu_tieu_de,
                    "khoan_so": khoan_so,
                    "text": f"Điều {dieu_so} Khoản {khoan_so}: {khoan_text}",
                })
    return chunks


def main():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    print(f"Số văn bản đầu vào: {len(df)}")

    all_chunks = []
    n_fallback = 0
    n_loose = 0
    for _, row in df.iterrows():
        content = row["content"]
        chunks = split_by_dieu(content)

        # Đếm fallback và loose để báo cáo chất lượng
        if not chunks:
            n_fallback += 1
            chunks = [{
                "chuong": None, "dieu_so": None, "dieu_tieu_de": None,
                "khoan_so": None, "text": content,
            }]
        elif not list(DIEU_RE_STRICT.finditer(content)) and list(DIEU_RE_LOOSE.finditer(content)):
            n_loose += 1

        for c in chunks:
            c["doc_id"] = row["doc_id"]
            c["doc_title"] = row["title"]
            c["issue_date"] = row.get("issue_date")
            c["effect_status_source"] = row.get("effect_status_source")
            c["matched_group"] = row.get("matched_group")   # ← thêm mới: cần cho đánh giá

        all_chunks.extend(chunks)

    out_df = pd.DataFrame(all_chunks)
    # Sắp xếp cột để dễ đọc
    col_order = [
        "doc_id", "doc_title", "matched_group",
        "chuong", "dieu_so", "dieu_tieu_de", "khoan_so",
        "text", "issue_date", "effect_status_source",
    ]
    out_df = out_df[[c for c in col_order if c in out_df.columns]]
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Số chunk (Điều/Khoản) tạo ra: {len(out_df):,}")
    print(f"  - Parse strict (^Điều đầu dòng): {len(df) - n_fallback - n_loose} văn bản")
    print(f"  - Parse loose  (Điều giữa văn bản): {n_loose} văn bản")
    print(f"  - Fallback (toàn văn): {n_fallback} văn bản")
    print()
    print("Phân bố matched_group trong chunks:")
    print(out_df["matched_group"].value_counts().to_string())
    print()
    print("Phân bố effect_status_source trong chunks:")
    print(out_df["effect_status_source"].value_counts().to_string())
    print(f"\nKết quả lưu tại: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
