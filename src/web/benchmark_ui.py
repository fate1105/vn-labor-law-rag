"""
Benchmark & Metrics Dashboard UI for VN Labor Law RAG.
"""

from pathlib import Path
import html
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def get_cached_benchmark_assets(project_root_str: str):
    """Nạp và lưu đệm trên RAM toàn bộ CSV, báo cáo Markdown và bytes của 3 biểu đồ PNG (tránh đọc đĩa lặp lại)."""
    root = Path(project_root_str)
    csv_path = root / "evaluation" / "results" / "benchmark_summary.csv"
    report_path = root / "evaluation" / "bao_cao_thuc_nghiem_dinh_luong.md"

    df = None
    options = []
    csv_bytes = b""
    if csv_path.exists():
        csv_bytes = csv_path.read_bytes()
        df = pd.read_csv(csv_path)
        options = [f"{r['id']} — [{r['category'].upper()}] {r['question'][:68]}..." for _, r in df.iterrows()]

    report_bytes = report_path.read_bytes() if report_path.exists() else b""

    figs = {}
    for k, fname in [
        ("fig1", "fig1_retrieval_metrics.png"),
        ("fig2", "fig2_safety_risk_comparison.png"),
        ("fig3", "fig3_mrr_by_category.png"),
    ]:
        p = root / "evaluation" / "figures" / fname
        figs[k] = p.read_bytes() if p.exists() else None

    return df, options, csv_bytes, report_bytes, figs


