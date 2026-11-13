"""Design system for the Engineering Intelligence Platform.

All custom CSS lives here. Selectors are scoped to class names used by
``app.ui.components`` so the rules survive Streamlit version drift, with a
small number of stable ``data-testid`` hooks for native chrome.
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --eip-navy-900: #101B2D;
  --eip-navy-800: #1D3048;
  --eip-blue: #3182CE;
  --eip-blue-soft: #E7F0FB;
  --eip-teal: #16B8A6;
  --eip-bg: #F4F6F9;
  --eip-card: #FFFFFF;
  --eip-text: #18283D;
  --eip-text-2: #64748B;
  --eip-border: #E2E8F0;
  --eip-success: #16A085;
  --eip-success-soft: #E6F6F2;
  --eip-warning: #E8A23A;
  --eip-warning-soft: #FBF3E4;
  --eip-error: #DC5B5B;
  --eip-error-soft: #FBEAEA;
  --eip-shadow: 0 1px 2px rgba(16, 27, 45, 0.06), 0 1px 3px rgba(16, 27, 45, 0.08);
}

/* ------------------------------
   Base typography
   ------------------------------ */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
button, input, textarea, select,
[data-testid="stMarkdownContainer"],
[data-testid="stText"], label, p, span {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
               Roboto, 'Helvetica Neue', Arial, sans-serif;
  letter-spacing: -0.01em;
}

[data-testid="stAppViewContainer"] {
  background: var(--eip-bg);
}

[data-testid="stHeader"] {
  /* Translucent with blur so scrolled content fades under the bar
     instead of being cut off at a hard opaque edge. */
  background: rgba(244, 246, 249, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--eip-border);
}

/* Hide Streamlit development chrome (Deploy button, kebab menu, run status)
   so the header reads as product chrome rather than a dev tool. The toolbar
   wrapper itself stays visible because it contains the sidebar expand
   control (stExpandSidebarButton) that users need after collapsing the
   sidebar. */
[data-testid="stBaseButton-header"],
[data-testid="stMainMenuButton"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
  display: none !important;
}

[data-testid="stMainBlockContainer"] {
  max-width: 1200px;
  /* The fixed stHeader bar is 60px tall; 4.5rem keeps page titles clear of it. */
  padding-top: 4.5rem;
  padding-bottom: 4.5rem;
}

/* ------------------------------
   Dark navy sidebar
   ------------------------------ */
[data-testid="stSidebar"] {
  background-color: var(--eip-navy-900);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stSidebar"] * {
  color: #B9C6D8;
}

[data-testid="stSidebar"] .eip-brand-name {
  color: #FFFFFF;
  font-size: 1.02rem;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

[data-testid="stSidebar"] .eip-brand-subtitle {
  color: #7E93AF;
  font-size: 0.72rem;
  font-weight: 500;
  line-height: 1.35;
}

[data-testid="stSidebar"] .eip-sidebar-caption {
  color: #7E93AF;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin: 0.9rem 0 0.3rem 0;
}

/* Navigation links */
[data-testid="stSidebar"] a[data-testid="stPageLink"],
[data-testid="stSidebar"] [data-testid="stPageLink"] {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 0.34rem 0.6rem;
  margin-bottom: 0.18rem;
  transition: background 120ms ease, border-color 120ms ease;
}

[data-testid="stSidebar"] a[data-testid="stPageLink"] span,
[data-testid="stSidebar"] [data-testid="stPageLink"] span {
  color: #B9C6D8;
  font-size: 0.865rem;
  font-weight: 500;
}

[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover,
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.08);
}

[data-testid="stSidebar"] a[data-testid="stPageLink"]:focus-visible,
[data-testid="stSidebar"] [data-testid="stPageLink"]:focus-visible {
  outline: 2px solid var(--eip-teal);
  outline-offset: 1px;
}

[data-testid="stSidebar"] .eip-nav-active span {
  color: #FFFFFF !important;
  font-weight: 600;
}

[data-testid="stSidebar"] .eip-nav-active,
[data-testid="stSidebar"] a.eip-nav-active {
  background: rgba(49, 130, 206, 0.18);
  border-color: rgba(49, 130, 206, 0.45);
}

/* Sidebar service rows */
.eip-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.28rem 0.1rem;
  font-size: 0.78rem;
}

.eip-status-row .eip-status-label { font-weight: 500; }

/* Sidebar footer */
.eip-sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 0.8rem;
  padding-top: 0.7rem;
  font-size: 0.68rem;
  color: #7E93AF;
  line-height: 1.5;
}

.eip-sidebar-footer strong { color: #B9C6D8; font-weight: 600; }

/* Bordered widget panels (st.container(border=True, key="eip-panel-…")).
   Streamlit applies the container key as a `st-key-*` class. The legacy
   stVerticalBlockBorderWrapper hook is kept for other Streamlit versions. */
div[data-testid="stVerticalBlockBorderWrapper"],
div[class*="st-key-eip-panel-"] {
  border: 1px solid var(--eip-border) !important;
  border-radius: 12px !important;
  background: var(--eip-card) !important;
  box-shadow: var(--eip-shadow);
  padding: 0.6rem 0.4rem;
}

div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"],
div[class*="st-key-eip-panel-"] [data-testid="stVerticalBlock"] {
  padding: 0 0.4rem;
}

/* ------------------------------
   Page header
   ------------------------------ */
.eip-page-header {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 0.2rem 0 1.1rem 0;
  border-bottom: 1px solid var(--eip-border);
  margin-bottom: 1.4rem;
}

.eip-page-header .eip-page-accent {
  width: 4px;
  align-self: stretch;
  border-radius: 2px;
  background: linear-gradient(180deg, var(--eip-blue) 0%, var(--eip-teal) 100%);
  flex-shrink: 0;
}

.eip-page-header h1 {
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--eip-text);
  margin: 0;
  padding: 0;
  line-height: 1.25;
  letter-spacing: -0.02em;
}

.eip-page-header .eip-page-subtitle {
  font-size: 0.83rem;
  color: var(--eip-text-2);
  margin-top: 0.15rem;
}

/* ------------------------------
   Metric cards
   ------------------------------ */
.eip-metric-grid {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.eip-metric-card {
  flex: 1 1 220px;
  min-width: 205px;
  background: var(--eip-card);
  border: 1px solid var(--eip-border);
  border-radius: 12px;
  padding: 0.95rem 1.05rem 0.9rem 1.05rem;
  box-shadow: var(--eip-shadow);
}

.eip-metric-label {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--eip-text-2);
}

.eip-metric-label .eip-metric-icon {
  font-size: 0.95rem;
  line-height: 1;
}

.eip-metric-value {
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--eip-text);
  margin-top: 0.45rem;
  line-height: 1.15;
  letter-spacing: -0.02em;
  word-break: break-word;
}

.eip-metric-sub {
  font-size: 0.74rem;
  color: var(--eip-text-2);
  margin-top: 0.3rem;
  line-height: 1.4;
}

.eip-metric-value.eip-value-ok   { color: var(--eip-success); }
.eip-metric-value.eip-value-bad  { color: var(--eip-error); }

/* ------------------------------
   Status pills
   ------------------------------ */
.eip-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.18rem 0.55rem 0.18rem 0.45rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
}

.eip-pill .eip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.eip-pill.eip-pill-success { background: var(--eip-success-soft); color: #0E7A63; }
.eip-pill.eip-pill-success .eip-dot { background: var(--eip-success); }

.eip-pill.eip-pill-warning { background: var(--eip-warning-soft); color: #9C6A14; }
.eip-pill.eip-pill-warning .eip-dot { background: var(--eip-warning); }

.eip-pill.eip-pill-error { background: var(--eip-error-soft); color: #B23A3A; }
.eip-pill.eip-pill-error .eip-dot { background: var(--eip-error); }

.eip-pill.eip-pill-neutral { background: #EDF1F6; color: #51617A; }
.eip-pill.eip-pill-neutral .eip-dot { background: #93A4BB; }

.eip-pill.eip-pill-info { background: var(--eip-blue-soft); color: #1D5FA8; }
.eip-pill.eip-pill-info .eip-dot { background: var(--eip-blue); }

/* ------------------------------
   Panels and cards
   ------------------------------ */
.eip-panel {
  background: var(--eip-card);
  border: 1px solid var(--eip-border);
  border-radius: 12px;
  padding: 1.05rem 1.15rem;
  box-shadow: var(--eip-shadow);
  margin-bottom: 0.9rem;
}

.eip-panel-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--eip-text);
  margin-bottom: 0.65rem;
  letter-spacing: -0.01em;
}

.eip-panel-title .eip-panel-icon { font-size: 1rem; line-height: 1; }

.eip-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.42rem 0;
  border-bottom: 1px solid #EDF1F5;
  font-size: 0.8rem;
}

.eip-row:last-child { border-bottom: none; }

.eip-row .eip-row-label { color: var(--eip-text-2); font-weight: 500; }
.eip-row .eip-row-value { color: var(--eip-text); font-weight: 600; text-align: right; word-break: break-word; }
.eip-row .eip-row-value.eip-mono {
  font-family: 'SFMono-Regular', ui-monospace, 'JetBrains Mono', Menlo, monospace;
  font-size: 0.74rem;
}

/* Quick navigation cards */
.eip-quicknav-grid {
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
}

.eip-quicknav {
  flex: 1 1 210px;
  min-width: 200px;
  background: var(--eip-card);
  border: 1px solid var(--eip-border);
  border-radius: 12px;
  padding: 0.95rem 1rem;
  box-shadow: var(--eip-shadow);
  transition: border-color 120ms ease, transform 120ms ease;
}

.eip-quicknav:hover { border-color: var(--eip-blue); }

.eip-quicknav .eip-quicknav-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--eip-blue-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  margin-bottom: 0.55rem;
}

.eip-quicknav .eip-quicknav-title {
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--eip-text);
}

.eip-quicknav .eip-quicknav-hint {
  font-size: 0.74rem;
  color: var(--eip-text-2);
  margin-top: 0.2rem;
  line-height: 1.4;
}

/* ------------------------------
   AI Assistant
   ------------------------------ */
.eip-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2.2rem 1rem 1.4rem 1rem;
}

.eip-welcome .eip-welcome-icon {
  width: 62px;
  height: 62px;
  border-radius: 16px;
  background: var(--eip-navy-900);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.05rem;
  box-shadow: var(--eip-shadow);
}

.eip-welcome h2 {
  font-size: 1.28rem;
  font-weight: 700;
  color: var(--eip-text);
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.02em;
}

.eip-welcome .eip-welcome-desc {
  font-size: 0.87rem;
  color: var(--eip-text-2);
  max-width: 540px;
  line-height: 1.55;
}

.eip-welcome .eip-welcome-capabilities {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.8rem;
}

.eip-suggested-grid {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  margin-top: 1.3rem;
}

.eip-suggested {
  flex: 1 1 240px;
  min-width: 225px;
  background: var(--eip-card);
  border: 1px solid var(--eip-border);
  border-radius: 12px;
  padding: 0.85rem 0.95rem;
  box-shadow: var(--eip-shadow);
  transition: border-color 120ms ease;
}

.eip-suggested:hover { border-color: var(--eip-blue); }

.eip-suggested .eip-suggested-domain {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--eip-blue);
  background: var(--eip-blue-soft);
  border-radius: 6px;
  padding: 0.16rem 0.5rem;
}

.eip-suggested .eip-suggested-question {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--eip-text);
  margin-top: 0.5rem;
  line-height: 1.4;
}

.eip-suggested .eip-suggested-ask {
  font-size: 0.73rem;
  color: var(--eip-blue);
  font-weight: 600;
  margin-top: 0.5rem;
}

/* Model banner */
.eip-model-banner {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  background: var(--eip-card);
  border: 1px solid var(--eip-border);
  border-radius: 12px;
  padding: 0.6rem 0.95rem;
  box-shadow: var(--eip-shadow);
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.eip-model-banner .eip-model-chip {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--eip-navy-900);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.eip-model-banner .eip-model-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--eip-text);
}

.eip-model-banner .eip-model-detail {
  font-size: 0.72rem;
  color: var(--eip-text-2);
}

/* Refusal banner inside assistant answers */
.eip-refusal-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--eip-warning-soft);
  border: 1px solid #F0DDB4;
  color: #9C6A14;
  border-radius: 9px;
  padding: 0.5rem 0.75rem;
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.6rem;
}

/* Source cards */
.eip-sources-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.9rem 0 0.45rem 0;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--eip-text-2);
}

.eip-source-item {
  border: 1px solid var(--eip-border);
  border-radius: 10px;
  background: #FBFCFE;
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.45rem;
}

.eip-source-item .eip-source-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--eip-text);
}

.eip-source-item .eip-cite-badge {
  background: var(--eip-blue-soft);
  color: var(--eip-blue);
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.1rem 0.42rem;
  flex-shrink: 0;
}

.eip-source-item .eip-source-meta {
  font-size: 0.7rem;
  color: var(--eip-text-2);
  margin-top: 0.15rem;
}

.eip-source-item .eip-source-excerpt {
  font-size: 0.76rem;
  color: #3D4C63;
  line-height: 1.5;
  margin-top: 0.4rem;
  padding-left: 0.65rem;
  border-left: 2px solid var(--eip-border);
}

/* Copy button (st.html) */
.eip-copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1px solid var(--eip-border);
  background: var(--eip-card);
  color: var(--eip-text-2);
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  font-family: inherit;
  padding: 0.3rem 0.65rem;
  cursor: pointer;
  transition: border-color 120ms ease, color 120ms ease;
}

.eip-copy-btn:hover { border-color: var(--eip-blue); color: var(--eip-blue); }
.eip-copy-btn:focus-visible { outline: 2px solid var(--eip-blue); outline-offset: 1px; }

/* ------------------------------
   Empty states
   ------------------------------ */
.eip-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: var(--eip-card);
  border: 1px dashed #C9D4E2;
  border-radius: 12px;
  padding: 1.8rem 1.2rem;
}

.eip-empty .eip-empty-icon {
  font-size: 1.7rem;
  margin-bottom: 0.5rem;
}

.eip-empty .eip-empty-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--eip-text);
}

.eip-empty .eip-empty-hint {
  font-size: 0.78rem;
  color: var(--eip-text-2);
  margin-top: 0.25rem;
  line-height: 1.5;
  max-width: 440px;
}

/* ------------------------------
   Data tables (custom HTML)
   ------------------------------ */
.eip-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--eip-card);
  border: 1px solid var(--eip-border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--eip-shadow);
  font-size: 0.8rem;
}

.eip-table thead th {
  background: #F8FAFC;
  color: var(--eip-text-2);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  text-align: left;
  padding: 0.55rem 0.85rem;
  border-bottom: 1px solid var(--eip-border);
}

.eip-table tbody td {
  padding: 0.6rem 0.85rem;
  border-bottom: 1px solid #EDF1F5;
  color: var(--eip-text);
  vertical-align: middle;
}

.eip-table tbody tr:last-child td { border-bottom: none; }
.eip-table tbody tr:hover td { background: #F8FAFD; }

.eip-table .eip-cell-strong { font-weight: 600; }
.eip-table .eip-cell-muted { color: var(--eip-text-2); font-size: 0.74rem; }
.eip-table .eip-cell-mono {
  font-family: 'SFMono-Regular', ui-monospace, 'JetBrains Mono', Menlo, monospace;
  font-size: 0.72rem;
}

/* Type tag */
.eip-type-tag {
  display: inline-block;
  background: #EDF1F6;
  color: #51617A;
  border-radius: 6px;
  font-size: 0.66rem;
  font-weight: 700;
  padding: 0.14rem 0.45rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ------------------------------
   Native Streamlit chrome polish
   ------------------------------ */
div[data-testid="stExpander"] {
  border: 1px solid var(--eip-border) !important;
  border-radius: 10px !important;
  background: var(--eip-card);
  box-shadow: none;
}

div[data-testid="stExpander"] details summary span {
  font-size: 0.8rem;
  font-weight: 600;
}

[data-testid="stChatMessage"] {
  border-radius: 12px;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] {
  border-radius: 12px;
}

[data-testid="stChatInput"]:focus-within {
  border-color: var(--eip-blue);
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.14);
}

[data-testid="stBaseButton-secondary"] button,
[data-testid="stBaseButton-tertiary"] button,
[data-testid="stBaseButton-primary"] button,
.stButton > button {
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.82rem;
}

[data-testid="stBaseButton-primary"] button,
.stButton > button[kind="primary"] {
  background: var(--eip-blue);
  border-color: var(--eip-blue);
}

[data-testid="stBaseButton-primary"] button:hover,
.stButton > button[kind="primary"]:hover {
  background: #2B6FBA;
  border-color: #2B6FBA;
}

[data-testid="stBaseButton-primary"] button:focus-visible {
  outline: 2px solid var(--eip-navy-900);
  outline-offset: 2px;
}

[data-testid="stFileUploaderDropzone"] {
  border-radius: 12px;
  border: 1.5px dashed #C9D4E2;
  background: #FBFCFE;
}

[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--eip-blue);
}

div[data-testid="stStatusWidget"],
[data-testid="stStatus"] {
  border-radius: 10px;
}

div[data-testid="stAlert"] {
  border-radius: 10px;
}

/* Scrollbars */
[data-testid="stAppViewContainer"] ::-webkit-scrollbar { width: 9px; height: 9px; }
[data-testid="stAppViewContainer"] ::-webkit-scrollbar-thumb {
  background: #C7D2E0; border-radius: 8px; border: 2px solid var(--eip-bg);
}
[data-testid="stSidebar"] ::-webkit-scrollbar { width: 8px; }
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.14); border-radius: 8px;
}

/* ------------------------------
   Responsive adjustments
   ------------------------------ */
@media (max-width: 1100px) {
  .eip-metric-card { min-width: 190px; }
  [data-testid="stMainBlockContainer"] { padding-left: 1.4rem; padding-right: 1.4rem; }
}

@media (max-width: 820px) {
  .eip-metric-value { font-size: 1.35rem; }
  .eip-page-header h1 { font-size: 1.2rem; }
  .eip-metric-grid { gap: 0.6rem; }
  .eip-metric-card { min-width: 45%; }
  [data-testid="stMainBlockContainer"] { padding-left: 1rem; padding-right: 1rem; }
}
"""


def load_css() -> None:
    import streamlit as st

    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
