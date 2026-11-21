"""
Styles and CSS Design System for VN Labor Law RAG Web UI.
"""

CUSTOM_CSS = """
<style>
:root {
    --bg-canvas: #f8fafc;
    --surface-card: #ffffff;
    --surface-subtle: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --brand-navy: #0b1f44;
    --brand-royal: #1d4ed8;
    --brand-accent: #2563eb;
    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --ok-bg: #ecfdf5;
    --ok-border: #6ee7b7;
    --ok-text: #065f46;
    --warn-bg: #fffbeb;
    --warn-border: #fcd34d;
    --warn-text: #92400e;
    --danger-bg: #fef2f2;
    --danger-border: #fca5a5;
    --danger-text: #991b1b;
    --shadow-sm: 0 1px 2px rgb(15 23 42 / 0.04), 0 2px 6px rgb(15 23 42 / 0.04);
    --shadow-md: 0 4px 12px -2px rgb(15 23 42 / 0.06), 0 2px 6px -1px rgb(15 23 42 / 0.04);
    --shadow-lg: 0 12px 28px -6px rgb(15 23 42 / 0.12), 0 4px 10px -2px rgb(15 23 42 / 0.06);
    --in-oklab: ;
}

@supports (background: linear-gradient(in oklab, white, black)) {
    :root {
        --in-oklab: in oklab;
    }
}

html, body, .stApp {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    line-height: 1.55;
    color: var(--text-primary);
    overflow-wrap: break-word;
}

.main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 3.5rem;
    max-width: 82rem;
}

/* ── SIDEBAR STYLING & BRAND CARD ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom var(--in-oklab), #ffffff, #f8fafc);
    border-right: 1px solid var(--border-subtle);
}

.sidebar-brand-card {
    background: linear-gradient(135deg var(--in-oklab), #0b1f44 0%, #1e3a8a 60%, #1d4ed8 100%);
    color: #ffffff;
    border-radius: 0.875rem;
    padding: 1.1rem 1.15rem;
    margin-bottom: 1.1rem;
    box-shadow: var(--shadow-md);
    border: 1px solid rgb(255 255 255 / 0.14);
}
.sidebar-brand-eyebrow {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #93c5fd;
    margin-bottom: 0.35rem;
}
.sidebar-author-name {
    font-size: 1.0625rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.2rem 0;
    line-height: 1.3;
}
.sidebar-supervisor {
    font-size: 0.8125rem;
    color: #dbeafe;
    margin: 0 0 0.65rem 0;
    line-height: 1.4;
}
.sidebar-live-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #d1fae5;
    background: rgb(6 78 59 / 0.55);
    border: 1px solid rgb(110 231 183 / 0.35);
    padding: 0.22rem 0.6rem;
    border-radius: 999px;
    min-block-size: 1.5rem;
}

/* Radio Mode Choice Cards in Sidebar (zero layout shift on selection) */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 0.45rem;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: var(--surface-card);
    border: 1.5px solid var(--border-subtle);
    border-radius: 0.65rem;
    padding: 0.55rem 0.75rem;
    margin: 0;
    transition: background-color 150ms ease-out, border-color 150ms ease-out, box-shadow 150ms ease-out;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    border-color: #93c5fd;
    background: #f8fafc;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    border-color: var(--brand-accent);
    background: color-mix(in oklab, var(--brand-accent) 7%, white);
    box-shadow: 0 2px 8px rgb(37 99 235 / 0.12);
}

/* Sidebar 2x2 Mini Stat Grid */
.sb-stat-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.5rem;
    margin-top: 0.35rem;
}
.sb-stat-item {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: 0.65rem;
    padding: 0.7rem 0.8rem;
    box-shadow: var(--shadow-sm);
}
.sb-stat-val {
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--brand-navy);
    line-height: 1.25;
}
.sb-stat-lbl {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}
.sb-source-card {
    font-size: 0.9rem;
    color: var(--text-primary);
    line-height: 1.65;
    margin-top: 0.65rem;
    padding: 0.8rem 0.9rem;
    background: var(--surface-card);
    border-radius: 0.65rem;
    border: 1px solid var(--border-subtle);
    box-shadow: var(--shadow-sm);
    overflow-wrap: anywhere;
}
.sb-source-card a {
    color: var(--brand-accent);
    text-decoration: underline;
    text-underline-offset: 2px;
    font-weight: 600;
}
.sb-source-card a:hover {
    text-decoration-thickness: 2px;
}

/* ── HERO BANNER ── */
.hero-banner {
    background:
        radial-gradient(circle at 92% 12%, rgb(96 165 250 / 0.24) 0%, transparent 45%),
        repeating-linear-gradient(to right, rgb(255 255 255 / 0.03) 0 1px, transparent 1px 2.5rem),
        linear-gradient(130deg var(--in-oklab), #091936 0%, #16357a 52%, #1d4ed8 100%);
    color: #ffffff;
    padding: 1.65rem 2rem;
    border-radius: 1.125rem;
    margin-bottom: 1.35rem;
    box-shadow: var(--shadow-lg);
    border: 1px solid rgb(255 255 255 / 0.14);
    position: relative;
    isolation: isolate;
}
.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgb(255 255 255 / 0.13);
    padding: 0.28rem 0.8rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #bfdbfe;
    margin-bottom: 0.65rem;
    border: 1px solid rgb(255 255 255 / 0.2);
    min-block-size: 1.6rem;
}
.hero-title {
    font-size: clamp(1.45rem, 1.1rem + 1.45vw, 2.05rem);
    font-weight: 800;
    margin: 0 0 0.45rem 0;
    line-height: 1.22;
    letter-spacing: -0.02em;
    color: #ffffff !important;
    text-wrap: balance;
}
.hero-subtitle {
    color: #dbeafe;
    font-size: 0.95rem;
    margin: 0;
    max-width: 72ch;
    line-height: 1.55;
    text-wrap: pretty;
}
.hero-subtitle strong, .hero-subtitle b {
    color: #93c5fd;
    font-weight: 700;
}
.hero-badges-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.95rem;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: rgb(15 23 42 / 0.42);
    border: 1px solid rgb(255 255 255 / 0.15);
    color: #f1f5f9;
    padding: 0.28rem 0.7rem;
    border-radius: 0.5rem;
    font-size: 0.78rem;
    font-weight: 500;
    min-block-size: 1.65rem;
}
.hero-pill b {
    color: #7dd3fc;
}

/* ── INTERACTIVE CONTROLS & QUICK PROMPT BUTTONS ── */
.section-eyebrow {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin: 0.2rem 0 0.55rem 0;
    font-size: 0.875rem;
    font-weight: 700;
    color: var(--text-secondary);
}

div[data-testid="stHorizontalBlock"] button {
    border-radius: 0.7rem !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    border: 1px solid var(--border-subtle) !important;
    background: var(--surface-card) !important;
    color: var(--text-primary) !important;
    padding: 0.55rem 0.85rem !important;
    min-block-size: 2.65rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow 150ms ease-out, border-color 150ms ease-out, background-color 150ms ease-out, scale 120ms ease-out !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    border-color: var(--brand-accent) !important;
    color: var(--brand-accent) !important;
    background: #eff6ff !important;
    box-shadow: 0 4px 12px rgb(37 99 235 / 0.14) !important;
}
div[data-testid="stHorizontalBlock"] button:active {
    scale: 0.98;
}
:where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
    outline: 2px solid var(--brand-accent) !important;
    outline-offset: 3px !important;
}

/* Styled Tabs */
div[data-testid="stTabs"] button[role="tab"] {
    font-weight: 700;
    font-size: 0.88rem;
    padding: 0.55rem 0.95rem;
    min-block-size: 2.5rem;
}

/* Active Query Context Bar */
.query-context-bar {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--brand-accent);
    border-radius: 0.75rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow-sm);
    font-size: 0.92rem;
    line-height: 1.5;
}

/* ── KPI METRIC CARDS (BENCHMARK & SUMMARY STRIPS) ── */
.kpi-card {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: 0.875rem;
    padding: 1.05rem 1.15rem;
    box-shadow: var(--shadow-md);
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    min-block-size: 6.5rem;
}
.kpi-card--accent {
    border-top: 3px solid var(--brand-accent);
}
.kpi-card--emerald {
    border-top: 3px solid #10b981;
}
.kpi-card--amber {
    border-top: 3px solid #f59e0b;
}
.kpi-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
}
.kpi-value {
    font-size: clamp(1.35rem, 1.1rem + 0.8vw, 1.75rem);
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.2;
}
.kpi-delta {
    display: inline-flex;
    align-items: center;
    align-self: flex-start;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: var(--ok-bg);
    color: var(--ok-text);
    border: 1px solid var(--ok-border);
    margin-top: 0.15rem;
}

/* ── COMPARISON SUMMARY STRIP & MODEL CARDS ── */
.compare-summary-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
    gap: 0.65rem;
    margin-bottom: 1.1rem;
}
.compare-stat-pill {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: 0.75rem;
    padding: 0.65rem 0.9rem;
    box-shadow: var(--shadow-sm);
    font-size: 0.82rem;
    color: var(--text-secondary);
}
.compare-stat-pill strong {
    display: block;
    font-size: 0.98rem;
    color: var(--text-primary);
    margin-top: 0.1rem;
}

.model-header-baseline {
    background: linear-gradient(to bottom var(--in-oklab), #ffffff, #f8fafc);
    border: 1px solid var(--border-strong);
    border-top: 4px solid #64748b;
    border-radius: 0.875rem;
    padding: 1.05rem 1.2rem;
    margin-bottom: 0.9rem;
    box-shadow: var(--shadow-md);
}
.model-header-effect {
    background: linear-gradient(to bottom var(--in-oklab), #ffffff, #f0fdf4);
    border: 1px solid #86efac;
    border-top: 4px solid #16a34a;
    border-radius: 0.875rem;
    padding: 1.05rem 1.2rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 6px 18px -4px rgb(22 163 74 / 0.12), 0 2px 6px rgb(15 23 42 / 0.04);
}
.model-header-baseline h4, .model-header-effect h4 {
    text-wrap: balance;
}
.model-tag {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 0.2rem 0.55rem;
    border-radius: 0.4rem;
    display: inline-block;
    margin-bottom: 0.4rem;
}
.tag-base { background: #e2e8f0; color: #334155; }
.tag-effect { background: #dcfce7; color: #166534; }

/* ── STATUS BADGES ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.2rem 0.6rem;
    border-radius: 0.4rem;
    font-size: 0.75rem;
    font-weight: 700;
    margin-right: 0.35rem;
    min-block-size: 1.45rem;
}
.badge-ok { background-color: var(--ok-bg); color: var(--ok-text); border: 1px solid var(--ok-border); }
.badge-warning { background-color: var(--warn-bg); color: var(--warn-text); border: 1px solid var(--warn-border); }
.badge-danger { background-color: var(--danger-bg); color: var(--danger-text); border: 1px solid var(--danger-border); }
.badge-unknown { background-color: var(--surface-subtle); color: var(--text-secondary); border: 1px solid var(--border-strong); }

/* ── CALLOUTS & CITATION CARDS ── */
.danger-callout {
    background-color: var(--danger-bg);
    border: 1px solid var(--danger-border);
    border-left: 5px solid #dc2626;
    padding: 0.85rem 1.05rem;
    border-radius: 0.65rem;
    margin: 0.75rem 0 1rem 0;
    color: var(--danger-text);
    font-size: 0.88rem;
    line-height: 1.55;
    text-wrap: pretty;
}
.analysis-card {
    background: linear-gradient(to right var(--in-oklab), #f0fdf4, #ffffff);
    border: 1px solid #86efac;
    border-left: 5px solid #16a34a;
    padding: 1.05rem 1.25rem;
    border-radius: 0.75rem;
    margin-top: 1.25rem;
    color: #14532d;
    font-size: 0.92rem;
    line-height: 1.6;
    box-shadow: var(--shadow-sm);
    text-wrap: pretty;
}

.citation-box {
    background-color: var(--surface-canvas, #f8fafc);
    border: 1px solid var(--border-subtle);
    border-left: 3.5px solid var(--brand-accent);
    padding: 0.8rem 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    line-height: 1.65;
    color: var(--text-primary);
    margin: 0.5rem 0 0.9rem 0;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    text-wrap: pretty;
}
.citation-box--ok { border-left-color: #16a34a; }
.citation-box--warning { border-left-color: #d97706; background-color: #fffdf5; }
.citation-box--danger { border-left-color: #dc2626; background-color: #fffafa; }

.citation-meta-chip {
    display: inline-block;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.74rem;
    background: var(--surface-subtle);
    color: #334155;
    border: 1px solid var(--border-subtle);
    padding: 0.15rem 0.45rem;
    border-radius: 0.35rem;
    margin-right: 0.4rem;
    margin-top: 0.2rem;
}

/* ── WAR ROOM SUMMARY TIMELINE & A4 OFFICIAL SHEET ── */
.wr-dossier-banner {
    background: linear-gradient(to right var(--in-oklab), #ecfdf5, #f8fafc);
    border: 1px solid #86efac;
    border-left: 5px solid #16a34a;
    padding: 0.95rem 1.2rem;
    border-radius: 0.75rem;
    margin-bottom: 0.9rem;
    box-shadow: var(--shadow-sm);
}
.wr-latency-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.55rem;
}
.wr-latency-chip {
    font-size: 0.75rem;
    font-weight: 600;
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 999px;
    padding: 0.18rem 0.6rem;
}

.a4-document-container {
    background: linear-gradient(to bottom var(--in-oklab), #e2e8f0, #f1f5f9);
    padding: 2rem 1.25rem;
    border-radius: 0.9rem;
    border: 1px solid var(--border-strong);
    margin: 1rem 0;
    box-shadow: inset 0 2px 6px rgb(15 23 42 / 0.05);
}
.a4-doc-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--brand-navy);
    color: #ffffff;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.3rem 0.95rem;
    border-radius: 999px;
    letter-spacing: 0.03em;
    box-shadow: var(--shadow-sm);
    min-block-size: 1.65rem;
}
.a4-paper-sheet {
    background: #ffffff;
    max-width: 52rem;
    margin: 0 auto;
    padding: 3.25rem 3.75rem;
    box-shadow: 0 14px 32px -8px rgb(15 23 42 / 0.12), 0 2px 6px rgb(15 23 42 / 0.06);
    border: 1px solid var(--border-strong);
    border-radius: 0.25rem;
    font-family: "Times New Roman", Times, Georgia, serif;
    font-size: 1.0625rem;
    line-height: 1.68;
    color: #0f172a;
    text-align: start;
    box-sizing: border-box;
    overflow-wrap: break-word;
}
/* ── BENCHMARK RESPONSIVE SEMANTIC TABLE ── */
.bench-table-wrap {
    overflow: auto;
    max-inline-size: 100%;
    max-block-size: min(32rem, 80vh);
    container-type: inline-size;
    border: 1px solid var(--border-subtle);
    border-radius: 0.875rem;
    background: var(--surface-card);
    box-shadow: var(--shadow-sm);
}
.bench-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.875rem;
    text-align: start;
    --label-2: "Số câu";
    --label-3: "Base Hit@3";
    --label-4: "Eff Hit@3";
    --label-5: "Base MRR";
    --label-6: "Eff MRR";
    --label-7: "Chênh lệch MRR";
    --label-8: "Base Chunks cũ";
    --label-9: "Eff Cờ DANGER";
}
.bench-table thead {
    position: sticky;
    inset-block-start: 0;
    z-index: 2;
}
.bench-table thead th {
    background: #f1f5f9;
    color: var(--text-primary);
    font-weight: 700;
    padding: 0.75rem 0.9rem;
    border-bottom: 1.5px solid var(--border-strong);
    white-space: nowrap;
}
.bench-table tbody th,
.bench-table tbody td {
    padding: 0.7rem 0.9rem;
    border-bottom: 1px solid var(--border-subtle);
    white-space: nowrap;
}
.bench-table tbody th {
    position: sticky;
    inset-inline-start: 0;
    z-index: 1;
    background: var(--surface-card);
    font-weight: 600;
    color: var(--text-primary);
}
.bench-table tbody tr:last-child th,
.bench-table tbody tr:last-child td {
    border-bottom: none;
    background: #f0fdf4;
    font-weight: 800;
    color: #14532d;
}
.bench-delta-pos {
    color: #15803d;
    font-weight: 700;
}
@container (width < 600px) {
    .bench-table, .bench-table thead, .bench-table tbody, .bench-table tr, .bench-table th, .bench-table td {
        display: block;
    }
    .bench-table thead {
        display: none;
    }
    .bench-table tbody tr {
        margin-block-end: 0.85rem;
        border: 1px solid var(--border-subtle);
        border-radius: 0.5rem;
    }
    .bench-table tbody th {
        position: sticky;
        inset-block-start: 0;
        z-index: 2;
        background: #f1f5f9;
    }
    .bench-table td:nth-child(2)::before { content: var(--label-2) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(3)::before { content: var(--label-3) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(4)::before { content: var(--label-4) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(5)::before { content: var(--label-5) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(6)::before { content: var(--label-6) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(7)::before { content: var(--label-7) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(8)::before { content: var(--label-8) ": "; font-weight: 600; color: var(--text-muted); }
    .bench-table td:nth-child(9)::before { content: var(--label-9) ": "; font-weight: 600; color: var(--text-muted); }
}

@media (max-width: 48rem) {
    .a4-paper-sheet {
        padding: 1.5rem 1.25rem;
        font-size: 0.96rem;
    }
    .hero-banner {
        padding: 1.25rem 1.25rem;
    }
}
</style>
"""
