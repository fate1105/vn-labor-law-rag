"""
GIAO DIỆN WEB CHATBOT HỎI ĐÁP PHÁP LUẬT LAO ĐỘNG VIỆT NAM (EFFECT-AWARE RAG)
Đồ án tốt nghiệp: Sinh viên Trần Tấn Phúc — D22CNTT03 | GVHD: TS. Nguyễn Trung Kiệt
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
    page_title="VN Labor Law RAG — Hỏi Đáp Pháp Luật Lao Động",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Font & Container */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header card */
    .header-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .header-box h1 {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .header-box p {
        color: #e0e7ff;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-ok { background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-warning { background-color: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .badge-danger { background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-unknown { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* Comparison column cards */
    .model-card-baseline {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #64748b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .model-card-effect {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-top: 4px solid #22c55e;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Citation box (hiển thị trọn vẹn văn bản không bị cắt chữ) */
    .citation-box {
        background-color: #f8fafc;
        border-left: 3px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #1e293b;
        margin: 8px 0 14px 0;
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* Warning alert inside answer */
    .danger-callout {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 8px 0;
        color: #991b1b;
        font-size: 0.9rem;
    }
    .warning-callout {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 8px 0;
        color: #92400e;
        font-size: 0.9rem;
    }

    /* Quick question pill */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 20px;
        font-size: 0.85rem;
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
    st.markdown("### 🎓 Đồ Án Tốt Nghiệp")
    st.markdown(
        """
        **Hệ thống hỏi đáp pháp luật lao động Việt Nam có kiểm tra hiệu lực văn bản**  
        *(Effect-Aware RAG)*
        ---
        """
    )

    st.markdown("### ⚙️ Chế độ hoạt động")
    mode = st.radio(
        "Chọn cơ chế trả lời:",
        options=[
            "🛡️ Effect-Aware RAG (Khuyên dùng)",
            "🔍 Baseline RAG (Tiêu chuẩn)",
            "⚖️ So sánh song song (Baseline vs Effect-Aware)",
        ],
        index=0,
        help="Chế độ 'Effect-Aware' có kiểm tra trạng thái hiệu lực văn bản từ đồ thị quan hệ để lọc bỏ luật cũ hoặc đưa ra cảnh báo.",
    )

    with st.expander("🛠️ Cài đặt nâng cao", expanded=False):
        model_name = st.selectbox(
            "Mô hình LLM:",
            options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"],
            index=0,
        )
        top_k_retrieve = st.slider("Top-K truy xuất FAISS:", min_value=3, max_value=12, value=7, step=1)
        top_k_llm = st.slider("Top-K đưa vào LLM:", min_value=3, max_value=7, value=5, step=1)
        temperature = st.slider("Temperature (Độ sáng tạo):", min_value=0.0, max_value=0.7, value=0.2, step=0.05)

    st.markdown("---")
    st.markdown("### 🔎 Tra cứu hiệu lực văn bản")
    with st.expander("Kiểm tra trạng thái & quan hệ văn bản", expanded=False):
        search_kw = st.text_input("Nhập ID hoặc số hiệu (VD: 45/2019, 05/2015, 38/2022):", key="doc_search_input")
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
    st.markdown("### 📊 Thống kê cơ sở tri thức")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Văn bản lọc", "800")
        st.metric("Vector chunks", "42,592")
    with col_sb2:
        st.metric("Quan hệ", "43,478")
        st.metric("Model Embed", "Bi-Encoder")

# ── Main Area Header ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="header-box">
        <h1>⚖️ Hệ Thống Hỏi Đáp Pháp Luật Lao Động Việt Nam</h1>
        <p>Tích hợp kiểm tra hiệu lực văn bản và truy vết đồ thị quan hệ pháp luật (Effect-Aware RAG)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Câu hỏi mẫu (Quick Prompts) ─────────────────────────────────────────────
st.markdown("##### 💡 Câu hỏi mẫu thường gặp:")
quick_cols = st.columns(4)

sample_questions = [
    ("💰 Lương tối thiểu", "Mức lương tối thiểu vùng hiện tại là bao nhiêu?"),
    ("⏰ Giờ làm thêm", "Người lao động được làm thêm tối đa bao nhiêu giờ trong một năm?"),
    ("🚪 Trợ cấp thôi việc", "Người lao động đơn phương chấm dứt hợp đồng lao động có được trợ cấp thôi việc không?"),
    ("🤰 Nghỉ thai sản", "Thời gian nghỉ việc hưởng chế độ thai sản của lao động nữ là bao nhiêu tuần?"),
]

for i, (label, q_text) in enumerate(sample_questions):
    with quick_cols[i]:
        if st.button(f"{label}", use_container_width=True, key=f"qp_{i}"):
            st.session_state.selected_query = q_text

# ── Khung chat / Input ───────────────────────────────────────────────────────
user_query = st.chat_input("Nhập câu hỏi của bạn về luật lao động, tiền lương, BHXH...")

# Nếu người dùng bấm câu hỏi mẫu
if st.session_state.selected_query and not user_query:
    user_query = st.session_state.selected_query
    st.session_state.selected_query = None

# ── Xử lý khi có câu hỏi ─────────────────────────────────────────────────────
if user_query:
    with st.chat_message("user"):
        st.markdown(f"**{user_query}**")

    # 1. Chế độ: SO SÁNH SONG SONG (Baseline vs Effect-Aware)
    if "So sánh" in mode:
        with st.chat_message("assistant"):
            st.markdown("### ⚖️ So sánh đối chứng kết quả giữa hai mô hình")
            with st.spinner("Đang chạy đối chứng đồng thời Baseline RAG và Effect-Aware RAG..."):
                comp = service.compare(
                    user_query,
                    top_k_retrieve=top_k_retrieve,
                    top_k_llm=top_k_llm,
                    model_name=model_name,
                )

            # Chia 2 cột so sánh
            col_base, col_eff = st.columns(2)

            with col_base:
                st.markdown(
                    """
                    <div class="model-card-baseline">
                        <h4 style="margin:0 0 8px 0; color:#334155;">🔍 1. Baseline RAG (RAG thông thường)</h4>
                        <p style="font-size:0.85rem; color:#64748b; margin:0 0 10px 0;">
                            Chỉ truy xuất theo độ tương đồng ngữ nghĩa FAISS, không kiểm tra văn bản đã hết hiệu lực hay chưa.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if comp["baseline_risky_chunks"] > 0:
                    st.markdown(
                        f"""
                        <div class="danger-callout">
                            ⚠️ <b>Cảnh báo rủi ro pháp lý:</b> Phát hiện <b>{comp['baseline_risky_chunks']}</b> đoạn trích dẫn
                            trong Baseline thuộc văn bản ĐÃ HẾT HIỆU LỰC hoặc BỊ SỬA ĐỔI nhưng vẫn được dùng để sinh câu trả lời!
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown(comp["baseline"]["answer"])
                st.caption(f"⏱️ Thời gian phản hồi: {comp['baseline']['latency']:.2f}s")

                with st.expander("📑 Các trích dẫn Baseline đã dùng (Top 5)", expanded=False):
                    for idx, c in enumerate(comp["baseline"]["chunks"], 1):
                        khoan = f", Khoản {c['khoan_so']}" if c.get("khoan_so") else ""
                        st.markdown(f"**{idx}. {c['doc_title']}** (Điều {c['dieu_so']}{khoan})")
                        st.caption(f"Score: `{c['score']:.3f}` | vbpl.vn: `{c.get('effect_status_source')}`")
                        render_citation_box(c["text"])
                        st.markdown("---")

            with col_eff:
                st.markdown(
                    """
                    <div class="model-card-effect">
                        <h4 style="margin:0 0 8px 0; color:#166534;">🛡️ 2. Effect-Aware RAG (Mô hình Đề tài)</h4>
                        <p style="font-size:0.85rem; color:#15803d; margin:0 0 10px 0;">
                            Kiểm tra hiệu lực qua đồ thị tri thức, tự động Rerank ưu tiên luật mới và cảnh báo luật lỗi thời.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                eff_res = comp["effect_aware"]
                stat_llm = eff_res["stats_llm"]
                st.markdown(
                    f"""
                    <div style="margin-bottom:8px;">
                        <span class="badge badge-ok">🟢 Còn hiệu lực: {stat_llm['OK']}</span>
                        <span class="badge badge-warning">🟡 Sửa đổi/Cảnh báo: {stat_llm['WARNING']}</span>
                        <span class="badge badge-danger">🔴 Hết hiệu lực/Thay thế: {stat_llm['DANGER']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(eff_res["answer"])
                st.caption(f"⏱️ Thời gian phản hồi: {eff_res['latency']:.2f}s")

                with st.expander("📑 Các trích dẫn Effect-Aware đã dùng (Đã Rerank)", expanded=False):
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
                        st.caption(f"Score gốc: `{c['score']:.3f}` | vbpl.vn: `{c.get('effect_status_source')}`")
                        render_citation_box(c["text"])
                        st.markdown("---")

            # Hộp phân tích đánh giá
            st.markdown("---")
            st.markdown("#### 💡 Phân tích đánh giá đối chứng")
            if comp["has_diff"]:
                st.success(
                    "✅ **Ưu thế rõ rệt của Effect-Aware RAG:** Hệ thống đã tự động nhận diện được sự thay đổi hiệu lực pháp luật. "
                    "Khác với Baseline RAG có nguy cơ trích dẫn các Nghị định/Quy định cũ mà người dùng không hề hay biết, "
                    "Effect-Aware RAG đã đẩy các văn bản còn hiệu lực lên trên và ghi nhận cảnh báo rõ ràng trong lời giải đáp."
                )
            else:
                st.info(
                    "ℹ️ Đối với câu hỏi này, các trích dẫn pháp luật được tìm thấy đều đang trong trạng thái ổn định (còn hiệu lực). "
                    "Cả hai mô hình đều đưa ra câu trả lời dựa trên cùng căn cứ pháp lý hiện hành."
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
                <div style="margin-bottom:12px;">
                    <span class="badge badge-ok">🟢 Còn hiệu lực: {stat_llm['OK']}</span>
                    <span class="badge badge-warning">🟡 Sửa đổi/Cảnh báo: {stat_llm['WARNING']}</span>
                    <span class="badge badge-danger">🔴 Bị thay thế: {stat_llm['DANGER']}</span>
                    <span class="badge badge-unknown">⚪ Chưa xác định: {stat_llm['UNKNOWN']}</span>
                    <span style="font-size:0.85rem; color:#64748b; margin-left:8px;">⏱️ {res['latency']:.2f}s</span>
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
                    st.caption(f"Mức độ tương đồng (Score): `{c['score']:.3f}` | vbpl.vn: `{c.get('effect_status_source')}`")
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
                    st.caption(f"Score: `{c['score']:.3f}` | Nguồn: vbpl.vn")
                    render_citation_box(c["text"])
                    st.markdown("---")
