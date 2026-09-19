"""
TUẦN 12 — EFFECT-AWARE RAG (TÍCH HỢP KIỂM TRA HIỆU LỰC)
----------------------------------------------------
Input:  data/index/faiss.index
        data/processed/chunk_metadata.parquet
        data/graph/legal_graph.gpickle + legal_graph.db  (từ Tuần 10)
        src/9_effect_checker.py                           (từ Tuần 11)

Output: In câu trả lời ra màn hình (kèm trích dẫn + cảnh báo hiệu lực)

Điểm khác so với Baseline RAG (6_baseline_rag.py):
  1. Sau khi FAISS retrieval, gọi EffectChecker.check_chunks() để:
     - Gắn thông tin hiệu lực vào mỗi chunk
     - Rerank: chunk còn hiệu lực (OK) lên trước, DANGER xuống cuối
  2. Context gửi cho LLM bao gồm cảnh báo hiệu lực [WARNING]/[DANGER]
     để LLM tự nhận thức và đưa vào câu trả lời
  3. System prompt bổ sung: LLM phải đề cập trạng thái hiệu lực khi có cảnh báo
  4. Output in thêm bảng tóm tắt hiệu lực các chunk được dùng

Cách chạy:
    python src/10_effect_aware_rag.py "câu hỏi cần hỏi"
    python src/10_effect_aware_rag.py "câu hỏi" --top-k 7
"""

import sys
import argparse
import faiss
import pandas as pd
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types

# Import Effect Checker từ Tuần 11
# (dùng importlib vì tên file bắt đầu bằng số)
import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location(
    "effect_checker",
    pathlib.Path(__file__).parent / "9_effect_checker.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
get_checker = _mod.get_checker
EffectLevel = _mod.EffectLevel

EMBED_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
LLM_MODEL_NAME   = "gemini-2.5-flash"
INDEX_PATH       = "data/index/faiss.index"
METADATA_PATH    = "data/processed/chunk_metadata.parquet"
TOP_K_DEFAULT    = 7   # lấy nhiều hơn Baseline (5) vì một số chunk sẽ bị hạ ưu tiên

SYSTEM_PROMPT = """Bạn là trợ lý tra cứu pháp luật lao động Việt Nam.
Chỉ trả lời dựa trên các đoạn văn bản pháp luật được cung cấp trong ngữ cảnh.

QUAN TRỌNG — Xử lý cảnh báo hiệu lực:
- Nếu một đoạn có gắn [WARNING] hoặc [DANGER], hãy đề cập rõ trong câu trả lời
  rằng văn bản đó có thể đã hết hiệu lực hoặc bị sửa đổi.
- Ưu tiên trích dẫn các đoạn CÒN HIỆU LỰC. Với đoạn [DANGER], chỉ dẫn chiếu
  nếu không có nguồn thay thế và phải nêu rõ cảnh báo.
- Nếu không có đoạn nào còn hiệu lực, hãy nói rõ giới hạn này.
- Với mỗi ý trả lời, trích dẫn nguồn: (Nguồn: <tên văn bản>, Điều <số>).
- Trả lời ngắn gọn, rõ ràng, đúng trọng tâm câu hỏi."""


def retrieve(query: str, top_k: int = TOP_K_DEFAULT) -> list[dict]:
    """Bước Retrieval — giống Baseline RAG."""
    index = faiss.read_index(INDEX_PATH)
    meta  = pd.read_parquet(METADATA_PATH)
    model = SentenceTransformer(EMBED_MODEL_NAME)

    q_seg = ViTokenizer.tokenize(query)
    q_vec = model.encode(
        [q_seg], normalize_embeddings=True, convert_to_numpy=True
    ).astype("float32")

    scores, indices = index.search(q_vec, top_k)

    chunks = []
    for score, idx in zip(scores[0], indices[0]):
        row = meta.iloc[idx]
        chunks.append({
            "score":      float(score),
            "doc_id":     str(row["doc_id"]),
            "doc_title":  row["doc_title"],
            "dieu_so":    row["dieu_so"],
            "khoan_so":   row.get("khoan_so"),
            "text":       row["text"],
            "matched_group": row.get("matched_group", ""),
        })
    return chunks


def generate_answer(query: str, enriched_chunks: list[dict]) -> str:
    """Bước Generation — dùng context có kèm cảnh báo hiệu lực."""
    checker = get_checker()
    context = checker.build_context_with_warning(enriched_chunks)

    client = genai.Client()
    user_message = f"""Ngữ cảnh (các đoạn văn bản pháp luật liên quan, kèm trạng thái hiệu lực):
{context}

Câu hỏi: {query}"""

    response = client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            max_output_tokens=1024,
        ),
    )
    return response.text


def print_effect_summary(enriched_chunks: list[dict]):
    """In bảng tóm tắt trạng thái hiệu lực các chunk được dùng."""
    print("\n📋 Tóm tắt hiệu lực các đoạn truy xuất:")
    print(f"  {'#':<3} {'Level':<8} {'Score':<7} {'Nguồn'}")
    print("  " + "-" * 65)
    for i, c in enumerate(enriched_chunks, 1):
        level = c.get("effect_level", "?")
        score = c.get("score", 0)
        khoan = f" K{c['khoan_so']}" if pd.notna(c.get("khoan_so")) else ""
        icon = {"OK": "✅", "WARNING": "⚠️ ", "DANGER": "🔴", "UNKNOWN": "❓"}.get(level, "  ")
        src = f"{c['doc_title'][:35]}... Đ{c['dieu_so']}{khoan}"
        print(f"  {i:<3} {icon}{level:<6} {score:.3f}  {src}")


def main():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(description="Effect-Aware RAG — hỏi đáp pháp luật lao động")
    parser.add_argument("query", help="Câu hỏi cần tra cứu")
    parser.add_argument("--top-k", type=int, default=TOP_K_DEFAULT,
                        help=f"Số chunk truy xuất (mặc định: {TOP_K_DEFAULT})")
    args = parser.parse_args()

    query = args.query
    top_k = args.top_k

    print(f"Câu hỏi: {query}\n")
    print(f"Đang truy xuất top-{top_k} đoạn liên quan...")
    chunks = retrieve(query, top_k)

    print("Đang kiểm tra hiệu lực các đoạn truy xuất...")
    checker = get_checker()
    enriched = checker.check_chunks(chunks)

    print_effect_summary(enriched)

    # Chỉ dùng top-5 sau rerank cho LLM (để giữ context ngắn gọn)
    top_for_llm = enriched[:5]

    ok_count  = sum(1 for c in top_for_llm if c["effect_level"] == "OK")
    warn_count = sum(1 for c in top_for_llm if c["effect_level"] == "WARNING")
    danger_count = sum(1 for c in top_for_llm if c["effect_level"] == "DANGER")
    print(f"\n  → Dùng 5 đoạn đầu cho LLM: "
          f"{ok_count} OK / {warn_count} WARNING / {danger_count} DANGER")

    print("\nĐang sinh câu trả lời...\n")
    answer = generate_answer(query, top_for_llm)

    print("=" * 60)
    print("CÂU TRẢ LỜI (Effect-Aware RAG):")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()
