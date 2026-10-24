"""
Script kiểm tra pipeline nhanh — KHÔNG gọi LLM
Chỉ test: FAISS retrieval + EffectChecker
Chạy: python test_pipeline.py
"""
import sys, io, importlib.util, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import faiss
import pandas as pd
from pyvi import ViTokenizer
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"
INDEX_PATH  = "data/index/faiss.index"
META_PATH   = "data/processed/chunk_metadata.parquet"
TOP_K       = 5

TEST_QUERIES = [
    "Mức lương tối thiểu vùng hiện tại là bao nhiêu?",
    "Người lao động được làm thêm tối đa bao nhiêu giờ trong một năm?",
    "Thời gian nghỉ thai sản của lao động nữ là bao nhiêu tuần?",
]

# ── Load model một lần ────────────────────────────────────────────
print("🔄 Đang load FAISS index + metadata...")
index = faiss.read_index(INDEX_PATH)
meta  = pd.read_parquet(META_PATH)
print(f"  ✅ FAISS: {index.ntotal:,} vectors | Metadata: {len(meta):,} rows")

print("🔄 Đang load embedding model (có thể mất vài phút lần đầu)...")
model = SentenceTransformer(EMBED_MODEL)
print("  ✅ Embedding model loaded")

# ── Load EffectChecker ────────────────────────────────────────────
print("🔄 Đang load EffectChecker...")
_spec = importlib.util.spec_from_file_location(
    "effect_checker",
    pathlib.Path("src/9_effect_checker.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
checker = _mod.get_checker()
print("  ✅ EffectChecker loaded (graph + SQLite)")

# ── Chạy test từng query ──────────────────────────────────────────
print("\n" + "="*65)
print("📊 KẾT QUẢ RETRIEVAL + EFFECT CHECK")
print("="*65)

for q in TEST_QUERIES:
    print(f"\n🔍 Câu hỏi: {q}")
    print("-"*65)

    q_seg = ViTokenizer.tokenize(q)
    q_vec = model.encode([q_seg], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    scores, indices = index.search(q_vec, TOP_K)

    chunks = []
    for score, idx in zip(scores[0], indices[0]):
        row = meta.iloc[idx]
        chunks.append({
            "score":     float(score),
            "doc_id":    str(row["doc_id"]),
            "doc_title": row["doc_title"],
            "dieu_so":   row["dieu_so"],
            "khoan_so":  row.get("khoan_so"),
            "text":      row["text"],
            "matched_group": row.get("matched_group", ""),
        })

    enriched = checker.check_chunks(chunks)

    for i, c in enumerate(enriched, 1):
        level = c.get("effect_level", "?")
        icon  = {"OK": "✅", "WARNING": "⚠️ ", "DANGER": "🔴", "UNKNOWN": "❓"}.get(level, "  ")
        khoan = f" K{c['khoan_so']}" if pd.notna(c.get("khoan_so")) else ""
        title_short = c['doc_title'][:45] + "..." if len(c['doc_title']) > 45 else c['doc_title']
        print(f"  {i}. {icon}{level:<8} score={c['score']:.3f}  "
              f"Đ{c['dieu_so']}{khoan} — {title_short}")
        if level in ("WARNING", "DANGER"):
            print(f"       ↳ {c.get('effect_message', '')[:80]}")

print("\n" + "="*65)
print("✅ Pipeline retrieval + effect check hoạt động bình thường!")
print("="*65)
