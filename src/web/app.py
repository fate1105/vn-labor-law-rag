"""
GIAO DIỆN WEB CHATBOT HỎI ĐÁP PHÁP LUẬT LAO ĐỘNG VIỆT NAM (EFFECT-AWARE RAG)
Đồ án tốt nghiệp: Sinh viên Trần Tấn Phúc — D22CNTT03 | GVHD: TS. Nguyễn Trung Kiệt
Chạy: python -m streamlit run src/web/app.py
"""

import os
import sys
import html
import pathlib
import warnings
import logging
import copy
import time
import pandas as pd
import streamlit as st

os.environ["TRANSFORMERS_VERBOSITY"] = "critical"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
warnings.filterwarnings("ignore", message=".*HF_TOKEN.*")
logging.getLogger("transformers").setLevel(logging.CRITICAL)
logging.getLogger("sentence_transformers").setLevel(logging.CRITICAL)
logging.getLogger("huggingface_hub").setLevel(logging.CRITICAL)

# Tự động nạp API key từ Streamlit Secrets khi deploy lên Streamlit Community Cloud
try:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets and not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Đảm bảo đường dẫn import hoạt động
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import RAG Service, War Room Orchestrator và các UI Module đã tách gọn
from rag_service import RAGService
from src.agents.war_room import WarRoomOrchestrator
from ui_styles import CUSTOM_CSS
from war_room_ui import render_office, extract_case_dialogue_updates, format_a4_html
from benchmark_ui import render_benchmark_dashboard

