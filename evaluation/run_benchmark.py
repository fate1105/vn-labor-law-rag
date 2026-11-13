"""
AUTOMATED BENCHMARK SUITE — ĐÁNH GIÁ ĐỊNH LƯỢNG HỆ THỐNG RAG PHÁP LUẬT LAO ĐỘNG
So sánh định lượng giữa Baseline RAG và Effect-Aware RAG
Tác vụ: Retrieval Metrics, Safety & Effect-Checking, Generation Quality
"""

import os
import sys
import io
import time
import json
import argparse
import pathlib
from typing import Dict, Any, List

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pandas as pd
import numpy as np

# Đảm bảo import được từ thư mục gốc
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.web.rag_service import RAGService

TESTSET_PATH = PROJECT_ROOT / "evaluation" / "golden_testset.json"
OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def check_doc_match(doc_title: str, target_list: List[str]) -> bool:
    """Kiểm tra xem tên văn bản có khớp với bất kỳ văn bản mục tiêu nào không."""
    doc_title_lower = doc_title.lower()
    for target in target_list:
        if target.lower() in doc_title_lower:
            return True
    return False


def calculate_metrics_for_case(
    test_case: Dict[str, Any],
    baseline_chunks: List[Dict[str, Any]],
    effect_chunks: List[Dict[str, Any]],
    baseline_answer: str = "",
    effect_answer: str = "",
) -> Dict[str, Any]:
    """Tính toán toàn bộ các chỉ số cho một câu test case."""
    targets = test_case.get("target_docs", [])
    outdated_traps = test_case.get("outdated_trap_docs", [])
    key_facts = test_case.get("key_facts", [])

    # 1. Retrieval Metrics cho Baseline
    base_hit3 = 0
    base_hit5 = 0
    base_mrr = 0.0
    base_outdated_count = 0

    for rank, chunk in enumerate(baseline_chunks[:5], start=1):
        is_target = check_doc_match(chunk["doc_title"], targets)
        is_outdated = check_doc_match(chunk["doc_title"], outdated_traps) or chunk.get("effect_status_source") in [
            "Hết hiệu lực toàn bộ", "Ngưng hiệu lực"
        ]

        if is_target:
            if rank <= 3 and base_hit3 == 0:
                base_hit3 = 1
            if rank <= 5 and base_hit5 == 0:
                base_hit5 = 1
            if base_mrr == 0.0:
                base_mrr = 1.0 / rank

        if is_outdated:
            base_outdated_count += 1

    # 2. Retrieval & Reranking Metrics cho Effect-Aware
    eff_hit3 = 0
    eff_hit5 = 0
    eff_mrr = 0.0
    eff_danger_in_top5 = 0
    eff_warning_in_top5 = 0

    for rank, chunk in enumerate(effect_chunks[:5], start=1):
        is_target = check_doc_match(chunk["doc_title"], targets)
        lvl = chunk.get("effect_level", "UNKNOWN")

        if is_target:
            if rank <= 3 and eff_hit3 == 0:
                eff_hit3 = 1
            if rank <= 5 and eff_hit5 == 0:
                eff_hit5 = 1
            if eff_mrr == 0.0:
                eff_mrr = 1.0 / rank

        if lvl == "DANGER":
            eff_danger_in_top5 += 1
        elif lvl == "WARNING":
            eff_warning_in_top5 += 1

    # 3. Fact Coverage (nếu có câu trả lời từ LLM)
    base_fact_cov = 0.0
    eff_fact_cov = 0.0
    if key_facts:
        if baseline_answer:
            base_matches = sum(1 for f in key_facts if f.lower() in baseline_answer.lower())
            base_fact_cov = base_matches / len(key_facts)
        if effect_answer:
            eff_matches = sum(1 for f in key_facts if f.lower() in effect_answer.lower())
            eff_fact_cov = eff_matches / len(key_facts)

    # 4. Kiểm tra cảnh báo hiệu lực trong câu trả lời
    base_has_warning = any(w in baseline_answer.lower() for w in ["cảnh báo", "hết hiệu lực", "lưu ý", "sửa đổi"])
    eff_has_warning = any(w in effect_answer.lower() for w in ["cảnh báo", "hết hiệu lực", "lưu ý", "sửa đổi"])

    return {
        "id": test_case["id"],
        "category": test_case["category"],
        "question": test_case["question"],
        # Baseline metrics
        "baseline_hit@3": base_hit3,
        "baseline_hit@5": base_hit5,
        "baseline_mrr": round(base_mrr, 4),
        "baseline_outdated_in_top5": base_outdated_count,
        "baseline_fact_coverage": round(base_fact_cov, 4),
        "baseline_has_warning": base_has_warning,
        # Effect-Aware metrics
        "effect_hit@3": eff_hit3,
        "effect_hit@5": eff_hit5,
        "effect_mrr": round(eff_mrr, 4),
        "effect_danger_in_top5": eff_danger_in_top5,
        "effect_warning_in_top5": eff_warning_in_top5,
        "effect_fact_coverage": round(eff_fact_cov, 4),
        "effect_has_warning": eff_has_warning,
    }


