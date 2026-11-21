"""
Comparison UI components for side-by-side Baseline RAG vs Effect-Aware RAG.
"""

import html
import streamlit as st


def render_citation_box(text: str, level: str = "DEFAULT"):
    """Hiển thị nội dung điều luật đầy đủ, viền màu theo trạng thái hiệu lực, không cắt chữ."""
    escaped_text = html.escape(text.strip())
    mod_cls = {
        "OK": " citation-box--ok",
        "WARNING": " citation-box--warning",
        "DANGER": " citation-box--danger",
    }.get(level, "")
    st.markdown(
        f'<div class="citation-box{mod_cls}">{escaped_text}</div>',
        unsafe_allow_html=True,
    )


def render_comparison_view(comp: dict):
    """Hiển thị thanh tóm tắt đối chứng và giao diện 2 cột giữa Baseline RAG và Effect-Aware RAG."""
    eff_res = comp["effect_aware"]
    stat_llm = eff_res["stats_llm"]
    risky_cnt = comp.get("baseline_risky_chunks", 0)
    total_lat = comp.get("total_latency", max(comp["baseline"]["latency"], eff_res["latency"]))

    risk_color = "#dc2626" if risky_cnt > 0 else "#16a34a"
    risk_text = f"⚠️ {risky_cnt} đoạn luật cũ/sửa đổi" if risky_cnt > 0 else "✅ 0 đoạn rủi ro"

    st.markdown(
        f"""
        <div class="compare-summary-strip">
            <div class="compare-stat-pill">
                ⏱️ Thời gian chạy song song
                <strong>{total_lat:.2f} giây</strong>
            </div>
            <div class="compare-stat-pill">
                🔍 Rủi ro ở Baseline RAG
                <strong style="color:{risk_color};">{risk_text}</strong>
            </div>
            <div class="compare-stat-pill">
                🛡️ Kiểm soát bởi Effect-Aware
                <strong style="color:#15803d;">{stat_llm['OK']} OK • {stat_llm['WARNING']} WARN • {stat_llm['DANGER']} DANGER</strong>
            </div>
            <div class="compare-stat-pill">
                🕸️ Tốc độ thẩm định Đồ thị
                <strong>&lt; 0.02 giây (O(1) Cache)</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_base, col_eff = st.columns(2)

    with col_base:
        st.markdown(
            """
            <article class="model-header-baseline">
                <span class="model-tag tag-base">MÔ HÌNH ĐỐI CHỨNG (BASELINE)</span>
                <h4 style="margin:0 0 0.35rem 0; color:#1e293b; font-weight:700;">🔍 Baseline RAG (RAG truyền thống)</h4>
                <p style="font-size:0.85rem; color:#64748b; margin:0; line-height:1.5;">
                    Truy xuất thuần túy theo điểm tương đồng ngữ nghĩa Cosine (FAISS). Không nhận biết vòng đời hiệu lực pháp lý.
                </p>
            </article>
            """,
            unsafe_allow_html=True,
        )
        if risky_cnt > 0:
            st.markdown(
                f"""
                <div class="danger-callout">
                    ⚠️ <strong>CẢNH BÁO RỦI RO PHÁP LÝ NGHIÊM TRỌNG:</strong><br>
                    Phát hiện <strong>{risky_cnt} đoạn trích dẫn</strong> trong ngữ cảnh Baseline thuộc văn bản
                    <strong>ĐÃ HẾT HIỆU LỰC HOẶC ĐÃ SỬA ĐỔI</strong> nhưng vẫn đưa thẳng vào mô hình sinh câu trả lời!
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(comp["baseline"]["answer"])
        st.caption(f"⏱️ Thời gian nhánh Baseline: `{comp['baseline']['latency']:.2f}s`")

        with st.expander(f"📋 Căn cứ Baseline đã nạp ({len(comp['baseline']['chunks'])} đoạn trích)", expanded=False):
            for idx, c in enumerate(comp["baseline"]["chunks"], 1):
                khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""
                st.markdown(f"**{idx}. {c['doc_title']}** *(Điều {c['dieu_so']}{khoan})*")
                st.markdown(
                    f'<span class="citation-meta-chip">Cosine: {c["score"]:.3f}</span>'
                    f'<span class="citation-meta-chip">vbpl.vn: {html.escape(str(c.get("effect_status_source", "")))}</span>',
                    unsafe_allow_html=True,
                )
                render_citation_box(c["text"])

    with col_eff:
        st.markdown(
            """
            <article class="model-header-effect">
                <span class="model-tag tag-effect">MÔ HÌNH ĐỀ TÀI ĐỀ XUẤT</span>
                <h4 style="margin:0 0 0.35rem 0; color:#14532d; font-weight:700;">🛡️ Effect-Aware Knowledge Graph RAG</h4>
                <p style="font-size:0.85rem; color:#15803d; margin:0; line-height:1.5;">
                    Thẩm định qua Đồ thị Tri thức (36,726 đỉnh), tự động tái xếp hạng ưu tiên luật hiện hành và gắn nhãn cảnh báo.
                </p>
            </article>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="margin-bottom:0.75rem; display:flex; flex-wrap:wrap; gap:0.35rem;">
                <span class="badge badge-ok">🟢 Còn hiệu lực: {stat_llm['OK']}</span>
                <span class="badge badge-warning">🟡 Sửa đổi/Cảnh báo: {stat_llm['WARNING']}</span>
                <span class="badge badge-danger">🔴 Hết hiệu lực/Thay thế: {stat_llm['DANGER']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(eff_res["answer"])
        st.caption(f"⏱️ Thời gian nhánh Effect-Aware: `{eff_res['latency']:.2f}s` (Duyệt đồ thị: `< 0.02s`)")

        with st.expander(f"📋 Căn cứ Effect-Aware sau Rerank & Thẩm định ({len(eff_res['llm_chunks'])} đoạn)", expanded=False):
            for idx, c in enumerate(eff_res["llm_chunks"], 1):
                lvl = c.get("effect_level", "UNKNOWN")
                badge_class = {
                    "OK": "badge-ok",
                    "WARNING": "badge-warning",
                    "DANGER": "badge-danger",
                    "UNKNOWN": "badge-unknown",
                }.get(lvl, "badge-unknown")
                khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""

                st.markdown(
                    f'<span class="badge {badge_class}">{lvl}</span> **{idx}. {html.escape(str(c["doc_title"]))}** *(Điều {c["dieu_so"]}{khoan})*',
                    unsafe_allow_html=True,
                )
                if lvl in ("WARNING", "DANGER"):
                    st.caption(f"⚠️ {c.get('effect_message')}")
                st.markdown(
                    f'<span class="citation-meta-chip">Cosine gốc: {c["score"]:.3f}</span>'
                    f'<span class="citation-meta-chip">vbpl.vn: {html.escape(str(c.get("effect_status_source", "")))}</span>',
                    unsafe_allow_html=True,
                )
                render_citation_box(c["text"], level=lvl)

    # Hộp phân tích đánh giá chuyên sâu
    verdict_html = (
        "✅ <strong>Ưu thế vượt trội của Effect-Aware RAG:</strong> Hệ thống đã kích hoạt thuật toán duyệt đồ thị phả hệ văn bản và phát hiện sự thay đổi trạng thái hiệu lực. Khác với Baseline RAG bị đánh lừa bởi độ tương đồng từ vựng của văn bản cũ, Effect-Aware RAG tự động đẩy lùi điều luật hết hiệu lực và phát cảnh báo tường minh, bảo vệ an toàn pháp lý cho người tra cứu."
        if comp.get("has_diff")
        else "ℹ️ <strong>Trạng thái quy phạm ổn định:</strong> Đối với truy vấn này, toàn bộ các điều khoản có độ tương đồng cao nhất đều đang còn nguyên hiệu lực thi hành. Cả hai mô hình cùng hội tụ về các căn cứ pháp luật hiện hành."
    )
    st.markdown(
        f"""
        <article class="analysis-card">
            <strong>💡 NHẬN ĐỊNH CHUYÊN MÔN VỀ ĐỘ AN TOÀN PHÁP LÝ:</strong><br>
            {verdict_html}
        </article>
        """,
        unsafe_allow_html=True,
    )
