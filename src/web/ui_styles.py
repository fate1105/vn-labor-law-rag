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
    margin-top: 12px;
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
.author-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 4px 0;
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