def run_benchmark(eval_llm: bool = False, max_cases: int = None):
    print("=" * 75)
    print("🚀 BẮT ĐẦU CHẠY BENCHMARK ĐỊNH LƯỢNG HỆ THỐNG RAG PHÁP LUẬT LAO ĐỘNG")
    print(f"   Chế độ đánh giá: {'Đầy đủ (Retrieval + LLM Generation)' if eval_llm else 'Truy xuất & Hiệu lực (Retrieval & Validity)'}")
    print("=" * 75)

    if not TESTSET_PATH.exists():
        print(f"❌ Không tìm thấy file testset: {TESTSET_PATH}")
        return

    with open(TESTSET_PATH, "r", encoding="utf-8") as f:
        testset_data = json.load(f)

    test_cases = testset_data["test_cases"]
    if max_cases:
        test_cases = test_cases[:max_cases]

    print(f"📋 Tổng số câu hỏi kiểm thử: {len(test_cases)}")
    service = RAGService.get_instance()

    results = []
    detailed_logs = []

    for idx, tc in enumerate(test_cases, start=1):
        qid = tc["id"]
        cat = tc["category"]
        q = tc["question"]

        print(f"\n[{idx:02d}/{len(test_cases):02d}] 🔍 [{cat.upper()}] {qid}: {q[:55]}...")

        # 1. Chạy Retrieval cho Baseline
        t0 = time.time()
        raw_chunks = service.retrieve(q, top_k=7)
        base_top5 = raw_chunks[:5]

        # 2. Chạy EffectChecker & Reranking cho Effect-Aware
        enriched_chunks = service.effect_checker.check_chunks(raw_chunks)
        effect_top5 = enriched_chunks[:5]

        base_ans = ""
        eff_ans = ""

        # 3. Chạy LLM nếu bật cờ eval_llm
        if eval_llm:
            print("   ⏳ Đang gọi Gemini cho Baseline RAG...")
            base_res = service.run_baseline(q, top_k=5)
            base_ans = base_res.get("answer", "")

            # Tránh hit rate limit free tier
            time.sleep(2.0)

            print("   ⏳ Đang gọi Gemini cho Effect-Aware RAG...")
            eff_res = service.run_effect_aware(q, top_k_retrieve=7, top_k_llm=5)
            eff_ans = eff_res.get("answer", "")

            time.sleep(2.0)

        # 4. Tính toán Metrics
        metrics = calculate_metrics_for_case(
            test_case=tc,
            baseline_chunks=base_top5,
            effect_chunks=effect_top5,
            baseline_answer=base_ans,
            effect_answer=eff_ans,
        )
        results.append(metrics)

        # Log chi tiết
        detailed_logs.append({
            "test_case": tc,
            "metrics": metrics,
            "baseline_chunks_top3": [
                {"title": c["doc_title"], "dieu": c["dieu_so"], "score": c["score"]} for c in base_top5[:3]
            ],
            "effect_chunks_top3": [
                {"title": c["doc_title"], "dieu": c["dieu_so"], "level": c.get("effect_level"), "score": c["score"]}
                for c in effect_top5[:3]
            ],
            "baseline_answer": base_ans,
            "effect_answer": eff_ans,
        })

        print(f"   ↳ Baseline: Hit@3={metrics['baseline_hit@3']} | MRR={metrics['baseline_mrr']:.2f} | Outdated Chunks={metrics['baseline_outdated_in_top5']}")
        print(f"   ↳ Effect-Aware: Hit@3={metrics['effect_hit@3']} | MRR={metrics['effect_mrr']:.2f} | Danger={metrics['effect_danger_in_top5']} | Warning={metrics['effect_warning_in_top5']}")

    # ── Tổng hợp và tính trung bình ──────────────────────────────────────────
    df = pd.DataFrame(results)

    # Lưu chi tiết ra file
    summary_csv = OUTPUT_DIR / "benchmark_summary.csv"
    detailed_json = OUTPUT_DIR / "benchmark_detailed.json"

    df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    with open(detailed_json, "w", encoding="utf-8") as f:
        json.dump(detailed_logs, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 75)
    print("📊 BẢNG TỔNG HỢP KẾT QUẢ ĐÁNH GIÁ ĐỊNH LƯỢNG")
    print("=" * 75)

    categories = ["repealed_trap", "active_current", "guidance_cross_ref"]
    summary_rows = []

    for cat in categories:
        sub_df = df[df["category"] == cat]
        if len(sub_df) == 0:
            continue
        row = {
            "Nhóm câu hỏi": cat,
            "Số câu": len(sub_df),
            "Base Hit@3": f"{sub_df['baseline_hit@3'].mean() * 100:.1f}%",
            "Eff Hit@3": f"{sub_df['effect_hit@3'].mean() * 100:.1f}%",
            "Base MRR": f"{sub_df['baseline_mrr'].mean():.3f}",
            "Eff MRR": f"{sub_df['effect_mrr'].mean():.3f}",
            "Base Outdated Chunks": f"{sub_df['baseline_outdated_in_top5'].sum()}",
            "Eff Danger Flagged": f"{sub_df['effect_danger_in_top5'].sum()}",
        }
        if eval_llm:
            row["Base FactCov"] = f"{sub_df['baseline_fact_coverage'].mean() * 100:.1f}%"
            row["Eff FactCov"] = f"{sub_df['effect_fact_coverage'].mean() * 100:.1f}%"
        summary_rows.append(row)

    # Dòng Overall
    overall_row = {
        "Nhóm câu hỏi": "TỔNG THỂ (OVERALL)",
        "Số câu": len(df),
        "Base Hit@3": f"{df['baseline_hit@3'].mean() * 100:.1f}%",
        "Eff Hit@3": f"{df['effect_hit@3'].mean() * 100:.1f}%",
        "Base MRR": f"{df['baseline_mrr'].mean():.3f}",
        "Eff MRR": f"{df['effect_mrr'].mean():.3f}",
        "Base Outdated Chunks": f"{df['baseline_outdated_in_top5'].sum()}",
        "Eff Danger Flagged": f"{df['effect_danger_in_top5'].sum()}",
    }
    if eval_llm:
        overall_row["Base FactCov"] = f"{df['baseline_fact_coverage'].mean() * 100:.1f}%"
        overall_row["Eff FactCov"] = f"{df['effect_fact_coverage'].mean() * 100:.1f}%"
    summary_rows.append(overall_row)

    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    print("=" * 75)
    print(f"✅ Đã lưu kết quả tóm tắt: {summary_csv}")
    print(f"✅ Đã lưu kết quả chi tiết: {detailed_json}")

    return summary_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy benchmark hệ thống RAG pháp luật")
    parser.add_argument("--eval-llm", action="store_true", help="Bật đánh giá câu trả lời LLM Gemini (có gọi API)")
    parser.add_argument("--max-cases", type=int, default=None, help="Giới hạn số lượng câu hỏi kiểm thử")
    args = parser.parse_args()

    run_benchmark(eval_llm=args.eval_llm, max_cases=args.max_cases)
