# 📊 Tổng hợp tiến độ — VN Labor Law RAG
**Sinh viên:** Trần Tấn Phúc — D22CNTT03 | **GVHD:** Nguyễn Trung Kiệt  
**Cập nhật:** 19/09/2026

---

## 🟢 Tiến độ tổng quan

| Giai đoạn | Số bước | Hoàn thành | Tỷ lệ |
|---|---|---|---|
| Data Pipeline (Bước 1–5) | 5 | 5 | ✅ **100%** |
| Baseline RAG (Bước 6) | 1 | 1 | ✅ **100%** |
| Effect-Aware RAG (Bước 7–12) | 6 | 6 | ✅ **100%** |
| Web / Evaluation / Báo cáo (Bước 13–16) | 4 | 0 | ⏳ **0%** |
| **Tổng cộng** | **16** | **12** | **75%** |

---

## ✅ Chi tiết từng bước đã hoàn thành

### 📁 Bước 1 — Lọc dữ liệu (`1_filter.py`)

| Chỉ số | Giá trị |
|---|---|
| Tổng văn bản trong dataset gốc (metadata.parquet) | ~171,000 |
| File content.parquet (raw) | ~748 MB trên disk |
| Văn bản sau lọc | **800 văn bản** |
| Chiến lược lọc | 3 tầng: EXACT_TITLE → PRIORITY → KEYWORD |

**Phân bố 800 văn bản theo nhóm:**

| Nhóm | Số văn bản | Mô tả |
|---|---|---|
| `tien_luong` | 350 | Tiền lương, lương tối thiểu, làm thêm giờ |
| `hop_dong_lao_dong` | 200 | Hợp đồng, sa thải, trợ cấp thôi việc |
| `bao_hiem_xa_hoi` | 150 | BHXH, BHYT, thai sản, hưu trí |
| `priority_doc` | 86 | Bộ luật/Luật liên quan lĩnh vực |
| `exact_title` | 14 | Bộ luật Lao động 2019, Luật BHXH 2014... |
| **Tổng** | **800** | |

---

### 📁 Bước 2 — Làm sạch metadata (`2_clean.py`)

| Chỉ số | Giá trị |
|---|---|
| Đầu vào | 800 văn bản |
| Đầu ra (`cleaned_documents.csv`) | **799 văn bản** (loại 1 văn bản lỗi) |
| Xử lý | Chuẩn hóa nhãn, liên kết văn bản-HTML, sửa bug mất cột |

---

### 📁 Bước 3 — Chunk hóa (`3_segment.py`)

| Chỉ số | Giá trị |
|---|---|
| Đầu vào | 799 văn bản |
| Đầu ra (`segmented_chunks.csv`) | **42,592 chunks** |
| Chiến lược parse | Strict regex → Loose regex → Fallback toàn văn |

**Phân bố chunks theo nhóm:**

| Nhóm | Số chunks |
|---|---|
| `hop_dong_lao_dong` | 18,161 |
| `tien_luong` | 12,165 |
| `exact_title` | 5,355 |
| `bao_hiem_xa_hoi` | 4,459 |
| `priority_doc` | 2,452 |
| **Tổng** | **42,592** |

> [!NOTE]  
> Mỗi chunk = 1 Điều hoặc 1 Khoản, kèm metadata đầy đủ: `doc_id`, `doc_title`, `dieu_so`, `khoan_so`, `chuong`, `effect_status_source`, `matched_group`.

---

### 📁 Bước 4 — Embedding (`4_embed.py`)

| Chỉ số | Giá trị |
|---|---|
| Model | `bkai-foundation-models/vietnamese-bi-encoder` |
| Số vectors | **42,592** |
| Chiều vector | **768** |
| File output | `chunk_embeddings.npy` (124.7 MB) |
| Tiền xử lý | PyVi tokenizer trước khi encode |

---

### 📁 Bước 5 — FAISS Index (`5_index.py`)

| Chỉ số | Giá trị |
|---|---|
| Số vectors trong index | **42,592** |
| Chiều | **768** |
| Index type | FAISS IndexFlatIP (cosine similarity) |
| File output | `faiss.index` (124.7 MB) |
| Top-K retrieval | K=5 (baseline) / K=7 (effect-aware) |

---

### 📁 Bước 6 — Baseline RAG (`6_baseline_rag.py`)

| Thành phần | Chi tiết |
|---|---|
| Retrieval | FAISS semantic search, top-5 chunks |
| LLM | Google Gemini API — `gemini-2.5-flash` (miễn phí) |
| Augmentation | Build context từ 5 chunks có trích dẫn nguồn |
| Generation | temperature=0.2, max_output_tokens=1024 |
| System Prompt | Chỉ trả lời từ context, bắt buộc trích dẫn `(Nguồn: ..., Điều N)` |
| Pipeline | Query → ViTokenizer → FAISS → Build context → Gemini → Answer |

---

### 📁 Bước 7 — Chuẩn hóa Relationships (`7_relationships.py`)

| Chỉ số | Giá trị |
|---|---|
| Tổng quan hệ gốc (`relationships.parquet`) | **1,033,255** |
| Số loại quan hệ gốc | nhiều loại (raw) |
| Sau khi map → 5 nhóm chuẩn hóa | **43,478 quan hệ** |
| File output | `relationships_clean.csv` (2.2 MB) |

**Phân bố 43,478 quan hệ sau chuẩn hóa:**

