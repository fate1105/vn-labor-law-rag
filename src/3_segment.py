"""
TUẦN 5 — CHUNK HÓA THEO ĐIỀU / KHOẢN / ĐIỂM
----------------------------------------------------
Input:  data/processed/cleaned_documents.csv   (từ clean.py)
Output: data/processed/segmented_chunks.csv

Kết quả dự kiến: tạo được tập chunk văn bản pháp luật kèm metadata và
thông tin nguồn (doc_id, tiêu đề, Chương/Điều/Khoản, ngày ban hành,
trạng thái hiệu lực).

Mỗi chunk gồm:
- doc_id, doc_title       : văn bản gốc
- chuong                  : số/tên Chương (nếu có)
- dieu_so, dieu_tieu_de   : số & tiêu đề Điều
- khoan_so                : số Khoản (nếu tách được ở cấp Khoản)
- text                    : nội dung chunk — dùng để tạo embedding ở tuần 6
- effect_status_source    : trạng thái hiệu lực gốc từ vbpl.vn (đi kèm mọi chunk
                            của văn bản đó, dùng cho tuần 8 khi cần cảnh báo)
"""

import re
import pandas as pd

INPUT_PATH = "data/processed/cleaned_documents.csv"
OUTPUT_PATH = "data/processed/segmented_chunks.csv"

CHUONG_RE = re.compile(r"(?m)^Chương\s+([IVXLCDM\d]+)\.?\s*(.*)$")
DIEU_RE = re.compile(r"(?m)^Điều\s+(\d+)\.?\s*(.*)$")
KHOAN_RE = re.compile(r"(?m)^(\d+)\.\s+(.*)")


def split_by_dieu(content: str):
    matches = list(DIEU_RE.finditer(content))
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

    all_chunks = []
    for _, row in df.iterrows():
        chunks = split_by_dieu(row["content"])
        if not chunks:
            chunks = [{
                "chuong": None, "dieu_so": None, "dieu_tieu_de": None,
                "khoan_so": None, "text": row["content"],
            }]
        for c in chunks:
            c["doc_id"] = row["doc_id"]
            c["doc_title"] = row["title"]
            c["issue_date"] = row.get("issue_date")
            c["effect_status_source"] = row.get("effect_status_source")
        all_chunks.extend(chunks)

    out_df = pd.DataFrame(all_chunks)
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Số văn bản đầu vào: {len(df)}")
    print(f"Số chunk (Điều/Khoản) tạo ra: {len(out_df)}")
    print(f"Kết quả lưu tại: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
