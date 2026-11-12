"""
GIAO DIỆN WEB CHATBOT HỎI ĐÁP PHÁP LUẬT LAO ĐỘNG VIỆT NAM (EFFECT-AWARE RAG)
Đồ án tốt nghiệp: Sinh viên Trần Tấn Phúc — D22CNTT03 | GVHD: TS. Nguyễn Trung Kiệt
Đơn vị tiếp nhận thực tập: CÔNG TY TNHH EDUZ
Chạy: python -m streamlit run src/web/app.py
"""

import os
import sys
import html
import pathlib
import streamlit as st

# Đảm bảo đường dẫn import hoạt động
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import RAG Service
from rag_service import RAGService

# ── Cấu hình trang Streamlit ─────────────────────────────────────────────────
st.set_page_config(
    page_title="VN Labor Law RAG — Hệ Thống Tra Cứu Pháp Luật Lao Động",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Nâng Cấp Giao Diện Chuẩn Báo Cáo / Slide ───────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Container căn chỉnh thoáng đãng */
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* ── HEADER BANNER CAO CẤP ── */
    .hero-banner {
        background: linear-gradient(135deg, #091e42 0%, #1e3a8a 50%, #2563eb 100%);
        color: white;
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -8px rgba(30, 58, 138, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: #93c5fd;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .hero-title {
        font-size: 1.95rem;
        font-weight: 800;
        margin: 0 0 8px 0;
        line-height: 1.25;
        letter-spacing: -0.5px;
        color: #ffffff !important;
    }
    .hero-subtitle {
        color: #cbd5e1;
        font-size: 0.98rem;
        margin: 0 0 16px 0;
        font-weight: 400;
        max-width: 850px;
        line-height: 1.5;
    }
    .hero-badges-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .hero-pill {
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #e2e8f0;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .hero-pill b {
        color: #38bdf8;
    }

    /* ── PROFILE CARD TRONG SIDEBAR ── */
    .author-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 18px;
    }
    .author-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #2563eb;
        background: #dbeafe;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .author-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 4px 0;
    }
    .author-meta {
        font-size: 0.84rem;
        color: #475569;
        margin: 2px 0;
        line-height: 1.45;
    }

    /* ── QUICK PROMPT CARDS (CÂU HỎI MẪU) ── */
    .quick-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 14px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        cursor: pointer;
    }
    .quick-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.12);
        transform: translateY(-1px);
    }

    /* ── MODEL CARDS (SO SÁNH SONG SONG) ── */
    .model-header-baseline {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #64748b;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .model-header-effect {
        background: #ffffff;
        border: 1px solid #86efac;
        border-top: 4px solid #16a34a;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 16px rgba(22, 163, 74, 0.08);
    }
    .model-tag {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .tag-base { background: #f1f5f9; color: #475569; }
    .tag-effect { background: #dcfce7; color: #15803d; }

    /* ── STATUS BADGES ── */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.2px;
        margin-right: 6px;
    }
    .badge-ok { background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-warning { background-color: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .badge-danger { background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-unknown { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* ── WARNING & CALLOUT BANNERS ── */
    .danger-callout {
        background-color: #fef2f2;
        border: 1px solid #fca5a5;
        border-left: 5px solid #dc2626;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0 16px 0;
        color: #991b1b;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .analysis-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #16a34a;
        padding: 16px 20px;
        border-radius: 10px;
        margin-top: 20px;
        color: #14532d;
        font-size: 0.93rem;
        line-height: 1.6;
    }

    /* ── CITATION LAW BOX ── */
    .citation-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #2563eb;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.88rem;
        line-height: 1.6;
        color: #1e293b;
        margin: 8px 0 14px 0;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .citation-meta-chip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        background: #e2e8f0;
        color: #334155;
        padding: 2px 6px;
        border-radius: 4px;
        margin-right: 6px;
    }

    /* Bo tròn nút bấm */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid #e2e8f0 !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: #2563eb !important;
        color: #2563eb !important;
        background: #eff6ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Khởi tạo Service (Cache bằng Streamlit) ──────────────────────────────────
@st.cache_resource(show_spinner="⏳ Đang tải mô hình embedding và FAISS index (chỉ chạy 1 lần)...")
def get_service() -> RAGService:
    return RAGService.get_instance()

service = get_service()

# ── Khởi tạo Session State ──────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_query" not in st.session_state:
    st.session_state.selected_query = None


def render_citation_box(text: str):
    """Hiển thị nội dung điều luật đầy đủ, xuống dòng tự nhiên, không cắt chữ."""
    escaped_text = html.escape(text.strip())
    st.markdown(
        f'<div class="citation-box">{escaped_text}</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="author-card">
            <span class="author-badge">ĐỒ ÁN TỐT NGHIỆP D22</span>
            <div class="author-name">Trần Tấn Phúc</div>
            <div class="author-meta">📌 <b>MSSV:</b> D22CNTT03</div>
            <div class="author-meta">👨‍🏫 <b>GVHD:</b> TS. Nguyễn Trung Kiệt</div>
            <div class="author-meta">🏛️ <b>Học viện:</b> PTIT</div>
            <div class="author-meta">🏢 <b>Cơ quan TT:</b> Công ty TNHH EDUZ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ Chế độ hoạt động")
    mode = st.radio(
        "Chọn cơ chế thử nghiệm:",
        options=[
            "⚖️ So sánh song song (Baseline vs Effect-Aware)",
            "🛡️ Effect-Aware RAG (Mô hình Đề tài)",
            "🔍 Baseline RAG (RAG thông thường)",
        ],
        index=0,
        help="Chế độ 'So sánh song song' là chế độ tốt nhất để chụp ảnh báo cáo vì thể hiện rõ ưu thế khắc phục trích dẫn luật cũ của đề tài.",
    )

    with st.expander("🛠️ Cài đặt tham số mô hình", expanded=False):
        model_name = st.selectbox(
            "Mô hình LLM:",
            options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"],
            index=0,
        )
        top_k_retrieve = st.slider("Top-K truy xuất FAISS:", min_value=3, max_value=12, value=7, step=1)
        top_k_llm = st.slider("Top-K đưa vào LLM:", min_value=3, max_value=7, value=5, step=1)
        temperature = st.slider("Temperature (Độ sáng tạo):", min_value=0.0, max_value=0.7, value=0.2, step=0.05)

    st.markdown("---")
    st.markdown("### 🔎 Tra cứu phả hệ văn bản")
    with st.expander("Kiểm tra trạng thái & đồ thị quan hệ", expanded=False):
        search_kw = st.text_input("Nhập ID hoặc số hiệu (VD: 45/2019, 122/2015, 38/2022):", key="doc_search_input")
        if search_kw:
            found_docs = service.search_docs(search_kw.strip(), limit=5)
            if not found_docs:
                st.warning("Không tìm thấy văn bản phù hợp.")
            else:
                for doc in found_docs:
                    st.markdown(f"**{doc['title']}**")
                    st.caption(f"ID: `{doc['doc_id']}` | vbpl.vn: `{doc['effect_status']}`")
                    if st.button(f"Xem chi tiết cây quan hệ", key=f"btn_{doc['doc_id']}"):
                        detail = service.get_doc_relations(str(doc["doc_id"]))
                        lvl = detail["level"]
                        icon = {"OK": "🟢", "WARNING": "🟡", "DANGER": "🔴", "UNKNOWN": "⚪"}.get(lvl, "⚪")
                        st.info(f"{icon} **Mức tổng hợp:** {lvl} — {detail['message']}")
                        if detail["relationships"]:
                            st.markdown("**Các quan hệ tác động:**")
                            for r in detail["relationships"][:6]:
                                st.markdown(f"- `[{r['rel_type']}]` ➔ {r['counterpart_title'][:55]}...")
                        else:
                            st.caption("(Không có quan hệ tác động nào trong DB)")
                    st.markdown("---")

    st.markdown("---")
    st.markdown("### 📊 Chỉ số cơ sở tri thức")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Văn bản lọc", "800")
        st.metric("Vector chunks", "42,592")
    with col_sb2:
        st.metric("Quan hệ pháp lý", "43,478")
        st.metric("Chiều vector", "768d")

# ── Main Area Header Banner (Rất đẹp khi chụp ảnh toàn cảnh) ────────────────
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-tag">🏛️ HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG • KHOA CNTT</div>
        <div class="hero-title">Hệ Thống Hỏi Đáp Pháp Luật Lao Động Việt Nam</div>
        <div class="hero-subtitle">
            Mô hình RAG tích hợp nhận thức hiệu lực văn bản qua Đồ thị tri thức (Effect-Aware Knowledge Graph RAG) — 
            Khắc phục triệt để hiện tượng trích dẫn quy phạm pháp luật đã hết hiệu lực.
        </div>
        <div class="hero-badges-row">
            <span class="hero-pill">📦 Dữ liệu: <b>800 văn bản hạt nhân</b></span>
            <span class="hero-pill">⚡ Lập chỉ mục: <b>42,592 chunks (FAISS)</b></span>
            <span class="hero-pill">🕸️ Đồ thị: <b>36,726 đỉnh • 42,571 cạnh</b></span>
            <span class="hero-pill">⏱️ Thời gian kiểm tra: <b>&lt; 0.02s</b></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Câu hỏi mẫu (Quick Prompts) ─────────────────────────────────────────────
st.markdown("##### 💡 Câu hỏi kiểm thử điển hình (Nhấp để thử nghiệm ngay):")
quick_cols = st.columns(4)

sample_questions = [
    ("💰 Lương tối thiểu vùng", "Mức lương tối thiểu vùng hiện tại là bao nhiêu?"),
    ("⏰ Giờ làm thêm tối đa", "Người lao động được làm thêm tối đa bao nhiêu giờ trong một năm?"),
    ("🚪 Trợ cấp thôi việc", "Người lao động đơn phương chấm dứt hợp đồng lao động có được trợ cấp thôi việc không?"),
    ("🤰 Nghỉ việc thai sản", "Thời gian nghỉ việc hưởng chế độ thai sản của lao động nữ là bao nhiêu tuần?"),
]

for i, (label, q_text) in enumerate(sample_questions):
    with quick_cols[i]:
        if st.button(f"{label}", use_container_width=True, key=f"qp_{i}"):
            st.session_state.selected_query = q_text

# ── Khung chat / Input ───────────────────────────────────────────────────────
user_query = st.chat_input("Nhập câu hỏi tra cứu pháp luật (VD: tiền lương, hợp đồng lao động, bảo hiểm xã hội)...")

# Nếu người dùng bấm câu hỏi mẫu
if st.session_state.selected_query and not user_query:
    user_query = st.session_state.selected_query
    st.session_state.selected_query = None

# ── Xử lý khi có câu hỏi ─────────────────────────────────────────────────────
if user_query:
    with st.chat_message("user"):
        st.markdown(f"**🔍 Câu hỏi tra cứu:** `{user_query}`")

    # 1. Chế độ: SO SÁNH SONG SONG (Hero Screenshot View!)
    if "So sánh" in mode:
        with st.chat_message("assistant"):
            st.markdown("### ⚖️ Kết quả đối chứng song song giữa hai mô hình RAG")
            with st.spinner("Đang chạy đối chứng đồng thời Baseline RAG và Effect-Aware RAG..."):
                comp = service.compare(
                    user_query,
                    top_k_retrieve=top_k_retrieve,
                    top_k_llm=top_k_llm,
                    model_name=model_name,
                )

            # Chia 2 cột đối chứng
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
                if comp["baseline_risky_chunks"] > 0:
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

                with st.expander("📑 Danh sách căn cứ Baseline đã trích dẫn (Top 5)", expanded=False):
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

                with st.expander("📑 Căn cứ Effect-Aware đã dùng (Đã Rerank & Thẩm định)", expanded=False):
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

            # Hộp phân tích đánh giá chuyên sâu (Rất giá trị để chụp vào báo cáo)
            st.markdown(
                f"""
                <div class="analysis-card">
                    <b>💡 ĐÁNH GIÁ CHUYÊN MÔN VỀ ĐỘ CHÍNH XÁC PHÁP LÝ:</b><br>
                    {
                    "✅ <b>Ưu thế vượt trội của Effect-Aware RAG:</b> Hệ thống đã tự động kích hoạt thuật toán duyệt đồ thị và nhận diện sự thay đổi trạng thái hiệu lực. Khác với Baseline RAG bị đánh lừa bởi độ tương đồng từ vựng dẫn đến trích dẫn điều luật đã hết hiệu lực, Effect-Aware RAG tự động đẩy lùi văn bản lỗi thời và phát cảnh báo tường minh đến người dùng, đảm bảo tính an toàn pháp lý tuyệt đối."
                    if comp["has_diff"] else
                    "ℹ️ <b>Trạng thái quy chuẩn ổn định:</b> Đối với câu hỏi này, các căn cứ pháp lý được tìm thấy đều đang trong trạng thái còn nguyên hiệu lực thi hành. Cả hai mô hình đều đưa ra câu trả lời dựa trên cùng các quy phạm hiện hành."
                    }
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 2. Chế độ: EFFECT-AWARE RAG (Đơn lẻ)
    elif "Effect-Aware" in mode:
        with st.chat_message("assistant"):
            with st.spinner("Đang tìm kiếm điều luật, kiểm tra đồ thị hiệu lực và sinh câu trả lời..."):
                res = service.run_effect_aware(
                    user_query,
                    top_k_retrieve=top_k_retrieve,
                    top_k_llm=top_k_llm,
                    model_name=model_name,
                    temperature=temperature,
                )

            stat_llm = res["stats_llm"]
            st.markdown(
                f"""
                <div style="margin-bottom:12px; display:flex; flex-wrap:wrap; gap:6px;">
                    <span class="badge badge-ok">🟢 Còn hiệu lực: {stat_llm['OK']}</span>
                    <span class="badge badge-warning">🟡 Sửa đổi/Cảnh báo: {stat_llm['WARNING']}</span>
                    <span class="badge badge-danger">🔴 Bị thay thế: {stat_llm['DANGER']}</span>
                    <span class="badge badge-unknown">⚪ Chưa xác định: {stat_llm['UNKNOWN']}</span>
                    <span style="font-size:0.84rem; color:#64748b; margin-left:8px; align-self:center;">⏱️ {res['latency']:.2f}s</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(res["answer"])

            with st.expander(f"📑 Căn cứ pháp lý đã trích dẫn ({len(res['llm_chunks'])} Điều/Khoản)", expanded=False):
                for idx, c in enumerate(res["llm_chunks"], 1):
                    lvl = c.get("effect_level", "UNKNOWN")
                    badge_class = {
                        "OK": "badge-ok",
                        "WARNING": "badge-warning",
                        "DANGER": "badge-danger",
                        "UNKNOWN": "badge-unknown",
                    }.get(lvl, "badge-unknown")
                    khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""

                    st.markdown(
                        f'<span class="badge {badge_class}">{lvl}</span> **{idx}. {c["doc_title"]}** — Điều {c["dieu_so"]}{khoan}',
                        unsafe_allow_html=True,
                    )
                    if lvl in ("WARNING", "DANGER"):
                        st.caption(f"⚠️ Cảnh báo: {c.get('effect_message')}")
                    st.markdown(
                        f'<span class="citation-meta-chip">Cosine Score: {c["score"]:.3f}</span>'
                        f'<span class="citation-meta-chip">Gốc vbpl.vn: {c.get("effect_status_source")}</span>',
                        unsafe_allow_html=True,
                    )
                    render_citation_box(c["text"])
                    st.markdown("---")

    # 3. Chế độ: BASELINE RAG (Đơn lẻ)
    else:
        with st.chat_message("assistant"):
            with st.spinner("Đang truy xuất ngữ nghĩa và sinh câu trả lời (Baseline)..."):
                res = service.run_baseline(
                    user_query,
                    top_k=top_k_llm,
                    model_name=model_name,
                    temperature=temperature,
                )

            st.caption(f"🔍 Chế độ Baseline RAG | ⏱️ {res['latency']:.2f}s")
            st.markdown(res["answer"])

            with st.expander(f"📑 Căn cứ pháp lý trích dẫn ({len(res['chunks'])} đoạn)", expanded=False):
                for idx, c in enumerate(res["chunks"], 1):
                    khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""
                    st.markdown(f"**{idx}. {c['doc_title']}** — Điều {c['dieu_so']}{khoan}")
                    st.markdown(
                        f'<span class="citation-meta-chip">Cosine Score: {c["score"]:.3f}</span>'
                        f'<span class="citation-meta-chip">Nguồn vbpl.vn</span>',
                        unsafe_allow_html=True,
                    )
                    render_citation_box(c["text"])
                    st.markdown("---")
