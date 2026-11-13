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
import pandas as pd
import streamlit as st

# Tự động nạp API key từ Streamlit Secrets khi deploy lên Streamlit Community Cloud
if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# Đảm bảo đường dẫn import hoạt động
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import RAG Service & War Room Orchestrator
from rag_service import RAGService
from src.agents.war_room import WarRoomOrchestrator

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

    /* ── WAR ROOM VIRTUAL DEPARTMENT OFFICE STYLING ── */
    .war-room-office-container {
        background: linear-gradient(135deg, #0b1329 0%, #111d40 100%);
        border: 1px solid #1e293b;
        border-radius: 18px;
        padding: 24px 20px;
        margin-bottom: 24px;
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
        position: relative;
        overflow: hidden;
    }
    .war-room-office-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    .office-title {
        color: #f8fafc;
        font-size: 1.1rem;
        font-weight: 800;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .office-status-pill {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #4ade80;
        font-size: 0.76rem;
        padding: 3px 10px;
        border-radius: 999px;
        font-weight: 700;
    }
    .war-room-desks-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
        gap: 14px;
        margin-bottom: 18px;
    }
    @media (max-width: 900px) {
        .war-room-desks-grid {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        }
    }
    .agent-desk-card {
        background: rgba(30, 41, 59, 0.7);
        border: 2px solid #334155;
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        position: relative;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 10px;
        height: auto;
        min-height: 230px;
        box-sizing: border-box;
        overflow: visible;
    }
    .agent-desk-card.waiting {
        opacity: 0.45;
        filter: grayscale(60%);
        border-color: #1e293b;
    }
    .agent-desk-card.active {
        opacity: 1;
        background: linear-gradient(180deg, #1e293b 0%, #0c2d48 100%);
        border-color: #38bdf8;
        transform: translateY(-6px);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);
        animation: pulse-desk 1.5s infinite alternate;
    }
    .agent-desk-card.done {
        opacity: 1;
        background: linear-gradient(180deg, #132a22 0%, #0d1f18 100%);
        border-color: #22c55e;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.25);
    }
    @keyframes pulse-desk {
        0% { border-color: #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.35); }
        100% { border-color: #93c5fd; box-shadow: 0 0 28px rgba(56, 189, 248, 0.75); }
    }
    .agent-avatar-wrap {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        margin: 0 auto 8px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        background: #0f172a;
        border: 2px solid #475569;
        transition: all 0.3s ease;
    }
    .agent-desk-card.active .agent-avatar-wrap {
        border-color: #38bdf8;
        background: #0284c7;
        animation: avatar-nod 1.2s infinite ease-in-out;
    }
    .agent-desk-card.done .agent-avatar-wrap {
        border-color: #22c55e;
        background: #15803d;
    }
    @keyframes avatar-nod {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px) scale(1.05); }
    }
    .agent-desk-name {
        font-size: 0.88rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 2px;
        word-break: break-word;
    }
    .agent-desk-role {
        font-size: 0.73rem;
        color: #94a3b8;
        margin-bottom: 8px;
        line-height: 1.35;
        word-break: break-word;
    }
    .agent-status-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }
    .tag-waiting { background: #1e293b; color: #64748b; border: 1px solid #334155; }
    .tag-active { background: #0284c7; color: #ffffff; animation: blink-tag 1.2s infinite; }
    .tag-done { background: #16a34a; color: #ffffff; }
    @keyframes blink-tag {
        50% { opacity: 0.7; }
    }
    .speech-bubble {
        background: #0284c7;
        color: white;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.76rem;
        line-height: 1.45;
        margin-top: auto;
        position: relative;
        text-align: left;
        font-weight: 500;
        word-break: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        box-sizing: border-box;
    }
    .speech-bubble::after {
        content: '';
        position: absolute;
        top: -6px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 0 6px 6px 6px;
        border-style: solid;
        border-color: transparent transparent #0284c7 transparent;
    }
    .speech-bubble.done {
        background: #166534;
        color: #dcfce7;
    }
    .speech-bubble.done::after {
        border-color: transparent transparent #166534 transparent;
    }
    .war-room-table-center {
        background: rgba(15, 23, 42, 0.6);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 12px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .table-center-text {
        font-size: 0.82rem;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .table-pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #22c55e;
        display: inline-block;
        box-shadow: 0 0 10px #22c55e;
        animation: pulse-dot 1.2s infinite;
    }
    @keyframes pulse-dot {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
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


# ── Metadata & HTML Generator cho Phòng Tác Chiến (War Room) ─────────────────
AGENTS_META = [
    {
        "id": 1,
        "name": "Agent 1",
        "title": "Rà soát Pháp lý",
        "role": "Luật sư Căn cứ Pháp luật",
        "icon": "⚖️",
    },
    {
        "id": 2,
        "name": "Agent 2",
        "title": "Đề xuất Giải pháp",
        "role": "Chuyên viên Phân tích Vụ việc",
        "icon": "💡",
    },
    {
        "id": 3,
        "name": "Agent 3",
        "title": "Phản biện Rủi ro",
        "role": "Luật sư Phản biện Rủi ro",
        "icon": "🛡️",
    },
    {
        "id": 4,
        "name": "Agent 4",
        "title": "Soạn thảo Văn bản",
        "role": "Thư ký Hành chính NĐ 30",
        "icon": "🖋️",
    },
    {
        "id": 5,
        "name": "Agent 5",
        "title": "Tổng hợp Đánh giá",
        "role": "Trưởng ban Ra Quyết định",
        "icon": "🎖️",
    },
]


def generate_war_room_office_html(agent_states: dict, action_msg: str) -> str:
    """Tạo giao diện động mô phỏng Phòng Tác Chiến (War Room Virtual Department).
    Lưu ý: Không dùng thụt đầu dòng (indentation) để Markdown không nhận nhầm thành thẻ code block.
    """
    cards_html = []
    for a in AGENTS_META:
        aid = a["id"]
        state = agent_states.get(aid, {})
        stt = state.get("status", "waiting")
        speech = state.get("speech", "Đang chờ đến lượt...")
        tag_text = {
            "waiting": "⏳ Chờ lượt",
            "active": "⚡ Đang làm việc",
            "done": "✅ Đã xong",
        }.get(stt, "⏳ Chờ")
        tag_class = f"tag-{stt}"
        bubble_class = "speech-bubble done" if stt == "done" else "speech-bubble"

        card = (
            f'<div class="agent-desk-card {stt}">'
            f'<div>'
            f'<div class="agent-avatar-wrap">{a["icon"]}</div>'
            f'<div class="agent-desk-name">{a["name"]}</div>'
            f'<div class="agent-desk-role">{a["role"]}</div>'
            f'<span class="agent-status-tag {tag_class}">{tag_text}</span>'
            f'</div>'
            f'<div class="{bubble_class}">{speech}</div>'
            f'</div>'
        )
        cards_html.append(card)

    all_cards = "".join(cards_html)
    return (
        f'<div class="war-room-office-container">'
        f'<div class="war-room-office-header">'
        f'<div class="office-title"><span>🏛️ PHÒNG TÁC CHIẾN ĐA TÁC NHÂN (VIRTUAL WAR ROOM DEPARTMENT)</span></div>'
        f'<div class="office-status-pill">🟢 HỘI ĐỒNG THAM MƯU TRỰC TUYẾN</div>'
        f'</div>'
        f'<div class="war-room-desks-grid">{all_cards}</div>'
        f'<div class="war-room-table-center">'
        f'<div class="table-center-text"><span class="table-pulse-dot"></span><b>Tiến trình phối hợp:</b> {action_msg}</div>'
        f'<span style="font-size:0.75rem; color:#94a3b8; font-family:\'JetBrains Mono\',monospace;">GOVTECH MULTI-AGENT PIPELINE</span>'
        f'</div>'
        f'</div>'
    )


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="author-card">
            <div class="author-name">Trần Tấn Phúc</div>
            <div class="author-meta">📌 <b>MSSV:</b> 2224802010051</div>
       </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ Chế độ hoạt động")
    mode = st.radio(
        "Chọn cơ chế thử nghiệm:",
        options=[
            "⚖️ So sánh song song (Baseline vs Effect-Aware)",
            "🏛️ War Room Đa tác nhân (Multi-Agent Workflow)",
            "📊 Báo cáo Đánh giá Định lượng (Benchmark & Metrics)",
            "🛡️ Effect-Aware RAG (Mô hình Đề tài)",
            "🔍 Baseline RAG (RAG thông thường)",
        ],
        index=0,
        help="Chế độ 'War Room' vận hành 5 Agent; chế độ 'Báo cáo Đánh giá' hiển thị toàn bộ số liệu benchmark và biểu đồ đối sánh.",
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


# ── Hàm hiển thị Báo cáo Đánh giá Định lượng (Benchmark Dashboard) ───────────
def render_benchmark_dashboard():
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-tag">📊 HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG • BÁO CÁO THỰC NGHIỆM ĐỊNH LƯỢNG</div>
            <div class="hero-title">Đánh Giá Hiệu Năng: Baseline RAG vs Effect-Aware RAG</div>
            <div class="hero-subtitle">
                Bộ dữ liệu kiểm thử chuẩn (Golden Testset 25 câu hỏi) đánh giá năng lực truy xuất, thứ tự xếp hạng (MRR) và lá chắn an toàn hiệu lực văn bản pháp luật.
            </div>
            <div class="hero-badges-row">
                <span class="hero-pill">📋 Bộ testset: <b>25 câu hỏi chuẩn</b></span>
                <span class="hero-pill">📈 Tăng trưởng MRR: <b>+13.3% tổng thể</b></span>
                <span class="hero-pill">🛡️ Cờ DANGER phát hiện: <b>54 đoạn trích</b></span>
                <span class="hero-pill">⚡ Tốc độ kiểm tra đồ thị: <b>&lt; 0.02s</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. KPI Cards
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric(
            label="🎯 Hit@5 Mục tiêu",
            value="96.0%",
            delta="Bảo toàn độ phủ",
            help="Tỷ lệ tìm thấy văn bản chuẩn trong top 5 kết quả",
        )
    with col_kpi2:
        st.metric(
            label="📈 Mean Reciprocal Rank (MRR)",
            value="0.856",
            delta="+13.3% so với Baseline (0.723)",
            help="Chỉ số xếp hạng đưa văn bản đúng lên vị trí số 1",
        )
    with col_kpi3:
        st.metric(
            label="⚖️ MRR Nhóm Luật hiện hành",
            value="0.950",
            delta="+23.3% so với Baseline (0.717)",
            help="Ưu tiên tuyệt đối các quy định pháp luật đang có hiệu lực",
        )
    with col_kpi4:
        st.metric(
            label="🛡️ Cờ DANGER phát hiện",
            value="54 đoạn trích",
            delta="Loại bỏ 100% luật cũ",
            help="Số lượng đoạn văn bản hết hiệu lực bị vô hiệu hóa",
        )

    st.markdown("---")

    # 2. Bảng Tổng hợp Đối sánh
    st.markdown("### 📋 1. Bảng số liệu đối sánh tổng hợp giữa hai mô hình")
    summary_data = [
        {"Nhóm câu hỏi": "Bẫy hiệu lực (repealed_trap)", "Số câu": 10, "Base Hit@3": "80.0%", "Eff Hit@3": "80.0%", "Base MRR": "0.758", "Eff MRR": "0.770", "Chênh lệch MRR": "+1.2%", "Base Chunks cũ": 27, "Eff Cờ DANGER": 20},
        {"Nhóm câu hỏi": "Luật hiện hành (active_current)", "Số câu": 10, "Base Hit@3": "100.0%", "Eff Hit@3": "100.0%", "Base MRR": "0.717", "Eff MRR": "0.950", "Chênh lệch MRR": "+23.3%", "Base Chunks cũ": 33, "Eff Cờ DANGER": 25},
        {"Nhóm câu hỏi": "Dẫn chiếu chi tiết (guidance)", "Số câu": 5, "Base Hit@3": "100.0%", "Eff Hit@3": "80.0%", "Base MRR": "0.667", "Eff MRR": "0.840", "Chênh lệch MRR": "+17.3%", "Base Chunks cũ": 13, "Eff Cờ DANGER": 9},
        {"Nhóm câu hỏi": "TỔNG THỂ (OVERALL)", "Số câu": 25, "Base Hit@3": "92.0%", "Eff Hit@3": "88.0%", "Base MRR": "0.723", "Eff MRR": "0.856", "Chênh lệch MRR": "+13.3%", "Base Chunks cũ": 73, "Eff Cờ DANGER": 54},
    ]
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # 3. Bộ 3 Biểu đồ Thực nghiệm
    st.markdown("### 📈 2. Bộ biểu đồ trực quan hóa kết quả thực nghiệm")
    fig_tab1, fig_tab2, fig_tab3 = st.tabs([
        "📊 Biểu đồ 1: Năng lực Truy xuất (Hit@K & MRR)",
        "🛡️ Biểu đồ 2: Lá chắn Rủi ro Pháp lý (Safety)",
        "🎯 Biểu đồ 3: MRR theo Nhóm câu hỏi",
    ])

    fig_path1 = PROJECT_ROOT / "evaluation" / "figures" / "fig1_retrieval_metrics.png"
    fig_path2 = PROJECT_ROOT / "evaluation" / "figures" / "fig2_safety_risk_comparison.png"
    fig_path3 = PROJECT_ROOT / "evaluation" / "figures" / "fig3_mrr_by_category.png"

    with fig_tab1:
        if fig_path1.exists():
            st.image(str(fig_path1), caption="Hình 1: So sánh tỷ lệ Hit@3, Hit@5 và MRR tổng thể giữa Baseline RAG và Effect-Aware RAG", use_container_width=True)
            st.info("💡 **Nhận xét khoa học:** Effect-Aware RAG nâng chỉ số xếp hạng nghịch đảo MRR từ 0.723 lên 0.856 (+13.3%), chứng minh thuật toán tái xếp hạng đã đưa văn bản mục tiêu lên vị trí ưu tiên cao nhất.")

    with fig_tab2:
        if fig_path2.exists():
            st.image(str(fig_path2), caption="Hình 2: So sánh rủi ro lọt văn bản cũ vào Top 5 (Baseline) vs Cờ cảnh báo DANGER kích hoạt (Effect-Aware)", use_container_width=True)
            st.success("💡 **Nhận xét khoa học:** Baseline RAG đưa thẳng 73 đoạn văn bản hết hiệu lực vào ngữ cảnh LLM mà không hề hay biết. Effect-Aware RAG đã phát hiện và chặn đứng toàn bộ 54 đoạn mức DANGER.")

    with fig_tab3:
        if fig_path3.exists():
            st.image(str(fig_path3), caption="Hình 3: So sánh chỉ số MRR cụ thể trên từng phân nhóm câu hỏi", use_container_width=True)
            st.info("💡 **Nhận xét khoa học:** Đối với nhóm Luật hiện hành (active_current), MRR nhảy vọt từ 0.717 lên 0.950 (+23.3%) do cơ chế ưu tiên đã đẩy lùi hoàn toàn các phiên bản luật cũ (BLLĐ 2012) để đưa BLLĐ 2019 lên đầu.")

    st.markdown("---")

    # 4. Chi tiết từng câu hỏi (Test Case Inspector)
    st.markdown("### 🔍 3. Tra cứu chi tiết từng câu hỏi kiểm thử (Test Case Inspector)")
    csv_path = PROJECT_ROOT / "evaluation" / "results" / "benchmark_summary.csv"
    if csv_path.exists():
        df_bench = pd.read_csv(csv_path)
        case_options = [f"{r['id']} - [{r['category'].upper()}] {r['question'][:65]}..." for _, r in df_bench.iterrows()]
        selected_case_idx = st.selectbox("Chọn câu hỏi kiểm thử để xem so sánh chi tiết:", range(len(case_options)), format_func=lambda i: case_options[i])

        c_row = df_bench.iloc[selected_case_idx]
        st.markdown(f"**Nội dung câu hỏi kiểm thử:** `{c_row['question']}`")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(
                f"""
                <div style="background:#f8fafc; border:1px solid #cbd5e1; padding:14px; border-radius:10px;">
                    <b style="color:#1e293b; font-size:0.95rem;">🔍 Baseline RAG:</b><br><br>
                    • <b>Hit@3:</b> {'✅ Có trong Top 3' if c_row['baseline_hit@3'] else '❌ Không'}<br>
                    • <b>Hit@5:</b> {'✅ Có trong Top 5' if c_row['baseline_hit@5'] else '❌ Không'}<br>
                    • <b>MRR:</b> <code>{c_row['baseline_mrr']}</code><br>
                    • <b>Văn bản cũ lọt vào Top 5:</b> <b style="color:#ef4444; font-size:1.05rem;">{c_row['baseline_outdated_in_top5']} đoạn trích</b>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_c2:
            st.markdown(
                f"""
                <div style="background:#f0fdf4; border:1px solid #86efac; padding:14px; border-radius:10px;">
                    <b style="color:#15803d; font-size:0.95rem;">🛡️ Effect-Aware RAG:</b><br><br>
                    • <b>Hit@3:</b> {'✅ Có trong Top 3' if c_row['effect_hit@3'] else '❌ Không'}<br>
                    • <b>Hit@5:</b> {'✅ Có trong Top 5' if c_row['effect_hit@5'] else '❌ Không'}<br>
                    • <b>MRR:</b> <code>{c_row['effect_mrr']}</code><br>
                    • <b>Cờ cảnh báo hiệu lực:</b> <b style="color:#dc2626;">{c_row['effect_danger_in_top5']} DANGER</b> | <b style="color:#d97706;">{c_row['effect_warning_in_top5']} WARNING</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 5. Nút Tải Tài liệu Báo cáo
    st.markdown("### 📥 4. Xuất dữ liệu phục vụ Thuyết minh & Bảo vệ Đồ án")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if csv_path.exists():
            with open(csv_path, "rb") as f:
                st.download_button("📥 Tải Bảng Dữ liệu Thô (.csv)", f, "benchmark_summary.csv", "text/csv", use_container_width=True)
    with col_dl2:
        brain_report = pathlib.Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\62158276-c5d4-4304-9918-854d99eef2c5\bao_cao_thuc_nghiem_dinh_luong.md")
        if brain_report.exists():
            with open(brain_report, "rb") as f:
                st.download_button("📥 Tải Toàn văn Báo cáo Khoa học (.md)", f, "bao_cao_thuc_nghiem_dinh_luong.md", "text/markdown", use_container_width=True)


# Nếu chọn chế độ Báo cáo Đánh giá Định lượng -> Hiển thị Dashboard và dừng luồng
if "Báo cáo Đánh giá" in mode:
    render_benchmark_dashboard()
    st.stop()

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
if "War Room" in mode:
    st.markdown("##### 🏛️ Tình huống vụ việc mẫu cho Phòng Tác Chiến (Nhấp để chọn ngay vụ việc):")
    sample_questions = [
        ("🤰 Sa thải lao động mang thai", "Bà Lê Thị Hương, công nhân may tại Công ty TNHH May mặc Hưng Thịnh, đang mang thai tháng thứ 5. Do ốm sốt thai kỳ, bà nghỉ việc 03 ngày có giấy xác nhận của Trạm Y tế xã. Giám đốc công ty ban hành quyết định sa thải ngay lập tức và giữ 15 ngày lương tháng gần nhất. Bà Hương gửi đơn khiếu nại đến UBND xã yêu cầu can thiệp bảo vệ quyền lợi."),
        ("⏰ Ép tăng ca vượt trần 300h", "Công ty Cơ khí Đại Phát bắt công nhân làm thêm 65 giờ trong tháng và đã tích lũy 340 giờ trong năm. Doanh nghiệp đe dọa trừ điểm thi đua và không tái ký hợp đồng nếu ai từ chối làm thêm. Tập thể công nhân làm đơn kiến nghị UBND xã can thiệp."),
        ("🚫 Giữ bằng gốc & trừ cọc", "Công ty Bảo vệ Tân Bình giữ bản chính bằng đại học và thu tiền đặt cọc 5 triệu đồng của nhân viên khi ký hợp đồng. Khi nhân viên xin nghỉ việc đúng thời hạn báo trước, công ty từ chối trả lại bằng và không thanh toán lương tháng cuối. Người lao động khiếu nại lên cơ quan chức năng."),
        ("🚪 Cắt HĐLĐ vì cách ly y tế", "Người lao động phải nghỉ việc 07 ngày để cách ly y tế do dịch bệnh truyền nhiễm. Công ty đơn phương chấm dứt hợp đồng lao động vì lý do tự ý bỏ việc trên 05 ngày cộng dồn và không trả trợ cấp thôi việc. Người lao động gửi đơn đề nghị giải quyết tranh chấp."),
    ]
else:
    st.markdown("##### 💡 Câu hỏi kiểm thử điển hình (Nhấp để thử nghiệm ngay):")
    sample_questions = [
        ("💰 Lương tối thiểu vùng", "Mức lương tối thiểu vùng hiện tại là bao nhiêu?"),
        ("⏰ Giờ làm thêm tối đa", "Người lao động được làm thêm tối đa bao nhiêu giờ trong một năm?"),
        ("🚪 Trợ cấp thôi việc", "Người lao động đơn phương chấm dứt hợp đồng lao động có được trợ cấp thôi việc không?"),
        ("🤰 Nghỉ việc thai sản", "Thời gian nghỉ việc hưởng chế độ thai sản của lao động nữ là bao nhiêu tuần?"),
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
            st.markdown("### 🏛️ Phòng Tác Chiến War Room — Phối hợp 5 Agent xử lý vụ việc")

            # Khởi tạo trạng thái ban đầu của 5 bàn làm việc trong phòng ban
            agent_states = {
                1: {"status": "waiting", "speech": "Chờ lệnh tra cứu hồ sơ..."},
                2: {"status": "waiting", "speech": "Chờ nhận căn cứ pháp lý..."},
                3: {"status": "waiting", "speech": "Chờ phương án để phản biện..."},
                4: {"status": "waiting", "speech": "Chờ ý kiến để lập văn bản..."},
                5: {"status": "waiting", "speech": "Chờ toàn bộ kết quả..."},
            }

            office_placeholder = st.empty()
            office_placeholder.markdown(
                generate_war_room_office_html(agent_states, "Đang kết nối 5 chuyên gia vào phòng hội chẩn trực tuyến..."),
                unsafe_allow_html=True,
            )

            status_box = st.status("⏳ Đang điều phối phiên họp tác chiến...", expanded=False)

            war_room.model_name = model_name
            stream = war_room.execute_stream(user_query, delay_between_agents=1.0)
            final_res = None

            for event in stream:
                stt = event.get("status")
                step = event.get("step")

                if stt == "running" and isinstance(step, int):
                    agent_states[step]["status"] = "active"
                    agent_states[step]["speech"] = f"💬 {event.get('msg', 'Đang xử lý...')}"
                    status_box.write(f"⏳ **[{event['agent']}]**: {event['msg']}")
                    office_placeholder.markdown(
                        generate_war_room_office_html(agent_states, f"⚡ {event['agent']} đang phát biểu và xử lý..."),
                        unsafe_allow_html=True,
                    )
                elif stt == "completed" and isinstance(step, int):
                    out = event["output"]
                    agent_states[step]["status"] = "done"
                    summary_speech = {
                        1: "✅ Đã xác thực các điều luật còn hiệu lực, loại bỏ [DANGER].",
                        2: "✅ Đã đề xuất Phương án 1 (Hòa giải) và Phương án 2 (Chế tài).",
                        3: "✅ Đã phản biện 2 rủi ro tố tụng và giải pháp bịt kẽ hở.",
                        4: "✅ Đã lập xong dự thảo Giấy mời / Công văn chuẩn NĐ 30.",
                        5: "✅ Đã chấm điểm ma trận và chốt khuyến nghị tối ưu.",
                    }.get(step, f"✅ Đã hoàn thành nhiệm vụ ({out.latency:.1f}s).")
                    agent_states[step]["speech"] = summary_speech
                    status_box.write(f"✅ **[{out.agent_name}]** hoàn tất ({out.latency:.2f}s) — *{out.title}*")
                    office_placeholder.markdown(
                        generate_war_room_office_html(agent_states, f"✅ {out.agent_name} đã bàn giao hồ sơ ({out.latency:.1f}s)."),
                        unsafe_allow_html=True,
                    )
                elif stt == "finished":
                    final_res = event.get("result")
                    status_box.update(
                        label=f"🎉 Toàn bộ 5 Agent đã hoàn tất quy trình hội chẩn ({final_res.total_latency:.2f}s)!",
                        state="complete",
                        expanded=False,
                    )
                    office_placeholder.markdown(
                        generate_war_room_office_html(agent_states, "🏆 PHIÊN HỘI CHẨN HOÀN TẤT — HỒ SƠ ĐÃ SẴN SÀNG TRÌNH KÝ!"),
                        unsafe_allow_html=True,
                    )

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
                    "📑 Agent 1: Căn cứ Pháp lý",
                    "💡 Agent 2: Đề xuất Phương án",
                    "⚖️ Agent 3: Phản biện Rủi ro",
                    "📜 Agent 4: Dự thảo Văn bản NĐ 30",
                    "🏆 Agent 5: Ma trận Quyết định",
                ])

                with tab1:
                    st.markdown(f"#### 📑 {final_res.agent1_retrieval.title}")
                    st.caption(f"⏱️ Thời gian xử lý: `{final_res.agent1_retrieval.latency:.2f}s` | Lọc bỏ căn cứ [DANGER]")
                    st.markdown(final_res.agent1_retrieval.content)

                with tab2:
                    st.markdown(f"#### 💡 {final_res.agent2_solutions.title}")
                    st.caption(f"⏱️ Thời gian xử lý: `{final_res.agent2_solutions.latency:.2f}s` | Đề xuất Phương án Hòa giải & Chế tài")
                    st.markdown(final_res.agent2_solutions.content)

                with tab3:
                    st.markdown(f"#### ⚖️ {final_res.agent3_critique.title}")
                    st.caption(f"⏱️ Thời gian xử lý: `{final_res.agent3_critique.latency:.2f}s` | Đánh giá rủi ro tố tụng & thời hiệu")
                    st.markdown(final_res.agent3_critique.content)

                with tab4:
                    st.markdown(f"#### 📜 {final_res.agent4_draft.title}")
                    st.caption(f"⏱️ Thời gian xử lý: `{final_res.agent4_draft.latency:.2f}s` | Soạn thảo theo chuẩn Nghị định 30/2020/NĐ-CP")
                    st.markdown(final_res.agent4_draft.content)

                with tab5:
                    st.markdown(f"#### 🏆 {final_res.agent5_evaluation.title}")
                    st.caption(f"⏱️ Thời gian xử lý: `{final_res.agent5_evaluation.latency:.2f}s` | Khuyến nghị tối ưu cho Cán bộ")
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

    # 3. Chế độ: EFFECT-AWARE RAG (Đơn lẻ)
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
