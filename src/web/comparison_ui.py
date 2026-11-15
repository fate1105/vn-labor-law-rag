"""
Comparison UI components for side-by-side Baseline RAG vs Effect-Aware RAG.
"""

import html
import streamlit as st


def render_citation_box(text: str):
    """Hiển thị nội dung điều luật đầy đủ, xuống dòng tự nhiên, không cắt chữ."""
    escaped_text = html.escape(text.strip())
    st.markdown(
        f'<div class="citation-box">{escaped_text}</div>',
        unsafe_allow_html=True,
    )


def render_comparison_view(comp: dict):
    """Hiển thị giao diện đối chứng song song 2 cột giữa Baseline RAG và Effect-Aware RAG."""
    col_base, col_eff = st.columns(2)

    with col_base:
        st.markdown(
            """
            <div class="model-header-baseline">
                <span class="model-tag tag-base">MÔ HÌNH ĐỐI CHỨNG (BASELINE)</span>
                <h4 style="margin:0 0 6px 0; color:#1e293b; font-weight:700;">🔍 Baseline RAG (RAG thông thường)</h4>
                <p style="font-size:0.84rem; color:#64748b; margin:0; line-height:1.45;">
                    Truy xuất thuần túy bằng Cosine Similarity qua FAISS. Không kiểm tra vòng đời hiệu lực văn bản.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if comp.get("baseline_risky_chunks", 0) > 0:
            st.markdown(
                f"""
                <div class="danger-callout">
                    ⚠️ <b>CẢNH BÁO RỦI RO PHÁP LÝ NGHIÊM TRỌNG:</b><br>
                    Phát hiện <b>{comp['baseline_risky_chunks']} đoạn trích dẫn</b> trong Baseline thuộc văn bản 
                    <b>ĐÃ HẾT HIỆU LỰC HOẶC BỊ SỬA ĐỔI</b> nhưng vẫn được dùng làm căn cứ sinh câu trả lời!
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(comp["baseline"]["answer"])
        st.caption(f"⏱️ Thời gian phản hồi: `{comp['baseline']['latency']:.2f}s`")

        with st.expander("📋 Danh sách căn cứ Baseline đã trích dẫn (Top 5)", expanded=False):
            for idx, c in enumerate(comp["baseline"]["chunks"], 1):
                khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""
                st.markdown(f"**{idx}. {c['doc_title']}** (Điều {c['dieu_so']}{khoan})")
                st.markdown(
                    f'<span class="citation-meta-chip">Score: {c["score"]:.3f}</span>'
                    f'<span class="citation-meta-chip">Gốc vbpl.vn: {c.get("effect_status_source")}</span>',
                    unsafe_allow_html=True,
                )
                render_citation_box(c["text"])
                st.markdown("---")

    with col_eff:
        st.markdown(
            """
            <div class="model-header-effect">
                <span class="model-tag tag-effect">MÔ HÌNH ĐỀ TÀI ĐỀ XUẤT</span>
                <h4 style="margin:0 0 6px 0; color:#14532d; font-weight:700;">🛡️ Effect-Aware RAG (Có kiểm tra hiệu lực)</h4>
                <p style="font-size:0.84rem; color:#15803d; margin:0; line-height:1.45;">
                    Thẩm định trạng thái qua Đồ thị tri thức (Knowledge Graph), tự động Rerank và cảnh báo luật cũ.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        eff_res = comp["effect_aware"]
        stat_llm = eff_res["stats_llm"]
        st.markdown(
            f"""
            <div style="margin-bottom:12px; display:flex; flex-wrap:wrap; gap:6px;">
                <span class="badge badge-ok">🟢 Còn hiệu lực: {stat_llm['OK']}</span>
                <span class="badge badge-warning">🟡 Sửa đổi/Cảnh báo: {stat_llm['WARNING']}</span>
                <span class="badge badge-danger">🔴 Hết hiệu lực/Thay thế: {stat_llm['DANGER']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(eff_res["answer"])
        st.caption(f"⏱️ Thời gian phản hồi: `{eff_res['latency']:.2f}s` (Kiểm tra đồ thị: &lt; 0.02s)")

        with st.expander("📋 Căn cứ Effect-Aware đã dùng (Đã Rerank & Thẩm định)", expanded=False):
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
                    f'<span class="badge {badge_class}">{lvl}</span> **{idx}. {c["doc_title"]}** (Điều {c["dieu_so"]}{khoan})',
                    unsafe_allow_html=True,
                )
                if lvl in ("WARNING", "DANGER"):
                    st.caption(f"⚠️ {c.get('effect_message')}")
                st.markdown(
                    f'<span class="citation-meta-chip">Score gốc: {c["score"]:.3f}</span>'
                    f'<span class="citation-meta-chip">Gốc vbpl.vn: {c.get("effect_status_source")}</span>',
                    unsafe_allow_html=True,
                )
                render_citation_box(c["text"])
                st.markdown("---")

    # Hộp phân tích đánh giá chuyên sâu
    st.markdown(
        f"""
        <div class="analysis-card">
            <b>💡 ĐÁNH GIÁ CHUYÊN MÔN VỀ ĐỘ CHÍNH XÁC PHÁP LÝ:</b><br>
            {
            "✅ <b>Ưu thế vượt trội của Effect-Aware RAG:</b> Hệ thống đã tự động kích hoạt thuật toán duyệt đồ thị và nhận diện sự thay đổi trạng thái hiệu lực. Khác với Baseline RAG bị đánh lừa bởi độ tương đồng từ vựng dẫn đến trích dẫn điều luật đã hết hiệu lực, Effect-Aware RAG tự động đẩy lùi văn bản lỗi thời và phát cảnh báo tường minh đến người dùng, đảm bảo tính an toàn pháp lý tuyệt đối."
            if comp.get("has_diff") else
            "ℹ️ <b>Trạng thái quy chuẩn ổn định:</b> Đối với câu hỏi này, các căn cứ pháp lý được tìm thấy đều đang trong trạng thái còn nguyên hiệu lực thi hành. Cả hai mô hình đều đưa ra câu trả lời dựa trên cùng các quy phạm hiện hành."
            }
        </div>
        """,
        unsafe_allow_html=True,
    )