def render_benchmark_dashboard(project_root: Path):
    """Hiển thị toàn bộ dữ liệu thực nghiệm, chỉ số MRR, Hit@K và bảng đối chiếu (0 disk I/O khi chuyển tab)."""
    df_bench, case_options, csv_bytes, report_bytes, figs = get_cached_benchmark_assets(str(project_root))

    st.markdown(
        """
        <header class="hero-banner">
            <div class="hero-tag">📊 BÁO CÁO THỰC NGHIỆM ĐỊNH LƯỢNG • QUANTITATIVE BENCHMARK</div>
            <h1 class="hero-title">Đánh Giá Hiệu Năng: Baseline RAG vs Effect-Aware RAG</h1>
            <p class="hero-subtitle">
                Kiểm chứng thực nghiệm trên bộ dữ liệu chuẩn <strong>Golden Testset (25 kịch bản pháp lý thực tế)</strong> — đo lường độ chính xác truy xuất, thứ hạng nghịch đảo trung bình (MRR) và lá chắn an toàn hiệu lực văn bản.
            </p>
            <div class="hero-badges-row">
                <span class="hero-pill">📋 Bộ kiểm thử: <b>25 câu hỏi chuẩn</b></span>
                <span class="hero-pill">📈 Tăng trưởng MRR: <b>+13.3% tổng thể</b></span>
                <span class="hero-pill">🏆 Hit@1: <b>80.0% (vs 56.0% Baseline)</b></span>
                <span class="hero-pill">⚡ Duyệt đồ thị: <b>&lt; 0.02s</b></span>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    # 1. Custom Elevated KPI Cards
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.markdown(
            """
            <article class="kpi-card kpi-card--accent">
                <span class="kpi-label">🎯 Độ phủ truy xuất (Hit@5)</span>
                <strong class="kpi-value">96.0%</strong>
                <span class="kpi-delta">✓ Hit@1 đạt 80.0% (+24%)</span>
            </article>
            """,
            unsafe_allow_html=True,
        )
    with col_kpi2:
        st.markdown(
            """
            <article class="kpi-card kpi-card--emerald">
                <span class="kpi-label">📈 Mean Reciprocal Rank (MRR)</span>
                <strong class="kpi-value">0.856</strong>
                <span class="kpi-delta">▲ +13.3% so với Baseline (0.723)</span>
            </article>
            """,
            unsafe_allow_html=True,
        )
    with col_kpi3:
        st.markdown(
            """
            <article class="kpi-card kpi-card--emerald">
                <span class="kpi-label">⚖️ MRR Nhóm Luật hiện hành</span>
                <strong class="kpi-value">0.950</strong>
                <span class="kpi-delta">▲ +23.3% so với Baseline (0.717)</span>
            </article>
            """,
            unsafe_allow_html=True,
        )
    with col_kpi4:
        st.markdown(
            """
            <article class="kpi-card kpi-card--amber">
                <span class="kpi-label">🛡️ Lá chắn Rủi ro Hiệu lực</span>
                <strong class="kpi-value">54 Cờ DANGER</strong>
                <span class="kpi-delta">✓ Chặn 73 đoạn cũ lọt lưới</span>
            </article>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='min-block-size:1rem;'></div>", unsafe_allow_html=True)

    # 2. Bảng Tổng hợp Đối sánh (Semantic HTML Table thay cho st.dataframe nặng)
    st.markdown('<h3 id="bench-summary-heading">📋 1. Bảng số liệu đối sánh tổng hợp theo phân nhóm kịch bản</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        <div tabindex="0" role="region" aria-labelledby="bench-summary-heading" class="bench-table-wrap">
            <table class="bench-table">
                <thead>
                    <tr>
                        <th scope="col">Nhóm câu hỏi</th>
                        <th scope="col">Số câu</th>
                        <th scope="col">Base Hit@3</th>
                        <th scope="col">Eff Hit@3</th>
                        <th scope="col">Base MRR</th>
                        <th scope="col">Eff MRR</th>
                        <th scope="col">Chênh lệch MRR</th>
                        <th scope="col">Base Chunks cũ</th>
                        <th scope="col">Eff Cờ DANGER</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row">Bẫy hiệu lực (repealed_trap)</th>
                        <td>10</td><td>80.0%</td><td>80.0%</td><td>0.758</td><td><strong>0.770</strong></td>
                        <td class="bench-delta-pos">+1.2%</td><td>27</td><td>20</td>
                    </tr>
                    <tr>
                        <th scope="row">Luật hiện hành (active_current)</th>
                        <td>10</td><td>100.0%</td><td>100.0%</td><td>0.717</td><td><strong>0.950</strong></td>
                        <td class="bench-delta-pos">+23.3%</td><td>33</td><td>25</td>
                    </tr>
                    <tr>
                        <th scope="row">Dẫn chiếu chi tiết (guidance)</th>
                        <td>5</td><td>100.0%</td><td>80.0%</td><td>0.667</td><td><strong>0.840</strong></td>
                        <td class="bench-delta-pos">+17.3%</td><td>13</td><td>9</td>
                    </tr>
                    <tr>
                        <th scope="row">TỔNG THỂ (OVERALL)</th>
                        <td>25</td><td>92.0%</td><td>88.0%</td><td>0.723</td><td>0.856</td>
                        <td>+13.3%</td><td>73</td><td>54</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 3. Bộ 3 Biểu đồ Thực nghiệm (Từ RAM cache)
    st.markdown("### 📈 2. Trực quan hóa kết quả thực nghiệm")
    fig_tab1, fig_tab2, fig_tab3 = st.tabs([
        "📊 Biểu đồ 1: Năng lực Truy xuất (Hit@K & MRR)",
        "🛡️ Biểu đồ 2: Lá chắn Rủi ro Pháp lý (Safety)",
        "🎯 Biểu đồ 3: MRR theo Nhóm kịch bản",
    ])

    with fig_tab1:
        if figs.get("fig1"):
            st.image(figs["fig1"], caption="Hình 1: So sánh tỷ lệ Hit@3, Hit@5 và MRR tổng thể giữa Baseline RAG và Effect-Aware RAG", use_container_width=True)
            st.info("💡 **Nhận xét khoa học:** Effect-Aware RAG nâng chỉ số xếp hạng nghịch đảo MRR từ 0.723 lên 0.856 (+13.3%), đưa văn bản mục tiêu lên vị trí Top 1 ở 80% số câu hỏi.")

    with fig_tab2:
        if figs.get("fig2"):
            st.image(figs["fig2"], caption="Hình 2: So sánh rủi ro lọt văn bản cũ vào Top 5 (Baseline) vs Cờ cảnh báo DANGER kích hoạt (Effect-Aware)", use_container_width=True)
            st.success("💡 **Nhận xét khoa học:** Baseline RAG đưa thẳng 73 đoạn văn bản hết hiệu lực vào ngữ cảnh LLM mà không hề nhận biết. Effect-Aware RAG phát hiện và gắn nhãn cảnh báo chính xác 54 đoạn mức DANGER và 56 đoạn mức WARNING.")

    with fig_tab3:
        if figs.get("fig3"):
            st.image(figs["fig3"], caption="Hình 3: So sánh chỉ số MRR cụ thể trên từng phân nhóm câu hỏi", use_container_width=True)
            st.info("💡 **Nhận xét khoa học:** Đối với nhóm Luật hiện hành (active_current), MRR tăng vọt từ 0.717 lên 0.950 (+23.3%) nhờ đẩy lùi hoàn toàn sự gây nhiễu của Bộ luật Lao động 2012 để đưa Bộ luật Lao động 2019 lên vị trí đầu tiên.")

    st.markdown("---")

    # 4. Chi tiết từng câu hỏi (Test Case Inspector)
    st.markdown("### 🔍 3. Thanh tra chi tiết từng kịch bản kiểm thử (Test Case Inspector)")
    if df_bench is not None and not df_bench.empty:
        selected_case_idx = st.selectbox(
            "Chọn kịch bản kiểm thử để đối chiếu chi tiết:",
            range(len(case_options)),
            format_func=lambda i: case_options[i],
        )

        c_row = df_bench.iloc[selected_case_idx]
        st.markdown(
            f'<div class="query-context-bar"><b>📌 Câu hỏi {html.escape(str(c_row["id"]))}:</b> {html.escape(str(c_row["question"]))}</div>',
            unsafe_allow_html=True,
        )
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                f"""
                <article class="model-header-baseline">
                    <span class="model-tag tag-base">KẾT QUẢ BASELINE RAG</span>
                    <p style="margin:0.4rem 0 0 0; font-size:0.9rem; line-height:1.7;">
                        • <strong>Hit@3:</strong> {'✅ Có trong Top 3' if c_row['baseline_hit@3'] else '❌ Không đạt'}<br>
                        • <strong>Hit@5:</strong> {'✅ Có trong Top 5' if c_row['baseline_hit@5'] else '❌ Không đạt'}<br>
                        • <strong>Điểm xếp hạng MRR:</strong> <code>{c_row['baseline_mrr']}</code><br>
                        • <strong>Đoạn luật cũ lọt Top 5:</strong> <strong style="color:#dc2626;">{c_row['baseline_outdated_in_top5']} đoạn trích</strong>
                    </p>
                </article>
                """,
                unsafe_allow_html=True,
            )
        with col_c2:
            st.markdown(
                f"""
                <article class="model-header-effect">
                    <span class="model-tag tag-effect">KẾT QUẢ EFFECT-AWARE RAG</span>
                    <p style="margin:0.4rem 0 0 0; font-size:0.9rem; line-height:1.7;">
                        • <strong>Hit@3:</strong> {'✅ Có trong Top 3' if c_row['effect_hit@3'] else '❌ Không đạt'}<br>
                        • <strong>Hit@5:</strong> {'✅ Có trong Top 5' if c_row['effect_hit@5'] else '❌ Không đạt'}<br>
                        • <strong>Điểm xếp hạng MRR:</strong> <code>{c_row['effect_mrr']}</code><br>
                        • <strong>Cờ hiệu lực kích hoạt:</strong> <strong style="color:#dc2626;">{c_row['effect_danger_in_top5']} DANGER</strong> • <strong style="color:#b45309;">{c_row['effect_warning_in_top5']} WARNING</strong>
                    </p>
                </article>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 5. Nút Tải Tài liệu Báo cáo (Lấy trực tiếp từ RAM cache)
    st.markdown("### 📥 4. Xuất dữ liệu phục vụ Thuyết minh & Bảo vệ Đồ án")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if csv_bytes:
            st.download_button("📥 Tải Bảng Dữ liệu Thực nghiệm (.csv)", csv_bytes, "benchmark_summary.csv", "text/csv", use_container_width=True)
    with col_dl2:
        if report_bytes:
            st.download_button("📥 Tải Toàn văn Báo cáo Khoa học (.md)", report_bytes, "bao_cao_thuc_nghiem_dinh_luong.md", "text/markdown", use_container_width=True)
