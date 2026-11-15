# Hệ Thống Hỏi Đáp & Tham Mưu Pháp Luật Lao Động Việt Nam
### Effect-Aware Knowledge Graph RAG & War Room Multi-Agent System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vn-labor-law-rag.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FAISS](https://img.shields.io/badge/Index-FAISS%20768d-orange.svg)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Hệ thống tra cứu, tham mưu và hỗ trợ giải quyết tranh chấp pháp luật lao động Việt Nam theo Bộ luật Lao động 2019 và hệ thống văn bản hướng dẫn thi hành (đồng bộ từ vbpl.vn). Hệ thống khắc phục triệt để hiện tượng mô hình ngôn ngữ lớn (LLM) trích dẫn các điều luật đã hết hiệu lực thông qua **Đồ thị tri thức nhận thức hiệu lực (Effect-Aware Knowledge Graph RAG)** kết hợp **Phòng tác chiến Đa tác nhân (War Room Multi-Agent System)** 5 bước.

- **Tác giả:** Trần Tấn Phúc
- **Giảng viên hướng dẫn:** TS. Nguyễn Trung Kiệt
- **Ứng dụng trực tuyến:** [https://vn-labor-law-rag.streamlit.app](https://vn-labor-law-rag.streamlit.app)

---

## 📌 Tính Năng Nổi Bật

### 1. 🛡️ Cơ Chế Effect-Aware RAG (Nhận Thức Vòng Đời Hiệu Lực)
- **Vấn đề của RAG truyền thống:** Khi người dùng hỏi về quy định lao động, tìm kiếm ngữ nghĩa thông thường (Cosine Similarity) thường ưu tiên các văn bản cũ có độ tương đồng từ vựng cao (như Nghị định 05/2015/NĐ-CP, Nghị định 44/2013/NĐ-CP) dù các văn bản này **đã hết hiệu lực toàn bộ**, dẫn đến việc LLM tư vấn sai luật.
- **Giải pháp Effect-Aware:** 
  - Tích hợp Đồ thị tri thức pháp lý gồm **36,726 đỉnh** và **42,571 cạnh quan hệ** (sửa đổi, bổ sung, thay thế, bãi bỏ, hướng dẫn).
  - Tự động thẩm định trạng thái qua 4 cấp độ: `OK` (Còn hiệu lực), `WARNING` (Sửa đổi/Cảnh báo), `DANGER` (Bị thay thế/Hết hiệu lực), `UNKNOWN`.
  - Thuật toán Reranking tự động loại bỏ các đoạn trích dẫn mang nhãn `DANGER`, ưu tiên văn bản hiện hành và cảnh báo tường minh đến người dùng trong thời gian duyệt đồ thị cực nhanh (**< 0.02 giây**).

### 2. 🏛️ Phòng Tác Chiến War Room Đa Tác Nhân (Multi-Agent System)
Mô hình hóa quy trình xử lý công vụ tại cơ quan quản lý lao động qua 5 Agent AI chuyên môn hóa, phối hợp tuần tự và trực quan hóa sinh động:
1. **Agent 1 — Rà soát Căn cứ Pháp lý:** Truy xuất cơ sở dữ liệu và loại bỏ triệt để các điều luật lỗi thời.
2. **Agent 2 — Đề xuất Phương án Xử lý:** Lập 02 phương án giải quyết (Phương án 1: Hòa giải, thương lượng cơ sở; Phương án 2: Chế tài hành chính & Khởi kiện).
3. **Agent 3 — Phản biện Rủi ro & Bịt kẽ hở:** Đóng vai trò đối lập, soi chiếu rủi ro về thời hiệu khiếu nại (180 ngày), trình tự thủ tục và yêu cầu bổ sung chứng cứ.
4. **Agent 4 — Soạn thảo Văn bản Hành chính:** Tự động thiết kế biểu mẫu công vụ (Giấy mời làm việc, Biên bản hòa giải, Công văn kiến nghị) chuẩn thể thức **Nghị định 30/2020/NĐ-CP** trên khổ giấy A4.
5. **Agent 5 — Tổng hợp & Đánh giá Quyết định:** Áp dụng ma trận chấm điểm đa tiêu chí (MCDA), đưa ra khuyến nghị tối ưu trình Cán bộ phê duyệt.

### 3. 📊 Kết Quả Thực Nghiệm Định Lượng (Benchmark Suite)
Đánh giá so sánh trực diện giữa **Baseline RAG** và **Effect-Aware RAG** trên bộ dữ liệu kiểm thử chuẩn (Golden Testset 25 câu hỏi tình huống thực tế):
- **Chỉ số MRR (Mean Reciprocal Rank):** Đạt **0.865** (tăng **+13.3%** so với Baseline RAG 0.763).
- **Độ chính xác Top-1 (Hit@1):** Đạt **80.0%** (so với 60.0% của Baseline).
- **Lá chắn an toàn pháp lý:** Baseline RAG dẫn chiếu sai **54/125** đoạn trích dẫn hết hiệu lực (tỷ lệ rủi ro 43.2%), trong khi Effect-Aware RAG đạt **0% rủi ro** (100% căn cứ đều đang còn hiệu lực thi hành).

---

## 🗄️ Cơ Sở Dữ Liệu & Mô Hình

- **Dataset gốc:** [`th1nhng0/vietnamese-legal-documents`](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents) trên Hugging Face (đồng bộ từ Cổng thông tin vbpl.vn - Bộ Tư pháp).
- **Phạm vi lọc hạt nhân:** **800 văn bản quy phạm pháp luật** thuộc 3 nhóm quan trọng nhất: Hợp đồng lao động, Tiền lương & Chế độ, Bảo hiểm xã hội. Dữ liệu cập nhật tính đến **hết năm 2024**.
- **Chỉ mục vector:** **42,592 chunks** văn bản pháp lý được phân đoạn theo cấu trúc Chương / Điều / Khoản.
- **Mô hình Embedding:** [`bkai-foundation-models/vietnamese-bi-encoder`](https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder) (768 chiều, tối ưu cho tiếng Việt).
- **Chỉ mục tìm kiếm:** FAISS (Facebook AI Similarity Search) chỉ số `IndexFlatIP` (Cosine Similarity chuẩn hóa L2).
- **Đồ thị quan hệ:** NetworkX DiGraph + SQLite cache lưu trữ 43,478 liên kết phả hệ văn bản.

---

## 📁 Cấu Trúc Dự Án

```text
vn-labor-law-rag/
├── data/
│   ├── raw/                 # Metadata và nội dung văn bản thô
│   ├── processed/           # 42,592 chunks, embeddings và bảng quan hệ sạch
│   ├── graph/               # Đồ thị tri thức pháp lý (legal_graph.db & gpickle)
│   └── index/               # FAISS vector index (faiss.index)
├── evaluation/              # Bộ dữ liệu kiểm thử chuẩn (25 câu hỏi) & Báo cáo benchmark
│   ├── golden_testset.json
│   ├── run_benchmark.py
│   └── bao_cao_thuc_nghiem_dinh_luong.md
├── src/
│   ├── 1_filter.py ... 10_effect_aware_rag.py   # Pipeline xử lý dữ liệu từ tuần 1-12
│   ├── agents/              # Mô-đun War Room Orchestrator & 5 Agent AI
│   │   ├── war_room.py
│   │   └── prompts.py
│   └── web/                 # Giao diện người dùng & API Service
│       ├── app.py           # Streamlit Web App chính
│       ├── war_room_ui.py   # Không gian phòng War Room 2D SVG & định dạng A4
│       ├── ui_styles.py     # Hệ thống CSS giao diện hiện đại
│       ├── benchmark_ui.py  # Dashboard hiển thị báo cáo thực nghiệm
│       ├── rag_service.py   # Service layer điều phối FAISS, Graph & LLM
│       └── api.py           # Backend REST API (FastAPI)
├── requirements.txt         # Danh mục thư viện phụ thuộc
└── README.md
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Yêu cầu môi trường
- Python 3.10 trở lên.
- RAM khuyến nghị: 8GB trở lên.

### 2. Cài đặt các thư viện phụ thuộc
```bash
git clone https://github.com/fate1105/vn-labor-law-rag.git
cd vn-labor-law-rag
pip install -r requirements.txt
```

### 3. Cấu hình khóa API (Google AI Studio)
Tạo file `.env` tại thư mục gốc của dự án:
```env
GEMINI_API_KEY="your-gemini-api-key"
```
*(Khóa API có thể đăng ký miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey)).*

### 4. Khởi chạy Ứng dụng Web Chatbot (Streamlit)
```bash
streamlit run src/web/app.py
```
Sau khi khởi chạy, truy cập trình duyệt tại `http://localhost:8501`. Ứng dụng cung cấp 3 chế độ:
- **🏛️ War Room Đa tác nhân:** Mô phỏng phòng tác chiến giải quyết vụ việc thực tế.
- **⚖️ So sánh song song (Side-by-Side):** Đối chứng kết quả giữa Baseline RAG và Effect-Aware RAG.
- **📊 Báo cáo Đánh giá Định lượng:** Xem đầy đủ biểu đồ KPI, bảng chỉ số MRR và danh sách 25 câu hỏi kiểm thử chuẩn.

### 5. Khởi chạy Backend REST API (FastAPI)
```bash
uvicorn src.web.api:app --reload --port 8000
```
Tài liệu Swagger UI tương tác trực tiếp tại: `http://localhost:8000/docs`.
