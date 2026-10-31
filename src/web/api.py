"""
FASTAPI BACKEND — HỆ THỐNG HỎI ĐÁP PHÁP LUẬT LAO ĐỘNG VIỆT NAM (EFFECT-AWARE RAG)
Đồ án tốt nghiệp: Trần Tấn Phúc — D22CNTT03 | GVHD: TS. Nguyễn Trung Kiệt
Chạy: uvicorn src.web.api:app --reload --port 8000
"""

import sys
import pathlib
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Đảm bảo đường dẫn import hoạt động
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from rag_service import RAGService

app = FastAPI(
    title="VN Labor Law Effect-Aware RAG API",
    description="API hệ thống hỏi đáp pháp luật lao động Việt Nam tích hợp kiểm tra hiệu lực văn bản",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str = Field(..., description="Câu hỏi pháp luật lao động")
    mode: str = Field("effect_aware", description="Chế độ: 'effect_aware' hoặc 'baseline'")
    top_k_retrieve: int = Field(7, ge=1, le=20, description="Số lượng chunk truy xuất từ FAISS")
    top_k_llm: int = Field(5, ge=1, le=10, description="Số lượng chunk đưa vào LLM sau rerank")
    model_name: str = Field("gemini-2.5-flash", description="Mô hình Gemini sử dụng")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="Độ sáng tạo của LLM")


class CompareRequest(BaseModel):
    query: str = Field(..., description="Câu hỏi đối chứng giữa 2 mô hình")
    top_k_retrieve: int = Field(7, ge=1, le=20)
    top_k_llm: int = Field(5, ge=1, le=10)
    model_name: str = Field("gemini-2.5-flash")


# ── Dependency / Service Loader ──────────────────────────────────────────────
def get_service() -> RAGService:
    return RAGService.get_instance()


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "project": "VN Labor Law RAG — Effect-Aware System",
        "student": "Trần Tấn Phúc — D22CNTT03",
        "supervisor": "TS. Nguyễn Trung Kiệt",
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    srv = get_service()
    return {
        "status": "healthy",
        "faiss_vectors": srv.index.ntotal,
        "metadata_rows": len(srv.meta),
        "db_connected": srv.db_conn is not None,
    }


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Gửi câu hỏi tới hệ thống RAG (hỗ trợ cả effect_aware và baseline)."""
    srv = get_service()
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    if req.mode == "baseline":
        result = srv.run_baseline(
            query=req.query,
            top_k=req.top_k_llm,
            model_name=req.model_name,
            temperature=req.temperature,
        )
    else:
        result = srv.run_effect_aware(
            query=req.query,
            top_k_retrieve=req.top_k_retrieve,
            top_k_llm=req.top_k_llm,
            model_name=req.model_name,
            temperature=req.temperature,
        )

    return result


@app.post("/api/compare")
def compare_models(req: CompareRequest):
    """Chạy so sánh đối chứng song song giữa Baseline RAG và Effect-Aware RAG."""
    srv = get_service()
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    return srv.compare(
        query=req.query,
        top_k_retrieve=req.top_k_retrieve,
        top_k_llm=req.top_k_llm,
        model_name=req.model_name,
    )


@app.get("/api/documents/search")
def search_documents(
    q: str = Query(..., description="Từ khóa hoặc doc_id tìm kiếm"),
    limit: int = Query(10, ge=1, le=50),
):
    """Tìm kiếm văn bản trong phạm vi đề tài."""
    srv = get_service()
    return srv.search_docs(keyword=q, limit=limit)


@app.get("/api/documents/{doc_id}")
def document_detail(doc_id: str):
    """Tra cứu chi tiết hiệu lực và cây quan hệ của một văn bản."""
    srv = get_service()
    return srv.get_doc_relations(doc_id=doc_id)

