"""
Styles and CSS configuration for VN Labor Law RAG Web UI.
"""

CUSTOM_CSS = """
<style>
html, body, .stApp {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
    margin: 0;
    font-weight: 400;
    max-width: 850px;
    line-height: 1.55;
}
.hero-subtitle b {
    color: #93c5fd;
}
.hero-badges-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.hero-scope {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.48);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-left: 3.5px solid #38bdf8;
    color: #e2e8f0;
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 0.83rem;
    line-height: 1.45;
    margin-top: 12px;
}
.hero-scope b {
    color: #38bdf8;
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

/* ── PHÒNG HỘI CHẨN & TRANH LUẬN ĐA TÁC NHÂN (VIRTUAL BOARDROOM) ── */
.war-room-office-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 24px 22px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05), 0 8px 10px -6px rgba(15, 23, 42, 0.03);
    position: relative;
    overflow: hidden;
}
.war-room-office-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 14px;
    margin-bottom: 20px;
}
.office-title {
    color: #0f172a;
    font-size: 1.12rem;
    font-weight: 800;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.office-status-pill {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 999px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
}
.war-room-desks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
    gap: 14px;
    margin-bottom: 18px;
    position: relative;
}
@media (max-width: 900px) {
    .war-room-desks-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
}
.agent-desk-card {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 16px 12px 14px 12px;
    text-align: center;
    position: relative;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
    height: auto;
    min-height: 250px;
    box-sizing: border-box;
}
.agent-desk-card.waiting {
    opacity: 0.55;
    background: #fafafa;
    border-color: #f1f5f9;
    filter: grayscale(40%);
}
.agent-desk-card.active {
    opacity: 1;
    background: #ffffff;
    border-color: #2563eb;
    transform: translateY(-8px);
    box-shadow: 0 14px 30px -4px rgba(37, 99, 235, 0.22), 0 0 0 2px rgba(37, 99, 235, 0.12);
    animation: pulse-desk-light 1.5s infinite alternate;
}
.agent-desk-card.done {
    opacity: 1;
    background: #ffffff;
    border-color: #16a34a;
    box-shadow: 0 6px 16px rgba(22, 163, 74, 0.12);
}
@keyframes pulse-desk-light {
    0% { border-color: #2563eb; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18); }
    100% { border-color: #60a5fa; box-shadow: 0 14px 32px rgba(37, 99, 235, 0.32); }
}
.agent-chair {
    position: relative;
    margin: 0 auto 6px auto;
}
.agent-avatar-wrap {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    background: #ffffff;
    border: 2px solid #cbd5e1;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}
.agent-desk-card.active .agent-avatar-wrap {
    border-color: #2563eb;
    background: #eff6ff;
    animation: agent-debate-speaking 1.1s infinite ease-in-out;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.18);
}
.agent-desk-card.done .agent-avatar-wrap {
    border-color: #16a34a;
    background: #f0fdf4;
}
@keyframes agent-debate-speaking {
    0%, 100% { transform: translateY(0) scale(1.05); }
    30% { transform: translateY(-5px) rotate(-3deg) scale(1.1); }
    70% { transform: translateY(-2px) rotate(3deg) scale(1.08); }
}
.agent-desk-mat {
    font-size: 0.68rem;
    color: #475569;
    background: #f1f5f9;
    padding: 2px 7px;
    border-radius: 6px;
    margin-top: 5px;
    font-weight: 600;
    border: 1px solid #e2e8f0;
    display: inline-block;
}
.sound-wave-bars {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    height: 16px;
    margin-bottom: 4px;
}
.sound-wave-bars span {
    width: 3px;
    background: #2563eb;
    border-radius: 999px;
    animation: sound-bar 0.9s infinite ease-in-out;
}
.sound-wave-bars span:nth-child(1) { animation-delay: 0.1s; height: 6px; }
.sound-wave-bars span:nth-child(2) { animation-delay: 0.3s; height: 14px; }
.sound-wave-bars span:nth-child(3) { animation-delay: 0.2s; height: 10px; }
.sound-wave-bars span:nth-child(4) { animation-delay: 0.4s; height: 8px; }
@keyframes sound-bar {
    0%, 100% { height: 4px; }
    50% { height: 16px; }
}
.agent-desk-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
    word-break: break-word;
}
.agent-desk-role {
    font-size: 0.73rem;
    color: #64748b;
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
.tag-waiting { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }
.tag-active { background: #2563eb; color: #ffffff; animation: blink-tag 1.2s infinite; box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3); }
.tag-done { background: #16a34a; color: #ffffff; }
@keyframes blink-tag {
    50% { opacity: 0.75; }
}
.speech-bubble {
    background: #ffffff;
    color: #1e293b;
    border: 1.5px solid #cbd5e1;
    padding: 10px 12px;
    border-radius: 12px;
    font-size: 0.76rem;
    line-height: 1.45;
    margin-top: auto;
    position: relative;
    text-align: left;
    font-weight: 500;
    word-break: break-word;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    box-sizing: border-box;
}
.speech-bubble-tail {
    position: absolute;
    top: -7px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-bottom: 7px solid #cbd5e1;
}
.speech-bubble-tail::after {
    content: '';
    position: absolute;
    top: 1.5px;
    left: -6px;
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-bottom: 6px solid #ffffff;
}
.agent-desk-card.active .speech-bubble {
    border-color: #2563eb;
    background: #f8faff;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.12);
}
.agent-desk-card.active .speech-bubble-tail {
    border-bottom-color: #2563eb;
}
.agent-desk-card.active .speech-bubble-tail::after {
    border-bottom-color: #f8faff;
}
.agent-desk-card.done .speech-bubble {
    border-color: #86efac;
    background: #f0fdf4;
    color: #166534;
}
.agent-desk-card.done .speech-bubble-tail {
    border-bottom-color: #86efac;
}
.agent-desk-card.done .speech-bubble-tail::after {
    border-bottom-color: #f0fdf4;
}
.boardroom-conference-table {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 2px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
}
.table-surface {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}
.table-agenda-dossier {
    display: flex;
    align-items: center;
    gap: 10px;
}
.dossier-icon { font-size: 22px; }
.dossier-title { font-size: 0.84rem; font-weight: 700; color: #0f172a; }
.dossier-sub { font-size: 0.73rem; color: #64748b; margin-top: 2px; }
.live-debate-indicator {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #dc2626;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 0.74rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
    animation: debate-pulse 1.2s infinite alternate;
}
@keyframes debate-pulse {
    0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.25); }
    100% { box-shadow: 0 0 0 6px rgba(220, 38, 38, 0.08); }
}
.swords-clash {
    display: inline-block;
    animation: clash-wiggle 0.6s infinite alternate;
}
@keyframes clash-wiggle {
    0% { transform: rotate(-12deg) scale(1); }
    100% { transform: rotate(12deg) scale(1.25); }
}
.war-room-table-center {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    padding: 12px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.table-center-text {
    font-size: 0.82rem;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 8px;
}
.table-pulse-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #16a34a;
    display: inline-block;
    box-shadow: 0 0 8px rgba(22, 163, 74, 0.5);
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

/* ── KHUNG VĂN BẢN A4 CHUẨN NGHỊ ĐỊNH 30/2020/NĐ-CP ── */
.a4-document-container {
    background: #f1f5f9;
    padding: 32px 20px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    margin: 16px 0;
}
.a4-doc-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1e3a8a;
    color: #ffffff;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 999px;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 6px rgba(30, 58, 138, 0.25);
}
.a4-paper-sheet {
    background: #ffffff;
    max-width: 820px;
    margin: 0 auto;
    padding: 56px 64px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    font-family: 'Times New Roman', Times, Georgia, serif;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #0f172a;
    text-align: justify;
    box-sizing: border-box;
}
@media (max-width: 768px) {
    .a4-paper-sheet {
        padding: 24px 20px;
        font-size: 0.95rem;
    }
}
</style>
"""

