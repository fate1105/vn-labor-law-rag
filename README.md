# Hệ thống hỏi đáp pháp luật lao động Việt Nam

Sinh viên: Trần Tấn Phúc — D22CNTT03 — GVHD: Nguyễn Trung Kiệt

## Timeline 8 tuần (theo yêu cầu của thầy)

| Tuần | Nội dung | File | Trạng thái |
|---|---|---|---|
| 1 | Khảo sát nghiên cứu, hệ thống RAG pháp luật, kiểm tra hiệu lực | — (tài liệu) | Cần tự tổng hợp |
| 2 | Khảo sát cấu trúc metadata / content / relationships | — (khảo sát) | Đã xác định: dataset `th1nhng0/vietnamese-legal-documents` |
| 3 | Lọc dữ liệu 3 nhóm nội dung (HĐLĐ, tiền lương, BHXH) | `src/filter.py` | Đã viết, đã tối ưu tốc độ |
| 4 | Làm sạch metadata, chuẩn hóa nhãn, liên kết văn bản-HTML | `src/clean.py` | Đã viết & test OK |
| 5 | Chunk hóa theo Chương/Điều/Khoản | `src/segment.py` | Đã viết & test OK |
| 6 | Chọn mô hình embedding & tạo vector | `src/embed.py` | Đã viết (model: `bkai-foundation-models/vietnamese-bi-encoder`) |
| 7 | Xây FAISS index & tìm kiếm ngữ nghĩa | `src/index.py` | Đã viết |
| 8 | Baseline RAG — sinh câu trả lời kèm trích dẫn | `src/baseline_rag.py` | Đã viết (LLM: Gemini API, `gemini-2.5-flash`, có gói miễn phí) |

## Cách chạy toàn bộ pipeline

```bash
pip install -r requirements.txt

# Tuần 3 — lọc dữ liệu (đọc từ data/raw/metadata.parquet, content.parquet)
python src/filter.py

# Tuần 4 — làm sạch
python src/clean.py

# Tuần 5 — chunk hóa
python src/segment.py

# Tuần 6 — tạo embedding (lần đầu tự tải model ~500MB)
python src/embed.py

# Tuần 7 — lập chỉ mục FAISS + thử tìm kiếm
python src/index.py "Người lao động nghỉ việc trước thời hạn có được trợ cấp thôi việc không?"

# Tuần 8 — chạy Baseline RAG hoàn chỉnh (cần đặt GEMINI_API_KEY trước)
python src/baseline_rag.py "Người lao động nghỉ việc trước thời hạn có được trợ cấp thôi việc không?"
```

**Trước khi chạy Tuần 8**, cần lấy API key miễn phí tại https://aistudio.google.com/apikey
(đăng nhập bằng tài khoản Google, không cần thẻ tín dụng cho gói free), rồi đặt biến môi trường:
```bash
export GEMINI_API_KEY="your-api-key"      # Mac/Linux
setx GEMINI_API_KEY "your-api-key"        # Windows (mở lại terminal sau khi setx)
```

## Dataset đã xác định

**`th1nhng0/vietnamese-legal-documents`** — nguồn vbpl.vn (Cổng thông tin điện tử Bộ Tư pháp).
Có sẵn cột `tinh_trang_hieu_luc` (trạng thái hiệu lực) và bảng `relationships`
(quan hệ sửa đổi/thay thế/dẫn chiếu) — dữ liệu gốc cho phần Effect-Aware RAG
ở giai đoạn sau.

## Sau Tuần 8 (chưa nằm trong timeline hiện tại, thuộc đề cương giai đoạn sau)

- Fine-tune embedding trên tập cặp (câu hỏi, chunk liên quan).
- Xây đồ thị quan hệ văn bản bằng NetworkX (dựa trên `relationships.parquet`).
- Xây mô-đun kiểm tra hiệu lực (đối chiếu `tinh_trang_hieu_luc` gốc).
- Xây Effect-Aware RAG hoàn chỉnh & so sánh với Baseline RAG.