# Hệ thống hỏi đáp pháp luật lao động Việt Nam

Sinh viên: Trần Tấn Phúc — D22CNTT03 — GVHD: Nguyễn Trung Kiệt

## Timeline 8 tuần (theo yêu cầu của thầy)

| Tuần | Nội dung | File | Trạng thái |
|---|---|---|---|
| 1 | Khảo sát nghiên cứu, hệ thống RAG pháp luật, kiểm tra hiệu lực | — (tài liệu) | Đã tổng hợp |
| 2 | Khảo sát cấu trúc metadata / content / relationships | — (khảo sát) | Đã xác định: dataset `th1nhng0/vietnamese-legal-documents` |
| 3 | Lọc dữ liệu 3 nhóm nội dung (HĐLĐ, tiền lương, BHXH) | `src/1_filter.py` | Đã viết, đã tối ưu tốc độ, bổ sung logic ưu tiên |
| 4 | Làm sạch metadata, chuẩn hóa nhãn, liên kết văn bản-HTML | `src/2_clean.py` | Đã viết & test OK, sửa bug mất cột |
| 5 | Chunk hóa theo Chương/Điều/Khoản | `src/3_segment.py` | Đã viết & test OK, bổ sung regex loose + matched_group |
| 6 | Chọn mô hình embedding & tạo vector | `src/4_embed.py` | Đã viết (model: `bkai-foundation-models/vietnamese-bi-encoder`) |
| 7 | Xây FAISS index & tìm kiếm ngữ nghĩa | `src/5_index.py` | Đã viết |
| 8 | Baseline RAG — sinh câu trả lời kèm trích dẫn | `src/6_baseline_rag.py` | Đã viết (LLM: Gemini API, `gemini-2.5-flash`, có gói miễn phí) |
| 9 | Chuẩn hóa dữ liệu relationships, xác định loại và chiều quan hệ | `src/7_relationships.py` | Đã viết (5 nhóm: THAY_THE / SUA_DOI / BAI_BO / DAN_CHIEU / HUONG_DAN) |
| 10 | Xây đồ thị NetworkX + lưu trữ SQLite, chức năng truy vấn | `src/8_build_graph.py` | Đã viết |
| 11 | Mô-đun kiểm tra trạng thái hiệu lực và truy vết chuỗi quan hệ | `src/9_effect_checker.py` | Đã viết — EffectChecker class, check_effect_status(), check_chunks(), rerank |
| 12 | Tích hợp mô-đun kiểm tra hiệu lực vào pipeline RAG | `src/10_effect_aware_rag.py` | Đã viết — Effect-Aware RAG với cảnh báo hiệu lực trong context |
| 13 | Backend FastAPI và giao diện chatbot web | `src/web/` | Chưa viết |
| 14 | Xây dựng bộ câu hỏi kiểm thử | `data/eval/` | Chưa viết |
| 15 | Thực nghiệm + đánh giá so sánh | `src/11_evaluate.py` | Chưa viết |
| 16 | Hoàn thiện, báo cáo, demo | — | Chưa viết |

## Cách chạy toàn bộ pipeline

```bash
pip install -r requirements.txt

# Tuần 3 — lọc dữ liệu (đọc từ data/raw/metadata.parquet, content.parquet)
python src/1_filter.py

# Tuần 4 — làm sạch
python src/2_clean.py

# Tuần 5 — chunk hóa
python src/3_segment.py

# Tuần 6 — tạo embedding (lần đầu tự tải model ~500MB)
python src/4_embed.py

# Tuần 7 — lập chỉ mục FAISS + thử tìm kiếm
python src/5_index.py "Người lao động nghỉ việc trước thời hạn có được trợ cấp thôi việc không?"

# Tuần 8 — chạy Baseline RAG hoàn chỉnh (cần đặt GEMINI_API_KEY trước)
python src/6_baseline_rag.py "Người lao động nghỉ việc trước thời hạn có được trợ cấp thôi việc không?"

# Tuần 9 — chuẩn hóa relationships
python src/7_relationships.py

# Tuần 10 — xây đồ thị NetworkX + SQLite
python src/8_build_graph.py
python src/8_build_graph.py "<doc_id>"  # demo truy vết quan hệ
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