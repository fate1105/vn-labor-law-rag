"""
TUẦN 8 — BASELINE RAG: SINH CÂU TRẢ LỜI KÈM TRÍCH DẪN
----------------------------------------------------
Input:  data/index/faiss.index, data/processed/chunk_metadata.parquet
Output: In câu trả lời ra màn hình (kèm trích dẫn nguồn)

Đây là bản BASELINE — chưa có kiểm tra hiệu lực / đồ thị quan hệ văn bản
(phần đó là Effect-Aware RAG, sẽ làm ở giai đoạn sau theo đề cương).
Pipeline baseline: câu hỏi -> truy xuất ngữ nghĩa (FAISS) -> LLM sinh câu
trả lời dựa trên các đoạn đã truy xuất, kèm trích dẫn.

Kết quả dự kiến: hoàn thành phiên bản chatbot RAG cơ bản.

LLM dùng: Google Gemini API (gemini-2.5-flash) — có gói miễn phí, không
cần thẻ tín dụng, đủ dùng cho đồ án. Lấy API key tại:
https://aistudio.google.com/apikey

Cần cài đặt API key trước khi chạy:
    export GEMINI_API_KEY="your-api-key"      (Mac/Linux)
    setx GEMINI_API_KEY "your-api-key"         (Windows, mở lại terminal sau khi setx)

Cách chạy:
    python src/baseline_rag.py "câu hỏi cần hỏi"
"""

import sys
import faiss
import pandas as pd
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types

EMBED_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
LLM_MODEL_NAME = "gemini-2.5-flash"  # nằm trong gói miễn phí của Gemini API
INDEX_PATH = "data/index/faiss.index"
METADATA_PATH = "data/processed/chunk_metadata.parquet"
TOP_K = 5

SYSTEM_PROMPT = """Bạn là trợ lý tra cứu pháp luật lao động Việt Nam.
Chỉ trả lời dựa trên các đoạn văn bản pháp luật được cung cấp trong ngữ cảnh.
Nếu ngữ cảnh không đủ thông tin để trả lời, hãy nói rõ là không tìm thấy quy định
liên quan, KHÔNG tự suy đoán hay bịa thông tin.
Với mỗi ý trả lời, phải trích dẫn rõ nguồn theo định dạng: (Nguồn: <tên văn bản>, Điều <số>).
Trả lời ngắn gọn, rõ ràng, đúng trọng tâm câu hỏi."""


def retrieve(query: str, top_k: int = TOP_K):
    """Truy xuất ngữ nghĩa — bước Retrieval của RAG."""
    index = faiss.read_index(INDEX_PATH)
    meta = pd.read_parquet(METADATA_PATH)
    embed_model = SentenceTransformer(EMBED_MODEL_NAME)

    q_seg = ViTokenizer.tokenize(query)
    q_vec = embed_model.encode([q_seg], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    scores, indices = index.search(q_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        row = meta.iloc[idx]
        results.append({
            "score": float(score),
            "doc_title": row["doc_title"],
            "dieu_so": row["dieu_so"],
            "khoan_so": row.get("khoan_so"),
            "text": row["text"],
        })
    return results


def build_context(chunks) -> str:
    """Ghép các chunk truy xuất được thành ngữ cảnh cho LLM — bước Augmentation."""
    parts = []
    for i, c in enumerate(chunks, start=1):
        khoan = f", Khoản {c['khoan_so']}" if pd.notna(c.get("khoan_so")) else ""
        parts.append(
            f"[Đoạn {i}] Nguồn: {c['doc_title']}, Điều {c['dieu_so']}{khoan}\n{c['text']}"
        )
    return "\n\n".join(parts)


def generate_answer(query: str, chunks) -> str:
    """Sinh câu trả lời từ ngữ cảnh — bước Generation, dùng Gemini API."""
    context = build_context(chunks)
    client = genai.Client()  # đọc API key từ biến môi trường GEMINI_API_KEY

    user_message = f"""Ngữ cảnh (các đoạn văn bản pháp luật liên quan):
{context}

Câu hỏi: {query}"""

    response = client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,  # giữ thấp để câu trả lời bám sát ngữ cảnh, hạn chế bịa
            max_output_tokens=1024,
        ),
    )
    return response.text


def main():
    if len(sys.argv) < 2:
        print('Cách dùng: python src/baseline_rag.py "câu hỏi cần hỏi"')
        return

    query = sys.argv[1]

    print(f"Câu hỏi: {query}\n")
    print("Đang truy xuất các Điều/Khoản liên quan...")
    chunks = retrieve(query)

    print(f"Đã truy xuất {len(chunks)} đoạn liên quan:")
    for c in chunks:
        khoan = f" Khoản {c['khoan_so']}" if pd.notna(c.get("khoan_so")) else ""
        print(f"  - {c['doc_title']} — Điều {c['dieu_so']}{khoan} (score={c['score']:.3f})")

    print("\nĐang sinh câu trả lời...\n")
    answer = generate_answer(query, chunks)

    print("=" * 60)
    print("CÂU TRẢ LỜI (Baseline RAG):")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()