# ── Cấu hình trang Streamlit ─────────────────────────────────────────────────
st.set_page_config(
    page_title="VN Labor Law RAG — Hệ Thống Tra Cứu Pháp Luật Lao Động",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Nâng Cấp Giao Diện ───────────────────────────────────────────
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Khởi tạo Service (Cache bằng Streamlit) ──────────────────────────────────
@st.cache_resource(show_spinner="⏳ Đang tải mô hình embedding và FAISS index (chỉ chạy 1 lần)...")
def get_service() -> RAGService:
    return RAGService.get_instance()

service = get_service()

@st.cache_resource(show_spinner=False)
def get_war_room() -> WarRoomOrchestrator:
    return WarRoomOrchestrator(rag_service=service)

war_room = get_war_room()

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
            <div class="author-name">Trần Tấn Phúc</div>
       </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Chế độ hoạt động")
    mode = st.radio(
        "Chọn cơ chế thử nghiệm:",
        options=[
            "🏛️ War Room Đa tác nhân (Multi-Agent Workflow)",
            "⚖️ So sánh song song (Baseline vs Effect-Aware)",
            "📊 Báo cáo Đánh giá Định lượng (Benchmark & Metrics)",
        ],
        index=0,
        help="'War Room' vận hành 5 Agent AI phối hợp xử lý vụ việc; 'So sánh song song' đối chứng trực quan 2 mô hình; 'Báo cáo Đánh giá' hiển thị toàn bộ số liệu benchmark.",
    )

    with st.expander("🛠️ Cài đặt tham số mô hình", expanded=False):
        model_name = st.selectbox(
            "Mô hình LLM:",
            options=["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"],
            index=0,
            help="gemini-3.5-flash có hạn mức quota cao và thời gian phản hồi nhanh nhất.",
        )
        top_k_retrieve = st.slider("Top-K truy xuất FAISS:", min_value=3, max_value=12, value=7, step=1)
        top_k_llm = st.slider("Top-K đưa vào LLM:", min_value=3, max_value=7, value=5, step=1)
        temperature = st.slider("Temperature (Độ sáng tạo):", min_value=0.0, max_value=0.7, value=0.2, step=0.05)

    st.markdown("---")
    st.markdown("### Tra cứu phả hệ văn bản")
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
                    if st.button("Xem chi tiết cây quan hệ", key=f"btn_{doc['doc_id']}"):
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
    st.markdown("### Chỉ số cơ sở tri thức")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Văn bản lọc", "800")
        st.metric("Vector chunks", "42,592")
    with col_sb2:
        st.metric("Quan hệ pháp lý", "43,478")
        st.metric("Chiều vector", "768d")
    st.markdown(
        """
        <div style="font-size:0.78rem; color:#475569; line-height:1.5; margin-top:10px; padding:8px 10px; background:#f1f5f9; border-radius:8px; border:1px solid #e2e8f0;">
            🤗 <b>Dataset:</b> <a href="https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents" target="_blank" style="color:#2563eb; text-decoration:none; font-weight:600;"><code>th1nhng0/vietnamese-legal-documents</code></a><br>
            🏛️ <b>Nguồn gốc:</b> vbpl.vn (Bộ Tư pháp)<br>
            ⚡ <b>Embedding:</b> <code>vietnamese-bi-encoder</code> (768d)
        </div>
        """,
        unsafe_allow_html=True,
    )


# Nếu chọn chế độ Báo cáo Đánh giá Định lượng -> Hiển thị Dashboard và dừng luồng
if "Báo cáo Đánh giá" in mode:
    render_benchmark_dashboard(PROJECT_ROOT)
    st.stop()

# ── Main Area Header Banner ──────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">Hệ Thống Hỏi Đáp Pháp Luật Lao Động Việt Nam</div>
        <div class="hero-subtitle">
            Hỗ trợ tra cứu &amp; tham mưu xử lý tranh chấp theo <b>Bộ luật Lao động 2019</b> (Dữ liệu quy phạm pháp luật cập nhật tính đến hết năm <b>2024</b>).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Câu hỏi mẫu (Quick Prompts) ─────────────────────────────────────────────
if "War Room" in mode:
    st.markdown("##### Tình huống vụ việc mẫu (Nhấp để chọn):")
    sample_questions = [
        ("Sa thải lao động mang thai", "Bà Lê Thị Hương, công nhân may tại Công ty TNHH May mặc Hưng Thịnh, đang mang thai tháng thứ 5. Do ốm sốt thai kỳ, bà nghỉ việc 03 ngày có giấy xác nhận của Trạm Y tế xã. Giám đốc công ty ban hành quyết định sa thải ngay lập tức và giữ 15 ngày lương tháng gần nhất. Bà Hương gửi đơn khiếu nại đến UBND xã yêu cầu can thiệp bảo vệ quyền lợi."),
        ("Ép tăng ca vượt trần 300h", "Công ty Cơ khí Đại Phát bắt công nhân làm thêm 65 giờ trong tháng và đã tích lũy 340 giờ trong năm. Doanh nghiệp đe dọa trừ điểm thi đua và không tái ký hợp đồng nếu ai từ chối làm thêm. Tập thể công nhân làm đơn kiến nghị UBND xã can thiệp."),
        ("Giữ bằng gốc & trừ cọc", "Công ty Bảo vệ Tân Bình giữ bản chính bằng đại học và thu tiền đặt cọc 5 triệu đồng của nhân viên khi ký hợp đồng. Khi nhân viên xin nghỉ việc đúng thời hạn báo trước, công ty từ chối trả lại bằng và không thanh toán lương tháng cuối. Người lao động khiếu nại lên cơ quan chức năng."),
        ("Cắt HĐLĐ vì cách ly y tế", "Người lao động phải nghỉ việc 07 ngày để cách ly y tế do dịch bệnh truyền nhiễm. Công ty đơn phương chấm dứt hợp đồng lao động vì lý do tự ý bỏ việc trên 05 ngày cộng dồn và không trả trợ cấp thôi việc. Người lao động gửi đơn đề nghị giải quyết tranh chấp."),
    ]
else:
    st.markdown("##### Câu hỏi kiểm thử điển hình (Nhấp để thử nghiệm):")
    sample_questions = [
        ("Lương tối thiểu vùng", "Mức lương tối thiểu vùng hiện tại là bao nhiêu?"),
        ("Giờ làm thêm tối đa", "Người lao động được làm thêm tối đa bao nhiêu giờ trong một năm?"),
        ("Trợ cấp thôi việc", "Người lao động đơn phương chấm dứt hợp đồng lao động có được trợ cấp thôi việc không?"),
        ("Nghỉ việc thai sản", "Thời gian nghỉ việc hưởng chế độ thai sản của lao động nữ là bao nhiêu tuần?"),
    ]

quick_cols = st.columns(4)
for i, (label, q_text) in enumerate(sample_questions):
    with quick_cols[i]:
        if st.button(f"{label}", use_container_width=True, key=f"qp_{i}"):
            st.session_state.selected_query = q_text

# ── Khung chat / Input ───────────────────────────────────────────────────────
input_placeholder = "Mô tả vụ việc tranh chấp, khiếu nại hoặc công văn cần xử lý..." if "War Room" in mode else "Nhập câu hỏi tra cứu pháp luật (VD: tiền lương, hợp đồng lao động, bảo hiểm xã hội)..."
user_query = st.chat_input(input_placeholder)

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

    # 2. Chế độ: WAR ROOM ĐA TÁC NHÂN (Multi-Agent System)
    elif "War Room" in mode:
        with st.chat_message("assistant"):
            st.markdown("### Phòng Tác Chiến War Room — Phối hợp 5 Agent xử lý vụ việc")

            # Khởi tạo trạng thái ban đầu của 5 bàn làm việc trong phòng ban
            agent_states = {
                1: {"status": "waiting", "speech": "Chờ lệnh tra cứu hồ sơ..."},
                2: {"status": "waiting", "speech": "Chờ nhận căn cứ pháp lý..."},
                3: {"status": "waiting", "speech": "Chờ phương án để phản biện..."},
                4: {"status": "waiting", "speech": "Chờ ý kiến để lập văn bản..."},
                5: {"status": "waiting", "speech": "Chờ toàn bộ kết quả..."},
            }

            summary_speech_map = {
                1: "✅ Đã xác thực căn cứ pháp lý còn hiệu lực, loại bỏ điều luật cũ.",
                2: "✅ Đã đề xuất Phương án 1 (Hòa giải) và Phương án 2 (Chế tài hành chính).",
                3: "⚔️ Đã phản biện 2 rủi ro tố tụng & đề xuất giải pháp bịt kín kẽ hở.",
                4: "📄 Đã lập xong Dự thảo Công văn / Giấy mời làm việc chuẩn NĐ 30.",
                5: "🏆 Đã hoàn tất ma trận MCDA và khuyến nghị phương án tối ưu.",
            }
            SCENE_BY_STEP = {1: "search", 2: "consult2", 3: "debate3", 4: "consult4", 5: "report"}
            SCENE_SECONDS = {1: 9, 2: 10, 3: 14, 4: 10, 5: 11}   # thời lượng tối thiểu của mỗi cảnh
            HANDOFF_SECONDS = 5.2                                  # đi + trò chuyện + đi về
            scene_t0 = 0.0

            # Kịch bản hội thoại động thích ứng theo kết quả thực tế của vụ án (0 token)
            case_dialogue = {
                "handoff": [
                    ["Em gửi căn cứ pháp lý nhé!",      "Đã nhận, em lập phương án ngay 👀"],
                    ["Đây là các phương án xử lý.",      "Nhận rồi, để em soi kẽ hở 🔎"],
                    ["Phản biện xong, nhờ soạn văn bản.","OK, em soạn theo mẫu NĐ 30 ✍️"],
                    ["Dự thảo xong, trình Trưởng ban.",  "Đã nhận. Tôi sẽ chấm ma trận ⚖️"],
                ],
                "consult2": [
                    [1, "Căn cứ này áp dụng được cho vụ việc chứ?"],
                    [0, "Được, còn hiệu lực. Điều khoản cũ đã bị loại."],
                    [1, "Tuyệt! Em lập 2 phương án theo căn cứ đó."]
                ],
                "debate3": [
                    [2, "Phương án 1 chưa tính tới thời hiệu khiếu nại!"],
                    [1, "Em đã nêu thời hạn xử lý ở bước 2 rồi mà."],
                    [2, "Vẫn hở: thiếu chứng cứ xác nhận y tế!"],
                    [1, "Ok, em bổ sung vào phương án."],
                    [2, "Tốt. Ký nháy nhé ✍️"]
                ],
                "consult4": [
                    [3, "Rủi ro nào bắt buộc nêu trong công văn?"],
                    [2, "Thời hiệu và chứng cứ. Ghi rõ nhé."],
                    [3, "Rõ. Em soạn theo mẫu NĐ 30."]
                ],
                "finale": [
                    "Căn cứ pháp lý: đã loại điều luật hết hiệu lực ✔",
                    "2 phương án xử lý đã sẵn sàng ✔",
                    "Rủi ro tố tụng đã được bịt kẽ hở ✔",
                    "Dự thảo công văn chuẩn NĐ 30 đã xong ✔",
                    "Tôi phê duyệt! Chốt phương án tối ưu 🎖️"
                ]
            }

            office_placeholder = st.empty()
            prev = copy.deepcopy(agent_states)
            render_office(office_placeholder, agent_states, "Đang kết nối 5 chuyên gia vào phòng làm việc...", prev, case_lines=case_dialogue)

            status_box = st.status("⏳ Đang điều phối phiên họp tác chiến...", expanded=False)

            war_room.model_name = model_name
            stream = war_room.execute_stream(user_query, delay_between_agents=0.0)
            final_res = None

            for event in stream:
                stt = event.get("status")
                step = event.get("step")

                if stt == "running" and isinstance(step, int):
                    agent_states[step]["status"] = "active"
                    if step == 3:
                        agent_states[step]["speech"] = "Đang phản biện các lỗ hổng của phương án Agent 2..."
                        action_title = "AGENT 3 đang tranh luận & phân tích rủi ro..."
                    elif step == 2:
                        agent_states[step]["speech"] = "Đang khoanh vùng vi phạm & thiết kế 2 phương án xử lý..."
                        action_title = "AGENT 2 đang thuyết trình các phương án xử lý vụ việc..."
                    elif step == 1:
                        agent_states[step]["speech"] = "Đang tra cứu cơ sở dữ liệu pháp luật và loại bỏ điều luật [DANGER]..."
                        action_title = "AGENT 1 đang rà soát căn cứ pháp luật hiện hành..."
                    elif step == 4:
                        agent_states[step]["speech"] = "Đang lập dự thảo văn bản công vụ chuẩn Nghị định 30/2020/NĐ-CP..."
                        action_title = "AGENT 4 đang soạn thảo văn bản hành chính NĐ 30..."
                    else:
                        agent_states[step]["speech"] = "Đang chấm điểm ma trận so sánh đa tiêu chí và chốt giải pháp..."
                        action_title = "AGENT 5 đang chủ trì ma trận đánh giá & ra quyết định..."

                    status_box.write(f"⏳ **[{event['agent']}]**: {event['msg']}")
                    scene_t0 = time.time()
                    render_office(office_placeholder, agent_states, action_title, prev,
                                  scene=SCENE_BY_STEP.get(step), case_lines=case_dialogue)

                elif stt == "completed" and isinstance(step, int):
                    out = event["output"]
                    # Cập nhật lời thoại động bám sát kết quả thực tế của Agent (0 token)
                    case_dialogue = extract_case_dialogue_updates(step, out, case_dialogue)

                    # nếu LLM trả lời nhanh hơn cảnh diễn thì chờ cho cảnh diễn xong
                    time.sleep(max(0.0, SCENE_SECONDS.get(step, 0) - (time.time() - scene_t0)))
                    prev = copy.deepcopy(agent_states)
                    agent_states[step]["status"] = "done"

                    # Hiển thị tóm tắt thực tế trên thẻ bàn Agent
                    dyn_speech = case_dialogue["finale"][step - 1] if step <= len(case_dialogue["finale"]) else ""
                    agent_states[step]["speech"] = dyn_speech if dyn_speech else summary_speech_map.get(step, f"Hoàn thành ({out.latency:.1f}s)")
                    status_box.write(f"✅ **[{out.agent_name}]** hoàn tất ({out.latency:.2f}s) — *{out.title}*")
                    if step < 5:
                        render_office(office_placeholder, agent_states,
                                      f"🚶 {out.agent_name} mang hồ sơ sang bàn kế tiếp...", prev, case_lines=case_dialogue)
                        time.sleep(HANDOFF_SECONDS)
                    else:
                        render_office(office_placeholder, agent_states, f"✅ {out.agent_name} đã duyệt xong.", prev, case_lines=case_dialogue)
                        time.sleep(1.0)

                elif stt == "finished":
                    final_res = event.get("result")
                    status_box.update(
                        label=f"🎉 Toàn bộ 5 Agent đã hoàn tất quy trình hội chẩn ({final_res.total_latency:.2f}s)!",
                        state="complete", expanded=False)
                    render_office(office_placeholder, agent_states,
                                  "🏆 PHIÊN LÀM VIỆC HOÀN TẤT — ĐANG HỌP CHỐT HỒ SƠ...", prev, scene="finale", case_lines=case_dialogue)

            if final_res:
                st.markdown(
                    f"""
                    <div style="background:#f0fdf4; border:1px solid #86efac; border-left:4px solid #16a34a; padding:12px 18px; border-radius:8px; margin-bottom:18px;">
                        <b>🏛️ KẾT QUẢ HỘI CHẨN ĐA TÁC NHÂN (WAR ROOM):</b> Tiến trình xử lý khép kín hoàn tất trong <b>{final_res.total_latency:.2f} giây</b> qua 5 chuyên gia AI.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Agent 1: Căn cứ Pháp lý",
                    "Agent 2: Đề xuất Phương án",
                    "Agent 3: Phản biện Rủi ro",
                    "Agent 4: Dự thảo NĐ 30",
                    "Agent 5: Ma trận Quyết định",
                ])

                with tab1:
                    st.markdown(f"#### {final_res.agent1_retrieval.title}")
                    st.caption(f"Thời gian: `{final_res.agent1_retrieval.latency:.2f}s` | Lọc bỏ căn cứ [DANGER]")
                    st.markdown(final_res.agent1_retrieval.content)

                with tab2:
                    st.markdown(f"#### {final_res.agent2_solutions.title}")
                    st.caption(f"Thời gian: `{final_res.agent2_solutions.latency:.2f}s` | Đề xuất Phương án Hòa giải & Chế tài")
                    st.markdown(final_res.agent2_solutions.content)

                with tab3:
                    st.markdown(f"#### {final_res.agent3_critique.title}")
                    st.caption(f"Thời gian: `{final_res.agent3_critique.latency:.2f}s` | Đánh giá rủi ro tố tụng & thời hiệu")
                    st.markdown(final_res.agent3_critique.content)

                with tab4:
                    st.markdown(f"#### {final_res.agent4_draft.title}")
                    st.caption(f"Thời gian: `{final_res.agent4_draft.latency:.2f}s` | Soạn thảo theo chuẩn Nghị định 30/2020/NĐ-CP")
                    st.markdown(
                        f"""
                        <div class="a4-document-container">
                            <div style="text-align:center; margin-bottom:14px;">
                                <span class="a4-doc-badge">📜 DỰ THẢO VĂN BẢN CÔNG VỤ • CHUẨN THỂ THỨC NGHỊ ĐỊNH 30/2020/NĐ-CP</span>
                            </div>
                            <div class="a4-paper-sheet">
                                {format_a4_html(final_res.agent4_draft.content)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with tab5:
                    st.markdown(f"#### {final_res.agent5_evaluation.title}")
                    st.caption(f"Thời gian: `{final_res.agent5_evaluation.latency:.2f}s` | Khuyến nghị tối ưu cho Cán bộ")
                    st.markdown(final_res.agent5_evaluation.content)

                st.markdown("---")
                # Nút tải toàn bộ hồ sơ
                full_doc = f"# HỒ SƠ TƯ VẤN & THAM MƯU XỬ LÝ VỤ VIỆC PHÁP LÝ\n" \
                           f"**Hệ thống AI Đa tác nhân (War Room Multi-Agent System)**\n\n" \
                           f"## I. TÌNH HUỐNG / VỤ VIỆC ĐẦU VÀO\n{final_res.case_description}\n\n" \
                           f"## II. CĂN CỨ PHÁP LÝ HIỆN HÀNH (AGENT 1)\n{final_res.agent1_retrieval.content}\n\n" \
                           f"## III. PHÂN TÍCH & CÁC PHƯƠNG ÁN XỬ LÝ (AGENT 2)\n{final_res.agent2_solutions.content}\n\n" \
                           f"## IV. BÁO CÁO PHẢN BIỆN RỦI RO & KHẮC PHỤC (AGENT 3)\n{final_res.agent3_critique.content}\n\n" \
                           f"## V. DỰ THẢO VĂN BẢN CÔNG VỤ (AGENT 4)\n{final_res.agent4_draft.content}\n\n" \
                           f"## VI. MA TRẬN ĐÁNH GIÁ & KHUYẾN NGHỊ RA QUYẾT ĐỊNH (AGENT 5)\n{final_res.agent5_evaluation.content}\n"

                st.download_button(
                    label="📥 Tải toàn bộ Hồ sơ Tham mưu Tư vấn (.md)",
                    data=full_doc,
                    file_name="ho_so_tham_muu_war_room.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
else:
    # Trạng thái chờ ban đầu (khi chưa nhập câu hỏi)
    if "War Room" in mode:
        st.markdown("### Phòng Tác Chiến War Room (5 Chuyên gia AI)")
        idle_states = {
            1: {"status": "waiting", "speech": "Chờ lệnh tra cứu hồ sơ..."},
            2: {"status": "waiting", "speech": "Chờ nhận căn cứ pháp lý..."},
            3: {"status": "waiting", "speech": "Chờ phương án để phản biện..."},
            4: {"status": "waiting", "speech": "Chờ ý kiến để lập văn bản..."},
            5: {"status": "waiting", "speech": "Chờ toàn bộ kết quả..."},
        }
        standby_ph = st.empty()
        render_office(
            standby_ph,
            idle_states,
            "Phòng tác chiến đang ở trạng thái trực ban — Vui lòng nhấp chọn tình huống mẫu phía trên hoặc nhập vụ việc bên dưới để bắt đầu hội chẩn.",
        )
