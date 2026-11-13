"""
SCRIPT VẼ BIỂU ĐỒ BÁO CÁO THỰC NGHIỆM ĐỒ ÁN TỐT NGHIỆP
Vẽ các biểu đồ trực quan hóa so sánh Baseline RAG vs Effect-Aware RAG từ kết quả benchmark.
"""

import json
import sys
import io
import pathlib

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS_CSV = PROJECT_ROOT / "evaluation" / "results" / "benchmark_summary.csv"
DETAILED_JSON = PROJECT_ROOT / "evaluation" / "results" / "benchmark_detailed.json"
FIG_DIR = PROJECT_ROOT / "evaluation" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình font và style cho biểu đồ học thuật
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def plot_retrieval_metrics(df: pd.DataFrame):
    """Biểu đồ 1: So sánh Hit@3, Hit@5 và MRR giữa hai mô hình."""
    metrics = ["Hit@3", "Hit@5", "MRR"]
    base_vals = [
        df["baseline_hit@3"].mean() * 100,
        df["baseline_hit@5"].mean() * 100,
        df["baseline_mrr"].mean() * 100,
    ]
    eff_vals = [
        df["effect_hit@3"].mean() * 100,
        df["effect_hit@5"].mean() * 100,
        df["effect_mrr"].mean() * 100,
    ]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    rects1 = ax.bar(x - width/2, base_vals, width, label="Baseline RAG", color="#6c757d", alpha=0.9)
    rects2 = ax.bar(x + width/2, eff_vals, width, label="Effect-Aware RAG", color="#1b4965", alpha=0.95)

    ax.set_ylabel("Tỷ lệ (%) / Điểm số quy đổi (%)", fontsize=11, fontweight="bold")
    ax.set_title("So sánh năng lực truy xuất và xếp hạng (Retrieval & Ranking)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 110)
    ax.legend(frameon=True, facecolor="#f8f9fa", edgecolor="none")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Hiển thị số liệu trên đỉnh cột
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    out_path = FIG_DIR / "fig1_retrieval_metrics.png"
    plt.savefig(out_path)
    plt.close()
    print(f"✅ Đã lưu: {out_path}")


def plot_safety_risk(df: pd.DataFrame):
    """Biểu đồ 2: So sánh rủi ro trích dẫn văn bản hết hiệu lực (Safety Risk)."""
    categories = ["repealed_trap", "active_current", "guidance_cross_ref"]
    cat_names = ["Bẫy hết hiệu lực\n(Repealed Trap)", "Luật hiện hành\n(Active Law)", "Dẫn chiếu/Chi tiết\n(Guidance)"]

    base_outdated = []
    eff_danger = []

    for cat in categories:
        sub = df[df["category"] == cat]
        base_outdated.append(sub["baseline_outdated_in_top5"].sum())
        eff_danger.append(sub["effect_danger_in_top5"].sum())

    x = np.arange(len(cat_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    rects1 = ax.bar(x - width/2, base_outdated, width, label="Văn bản cũ bị đưa vào top 5 (Baseline)", color="#d90429", alpha=0.85)
    rects2 = ax.bar(x + width/2, eff_danger, width, label="Văn bản hết hiệu lực được phát hiện (Effect-Aware)", color="#2b9348", alpha=0.9)

    ax.set_ylabel("Số lượng đoạn trích (Chunks)", fontsize=11, fontweight="bold")
    ax.set_title("Năng lực phát hiện và cảnh báo rủi ro pháp lý theo từng nhóm câu hỏi", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_names, fontsize=10, fontweight="bold")
    ax.legend(frameon=True, facecolor="#f8f9fa", edgecolor="none")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for rect in rects1:
        h = rect.get_height()
        if h > 0:
            ax.annotate(f"{int(h)} chunks", xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for rect in rects2:
        h = rect.get_height()
        if h > 0:
            ax.annotate(f"{int(h)} cờ cảnh báo", xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    out_path = FIG_DIR / "fig2_safety_risk_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"✅ Đã lưu: {out_path}")


def plot_mrr_by_category(df: pd.DataFrame):
    """Biểu đồ 3: So sánh chỉ số xếp hạng MRR (Mean Reciprocal Rank) theo từng nhóm câu hỏi."""
    categories = ["repealed_trap", "active_current", "guidance_cross_ref"]
    cat_labels = ["Bẫy hết hiệu lực\n(Repealed Trap)", "Luật hiện hành\n(Active Law)", "Dẫn chiếu/Chi tiết\n(Guidance)"]

    base_mrr = [df[df["category"] == c]["baseline_mrr"].mean() for c in categories]
    eff_mrr = [df[df["category"] == c]["effect_mrr"].mean() for c in categories]

    # Thêm cột tổng thể
    cat_labels.append("TỔNG THỂ\n(OVERALL)")
    base_mrr.append(df["baseline_mrr"].mean())
    eff_mrr.append(df["effect_mrr"].mean())

    x = np.arange(len(cat_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    rects1 = ax.bar(x - width/2, base_mrr, width, label="Baseline RAG (FAISS thuần)", color="#adb5bd", alpha=0.9)
    rects2 = ax.bar(x + width/2, eff_mrr, width, label="Effect-Aware RAG (Tái xếp hạng theo hiệu lực)", color="#0077b6", alpha=0.95)

    ax.set_ylabel("Mean Reciprocal Rank (MRR)", fontsize=11, fontweight="bold")
    ax.set_title("Chỉ số xếp hạng văn bản chuẩn (MRR) - Tái xếp hạng đưa văn bản đúng lên đầu", fontsize=12, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.legend(frameon=True, facecolor="#f8f9fa", edgecolor="none", loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.3f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.3f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#03045e")

    plt.tight_layout()
    out_path = FIG_DIR / "fig3_mrr_by_category.png"
    plt.savefig(out_path)
    plt.close()
    print(f"✅ Đã lưu: {out_path}")


def main():
    if not RESULTS_CSV.exists():
        print(f"❌ Chưa có dữ liệu benchmark tại {RESULTS_CSV}. Hãy chạy run_benchmark.py trước!")
        return

    df = pd.read_csv(RESULTS_CSV)
    print(f"📈 Đang tạo biểu đồ từ {len(df)} mẫu thử nghiệm...")
    plot_retrieval_metrics(df)
    plot_safety_risk(df)
    plot_mrr_by_category(df)
    print("🎉 Hoàn tất tạo tất cả biểu đồ báo cáo!")


if __name__ == "__main__":
    main()
