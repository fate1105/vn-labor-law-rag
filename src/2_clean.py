"""
BƯỚC 1.2 — LÀM SẠCH & CHUẨN HÓA DỮ LIỆU
----------------------------------------------------
Input:  data/raw/filtered_documents.csv   (từ bước 01)
Output: data/processed/cleaned_documents.csv

Các việc thực hiện:
- Loại bỏ HTML tag, ký tự thừa, khoảng trắng lặp.
- Chuẩn hóa Unicode tiếng Việt (tránh lỗi dấu bị tách rời).
- Loại bỏ văn bản trùng lặp hoặc rỗng.
- Chuẩn hóa cột ngày ban hành về định dạng thống nhất (YYYY-MM-DD).
"""

import re
import unicodedata
import pandas as pd

INPUT_PATH = "data/raw/filtered_documents.csv"
OUTPUT_PATH = "data/processed/cleaned_documents.csv"

HTML_TAG_RE = re.compile(r"<[^>]+>")
MULTI_SPACE_RE = re.compile(r"[ \t]+")
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def normalize_unicode(text: str) -> str:
    """Chuẩn hóa Unicode về dạng NFC — tránh lỗi dấu tiếng Việt bị tách rời
    (ví dụ 'ệ' bị lưu thành 2 ký tự thay vì 1)."""
    return unicodedata.normalize("NFC", text)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = normalize_unicode(text)
    text = HTML_TAG_RE.sub(" ", text)
    text = MULTI_SPACE_RE.sub(" ", text)
    text = MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def parse_date(value):
    """Chuẩn hóa ngày ban hành về YYYY-MM-DD, trả về None nếu không parse được."""
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value, errors="coerce").strftime("%Y-%m-%d")
    except Exception:
        return None


def main():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    n_before = len(df)

    df["title"] = df["title"].apply(clean_text)
    df["content"] = df["content"].apply(clean_text)
    df["issue_date"] = df["issue_date"].apply(parse_date)

    # Loại bỏ văn bản rỗng hoặc quá ngắn (nhiều khả năng là lỗi crawl)
    df = df[df["content"].str.len() > 50]

    # Loại bỏ trùng lặp theo nội dung
    df = df.drop_duplicates(subset=["content"])

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Trước làm sạch: {n_before} văn bản")
    print(f"Sau làm sạch:   {len(df)} văn bản")
    print(f"Kết quả lưu tại: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()