| Loại | Số lượng | Importance | Ý nghĩa |
|---|---|---|---|
| `DAN_CHIEU` | 39,491 | 1 | Dẫn chiếu, căn cứ |
| `HUONG_DAN` | 1,654 | 2 | Hướng dẫn thi hành |
| `BAI_BO` | 1,324 | 4 | Bãi bỏ, đình chỉ ⚠️ |
| `THAY_THE` | 541 | 5 | Thay thế toàn bộ 🔴 |
| `SUA_DOI` | 468 | 3 | Sửa đổi, bổ sung ⚠️ |

---

### 📁 Bước 8 — Xây đồ thị NetworkX + SQLite (`8_build_graph.py`)

| Chỉ số | Giá trị |
|---|---|
| Nodes (văn bản) trong graph | **36,726** |
| Edges (quan hệ) trong graph | **42,571** |
| Node trong phạm vi đề tài | 800 |
| File pickle | `legal_graph.gpickle` (3.5 MB) |
| SQLite DB | `legal_graph.db` (4.6 MB) |
| DB: bảng `documents` | 800 records |
| DB: bảng `relationships` | 43,478 records |
| Chức năng | `query_affected_by()`, `trace_chain()` (BFS, max_depth=5) |

> [!NOTE]  
> Graph có nhiều node hơn 800 vì các `other_doc_id` từ relationships ngoài phạm vi đề tài cũng được thêm vào (node với `in_scope=False`).

---

### 📁 Bước 9 — Effect Checker (`9_effect_checker.py`)

| Thành phần | Chi tiết |
|---|---|
| Class | `EffectChecker` (singleton, lazy-loaded) |
| Levels | OK / WARNING / DANGER / UNKNOWN |
| Method chính | `check_effect_status(doc_id)` → EffectStatus |
| Method chính | `check_chunks(chunks)` → enriched + reranked list |
| Method chính | `build_context_with_warning(chunks)` → context string |
| Logic phân loại | Đọc `effect_status_source` gốc + tra đồ thị THAY_THE/BAI_BO |
| Reranking | OK → WARNING → UNKNOWN → DANGER |
| Status map | 8 giá trị gốc → OK/WARNING/DANGER/UNKNOWN |

**Ánh xạ trạng thái hiệu lực:**

| Giá trị gốc (vbpl.vn) | Level |
|---|---|
| Còn hiệu lực | ✅ OK |
| Hết hiệu lực một phần / Ngưng hiệu lực một phần / Chưa có hiệu lực | ⚠️ WARNING |
| Ngưng hiệu lực / Hết hiệu lực toàn bộ / Không còn phù hợp | 🔴 DANGER |
| Chưa xác định | ❓ UNKNOWN |

---

### 📁 Bước 10 — Effect-Aware RAG (`10_effect_aware_rag.py`)

| Thành phần | Chi tiết |
|---|---|
| Top-K retrieval | **7** (nhiều hơn baseline 5 để có buffer rerank) |
| Chunks dùng cho LLM | Top **5** sau rerank |
| System Prompt bổ sung | LLM phải đề cập cảnh báo [WARNING]/[DANGER] trong câu trả lời |
| Context format | Kèm `⚠️ [WARNING/DANGER] message` cho từng chunk |
| Output bổ sung | Bảng tóm tắt hiệu lực (✅/⚠️/🔴/❓) từng chunk |
| Điểm khác vs Baseline | +EffectChecker → +Rerank → +Warning context → +LLM-aware prompt |

---

## ⏳ Còn lại (chưa làm)

| Bước | Nội dung | Ước lượng công |
|---|---|---|
| **Bước 11** | Backend FastAPI + giao diện chatbot web (`src/web/`) | Trung bình |
| **Bước 12** | Xây bộ câu hỏi kiểm thử (`data/eval/`) | Nhỏ–Trung bình |
| **Bước 13** | Script đánh giá so sánh Baseline vs Effect-Aware (`src/11_evaluate.py`) | Trung bình |
| **Bước 14** | Hoàn thiện báo cáo + demo | Lớn |

---

## 📦 Tóm tắt file đầu ra (tất cả đã có)

| File | Kích thước | Mô tả |
|---|---|---|
| `data/raw/filtered_documents.csv` | 25.9 MB | 800 văn bản đã lọc |
| `data/processed/cleaned_documents.csv` | 24.8 MB | 799 văn bản đã làm sạch |
| `data/processed/segmented_chunks.csv` | 45.6 MB | 42,592 chunks Điều/Khoản |
| `data/processed/relationships_clean.csv` | 2.2 MB | 43,478 quan hệ chuẩn hóa |
| `data/processed/chunk_embeddings.npy` | 124.7 MB | 42,592 × 768 float32 vectors |
| `data/processed/chunk_metadata.parquet` | 9.4 MB | Metadata của 42,592 chunks |
| `data/index/faiss.index` | 124.7 MB | FAISS index sẵn sàng truy xuất |
| `data/graph/legal_graph.gpickle` | 3.5 MB | NetworkX DiGraph (36,726 nodes) |
| `data/graph/legal_graph.db` | 4.6 MB | SQLite (800 docs, 43,478 rels) |

**Tổng dung lượng data đầu ra (processed + index + graph): ~339 MB**

---

## 🔄 Pipeline hoàn chỉnh (end-to-end đã chạy được)

```
[Câu hỏi]
    ↓ ViTokenizer
[FAISS Search] → top-7 chunks (42,592 vectors, dim=768)
    ↓
[EffectChecker] → kiểm tra hiệu lực từng chunk (graph + SQLite)
    ↓ rerank: OK > WARNING > UNKNOWN > DANGER
[Build Context] → ghép top-5, kèm cảnh báo ⚠️/🔴
    ↓
[Gemini 2.5-flash] → sinh câu trả lời + trích dẫn + cảnh báo hiệu lực
    ↓
[Output] → Answer + Bảng tóm tắt hiệu lực
```
