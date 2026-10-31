# Hệ thống hỏi đáp pháp luật lao động Việt Nam (Effect-Aware RAG)

Sinh viên: **Trần Tấn Phúc** — MSSV: D22CNTT03  
GVHD: **TS. Nguyễn Trung Kiệt** — Học viện Công nghệ Bưu chính Viễn thông

---

## 📌 Tổng quan tiến độ đề tài

| Giai đoạn | Nội dung | Module / File | Trạng thái |
|---|---|---|---|
| **Tuần 1–2** | Khảo sát nghiên cứu & cấu trúc dataset vbpl.vn | `data/raw/` | ✅ Hoàn thành |
| **Tuần 3** | Lọc dữ liệu 3 nhóm (HĐLĐ, tiền lương, BHXH) | `src/1_filter.py` | ✅ 800 văn bản |
| **Tuần 4** | Làm sạch metadata, liên kết HTML | `src/2_clean.py` | ✅ 799 văn bản sạch |
| **Tuần 5** | Chunk hóa theo Điều / Khoản | `src/3_segment.py` | ✅ 42,592 chunks |
| **Tuần 6** | Tạo embedding (`vietnamese-bi-encoder`) | `src/4_embed.py` | ✅ 42,592 vectors (768d) |
| **Tuần 7** | Xây FAISS Index tìm kiếm ngữ nghĩa | `src/5_index.py` | ✅ Cosine similarity |
| **Tuần 8** | Baseline RAG (RAG thông thường) | `src/6_baseline_rag.py` | ✅ Gemini API |
| **Tuần 9** | Chuẩn hóa 5 nhóm quan hệ pháp luật | `src/7_relationships.py` | ✅ 43,478 quan hệ |
| **Tuần 10** | Xây đồ thị NetworkX DiGraph + SQLite DB | `src/8_build_graph.py` | ✅ 36,726 nodes |
| **Tuần 11** | Mô-đun kiểm tra hiệu lực & truy vết | `src/9_effect_checker.py` | ✅ OK/WARN/DANGER/UNKNOWN |
| **Tuần 12** | Tích hợp Effect-Aware RAG hoàn chỉnh | `src/10_effect_aware_rag.py` | ✅ Rerank + Cảnh báo |
| **Tuần 13** | Web Chatbot UI (Streamlit) & FastAPI Backend | `src/web/` | ✅ Hoàn thành |
| **Tuần 14** | Xây dựng bộ câu hỏi kiểm thử | `data/eval/` | ⏳ Tiếp theo |
| **Tuần 15** | Thực nghiệm & đánh giá định lượng so sánh | `src/11_evaluate.py` | ⏳ Tiếp theo |
| **Tuần 16** | Hoàn thiện báo cáo ĐATN & slide demo | — | ⏳ Tiếp theo |

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc của project (hoặc lấy API key miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey)):
```env
GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Khởi chạy Giao diện Web Chatbot (Khuyên dùng)
Giao diện Streamlit trực quan, hỗ trợ 3 chế độ (Effect-Aware, Baseline, So sánh Side-by-Side):
```bash
streamlit run src/web/app.py
```

### 4. Khởi chạy Backend REST API (FastAPI)
Swagger UI tương tác tại: `http://localhost:8000/docs`
```bash
uvicorn src.web.api:app --reload --port 8000
```

### 5. Chạy thử nghiệm qua Command Line
```bash
# Kiểm tra nhanh pipeline retrieval + effect check (không tốn token LLM)
python test_pipeline.py

# Chạy Baseline RAG (chưa kiểm tra hiệu lực)
python src/6_baseline_rag.py "Mức lương tối thiểu vùng hiện tại là bao nhiêu?"

# Chạy Effect-Aware RAG (có kiểm tra hiệu lực & cảnh báo luật cũ)
python src/10_effect_aware_rag.py "Mức lương tối thiểu vùng hiện tại là bao nhiêu?"
```
