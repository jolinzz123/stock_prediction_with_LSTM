import streamlit as st
from theme import inject_global_css
from page_watchlist import render_watchlist_page
from page_detail import render_detail_page
from page_compare import render_compare_page

<<<<<<< Updated upstream
# ── Page config (must run before any other st call) ─────────────────────────
st.set_page_config(
    page_title="Foresight — Stock Intelligence",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><polyline points='3 17 9 11 13 15 21 7' fill='none' stroke='%234C9BE8' stroke-width='2.5' stroke-linecap='round'/></svg>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ───────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "watchlist"
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ── Table row click → ?ticker= → navigate to detail ────────────────────────
try:
    qp = st.query_params
    if "ticker" in qp:
        st.session_state.selected_ticker = str(qp["ticker"]).strip().upper()
        st.session_state.page = "detail"
        st.query_params.clear()
        st.rerun()
except Exception:
    pass

# ── Inject global CSS ──────────────────────────────────────────────────────
inject_global_css()

# ── Route dispatch ─────────────────────────────────────────────────────────
if st.session_state.page == "detail" and st.session_state.selected_ticker:
    render_detail_page(st.session_state.selected_ticker)
elif st.session_state.page == "compare":
    render_compare_page()
else:
    render_watchlist_page()
=======
from data_fetcher import fetch_stock_data, get_stock_info
from predictor import run_prediction
from news_analyzer import (
    get_news_sentiment,
    generate_recommendation,
    extract_market_drivers,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Foresight — Stock Predictor",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%232EE59D' d='M3 17l4-4 4 4 4-8 4 4'/></svg>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme toggle (stored in session state) ─────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ── Design tokens (per theme) ──────────────────────────────────────────────────
DARK = {
    "bg_base":        "#080C10",
    "bg_surface":     "#0F1923",
    "bg_card":        "#111D2B",
    "bg_card_hover":  "#162234",
    "bg_input":       "#0D1824",
    "border":         "#1E2D3D",
    "border_accent":  "#2EE59D",
    "accent_green":   "#2EE59D",
    "accent_blue":    "#4C9BE8",
    "accent_red":     "#FF4D6D",
    "accent_amber":   "#F5A623",
    "text_primary":   "#E8F1F9",
    "text_secondary": "#7A92A8",
    "text_muted":     "#3D5166",
    "text_on_green":  "#041810",
    "text_on_red":    "#1A0008",
    "chart_grid":     "#111D2B",
    "chart_paper":    "rgba(0,0,0,0)",
    "chart_bg":       "rgba(0,0,0,0)",
    "plotly_theme":   "plotly_dark",
    "rail_glow":      "rgba(46,229,157,0.4)",
    "shadow":         "0 4px 32px rgba(0,0,0,0.6)",
    "badge_buy_bg":   "rgba(46,229,157,0.12)",
    "badge_buy_bd":   "rgba(46,229,157,0.35)",
    "badge_sell_bg":  "rgba(255,77,109,0.12)",
    "badge_sell_bd":  "rgba(255,77,109,0.35)",
    "badge_hold_bg":  "rgba(245,166,35,0.12)",
    "badge_hold_bd":  "rgba(245,166,35,0.35)",
    "pos_pill_bg":    "rgba(46,229,157,0.12)",
    "neg_pill_bg":    "rgba(255,77,109,0.12)",
    "neu_pill_bg":    "rgba(122,146,168,0.12)",
    "scrollbar_track": "#0F1923",
    "scrollbar_thumb": "#1E2D3D",
    "toggle_bg":      "#0F1923",
    "toggle_border":  "#1E2D3D",
}

LIGHT = {
    "bg_base":        "#EEF2F7",
    "bg_surface":     "#F7F9FC",
    "bg_card":        "#FFFFFF",
    "bg_card_hover":  "#F0F5FB",
    "bg_input":       "#FFFFFF",
    "border":         "#D4DDE8",
    "border_accent":  "#0EA271",
    "accent_green":   "#0EA271",
    "accent_blue":    "#1A72CC",
    "accent_red":     "#D93052",
    "accent_amber":   "#C07B00",
    "text_primary":   "#0A1929",
    "text_secondary": "#4A6280",
    "text_muted":     "#9EB3C8",
    "text_on_green":  "#FFFFFF",
    "text_on_red":    "#FFFFFF",
    "chart_grid":     "#E8EEF5",
    "chart_paper":    "rgba(0,0,0,0)",
    "chart_bg":       "rgba(0,0,0,0)",
    "plotly_theme":   "plotly_white",
    "rail_glow":      "rgba(14,162,113,0.25)",
    "shadow":         "0 2px 16px rgba(0,40,90,0.08)",
    "badge_buy_bg":   "rgba(14,162,113,0.10)",
    "badge_buy_bd":   "rgba(14,162,113,0.30)",
    "badge_sell_bg":  "rgba(217,48,82,0.09)",
    "badge_sell_bd":  "rgba(217,48,82,0.28)",
    "badge_hold_bg":  "rgba(192,123,0,0.09)",
    "badge_hold_bd":  "rgba(192,123,0,0.28)",
    "pos_pill_bg":    "rgba(14,162,113,0.10)",
    "neg_pill_bg":    "rgba(217,48,82,0.09)",
    "neu_pill_bg":    "rgba(74,98,128,0.09)",
    "scrollbar_track": "#EEF2F7",
    "scrollbar_thumb": "#C8D5E3",
    "toggle_bg":      "#FFFFFF",
    "toggle_border":  "#D4DDE8",
}

T = DARK if st.session_state.theme == "dark" else LIGHT
is_dark = st.session_state.theme == "dark"

# ── SVG icon helpers ───────────────────────────────────────────────────────────


def icon(name: str, size: int = 16, color: str | None = None) -> str:
    """Return an inline SVG icon by name. Stroke-based, Tabler-style."""
    c = color or T["text_secondary"]
    s = f'width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'
    icons = {
        "chart-line":    f'<svg {s}><polyline points="3 17 9 11 13 15 21 7"/><polyline points="14 7 21 7 21 14"/></svg>',
        "trending-up":   f'<svg {s}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
        "trending-down": f'<svg {s}><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
        "minus-circle":  f'<svg {s}><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
        "sun":           f'<svg {s}><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
        "moon":          f'<svg {s}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
        "newspaper":     f'<svg {s}><path d="M4 3h16a1 1 0 0 1 1 1v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4a1 1 0 0 1 1-1z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="12" y2="15"/></svg>',
        "brain":         f'<svg {s}><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.44-3.14Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.44-3.14Z"/></svg>',
        "calendar":      f'<svg {s}><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "external-link": f'<svg {s}><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
        "alert":         f'<svg {s}><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        "search":        f'<svg {s}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        "activity":      f'<svg {s}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
        "layers":        f'<svg {s}><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        "check-circle":  f'<svg {s}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        "info":          f'<svg {s}><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    }
    return icons.get(name, icons["info"])


def sentiment_icon(label: str) -> str:
    if "positive" in label.lower():
        return icon("trending-up", 14, T["accent_green"])
    if "negative" in label.lower():
        return icon("trending-down", 14, T["accent_red"])
    return icon("minus-circle", 14, T["text_secondary"])


# ── CSS injection ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & base ─────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {{ 
    background: {T["bg_base"]} !important;
    color: {T["text_primary"]} !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}}

/* ── Hide Streamlit chrome ─────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stSidebar"] {{ display: none; }}
.block-container {{
    max-width: 1360px !important;
    padding: 0 2rem 4rem !important;
}}

/* ── Scrollbar ─────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {T["scrollbar_track"]}; }}
::-webkit-scrollbar-thumb {{ background: {T["scrollbar_thumb"]}; border-radius: 3px; }}

/* ── Typography helpers ────────────────────────────── */
.sg {{ font-family: 'Space Grotesk', sans-serif !important; }}
.mono {{ font-family: 'JetBrains Mono', monospace !important; }}

/* ── Top nav bar ───────────────────────────────────── */
.topnav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 0 1rem;
    border-bottom: 1px solid {T["border"]};
    margin-bottom: 2rem;
}}
.topnav-brand {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: {T["text_primary"]};
    letter-spacing: -0.02em;
}}
.topnav-brand .brand-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: {T["accent_green"]};
    box-shadow: 0 0 8px {T["rail_glow"]};
    margin-right: 2px;
}}
.topnav-sub {{
    font-size: 0.78rem;
    color: {T["text_muted"]};
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 400;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.topnav-right {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

/* ── Theme pill toggle ─────────────────────────────── */
.theme-toggle {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: {T["toggle_bg"]};
    border: 1px solid {T["toggle_border"]};
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    color: {T["text_secondary"]};
    cursor: pointer;
    transition: all 0.2s;
}}

/* ── Data rail section header ──────────────────────── */
.rail-header {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 2rem 0 1.25rem;
    position: relative;
}}
.rail-header::before {{
    content: '';
    display: block;
    width: 2px;
    height: 18px;
    background: {T["accent_green"]};
    border-radius: 2px;
    box-shadow: 0 0 8px {T["rail_glow"]};
    flex-shrink: 0;
}}
.rail-header-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: {T["text_secondary"]};
    letter-spacing: 0.09em;
    text-transform: uppercase;
}}
.rail-header-line {{
    flex: 1;
    height: 1px;
    background: {T["border"]};
}}

/* ── Metric cards ──────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {T["bg_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}}
[data-testid="stMetric"]::after {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, {T["accent_green"]}22, transparent);
}}
[data-testid="stMetric"]:hover {{
    border-color: {T["border_accent"]}55 !important;
    box-shadow: {T["shadow"]} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {T["text_secondary"]} !important;
    font-size: 0.72rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}}
[data-testid="stMetricValue"] {{
    color: {T["text_primary"]} !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.03em !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.8rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ── Chart containers ──────────────────────────────── */
.chart-container {{
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 1.25rem 1.25rem 0.5rem;
    margin-bottom: 1.25rem;
    box-shadow: {T["shadow"]};
}}

/* ── Input field ───────────────────────────────────── */
[data-testid="stTextInput"] input {{
    background: {T["bg_input"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    color: {T["text_primary"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    padding: 0.65rem 1rem !important;
    height: 48px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {T["accent_green"]} !important;
    box-shadow: 0 0 0 3px {T["rail_glow"]} !important;
    outline: none !important;
}}
[data-testid="stTextInput"] input::placeholder {{
    color: {T["text_muted"]} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
    font-size: 0.88rem !important;
}}

/* ── Primary button ────────────────────────────────── */
[data-testid="stButton"] button[kind="primary"],
[data-testid="baseButton-primary"] {{
    background: {T["accent_green"]} !important;
    color: {T["text_on_green"]} !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    height: 48px !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.18s, transform 0.12s !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="baseButton-primary"]:hover {{
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stButton"] button[kind="primary"]:active {{
    transform: translateY(0) scale(0.98) !important;
}}

/* ── Secondary button ──────────────────────────────── */
[data-testid="stButton"] button[kind="secondary"],
[data-testid="baseButton-secondary"] {{
    background: {T["bg_card"]} !important;
    color: {T["text_secondary"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    height: 48px !important;
    transition: border-color 0.2s, color 0.2s !important;
}}
[data-testid="stButton"] button[kind="secondary"]:hover {{
    border-color: {T["text_secondary"]} !important;
    color: {T["text_primary"]} !important;
}}

/* ── Link buttons ──────────────────────────────────── */
[data-testid="stLinkButton"] a {{
    background: {T["bg_card"]} !important;
    color: {T["accent_blue"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.85rem !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stLinkButton"] a:hover {{
    border-color: {T["accent_blue"]} !important;
}}

/* ── Progress bar ──────────────────────────────────── */
[data-testid="stProgressBar"] > div {{
    background: {T["border"]} !important;
    border-radius: 4px !important;
}}
[data-testid="stProgressBar"] > div > div {{
    background: linear-gradient(90deg, {T["accent_blue"]}, {T["accent_green"]}) !important;
    border-radius: 4px !important;
}}

/* ── Spinner ───────────────────────────────────────── */
[data-testid="stSpinner"] p {{
    color: {T["text_secondary"]} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
}}

/* ── Info / warning boxes ──────────────────────────── */
[data-testid="stAlert"] {{
    background: {T["bg_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    color: {T["text_secondary"]} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}}

/* ── Dataframe ─────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}
[data-testid="stDataFrame"] th {{
    background: {T["bg_surface"]} !important;
    color: {T["text_secondary"]} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    border-bottom: 1px solid {T["border"]} !important;
}}
[data-testid="stDataFrame"] td {{
    background: {T["bg_card"]} !important;
    color: {T["text_primary"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid {T["border"]} !important;
}}

/* ── Expander ──────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: {T["bg_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}}
[data-testid="stExpander"] summary {{
    color: {T["text_primary"]} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
}}
[data-testid="stExpander"] summary:hover {{
    background: {T["bg_card_hover"]} !important;
}}

/* ── Divider ───────────────────────────────────────── */
hr {{
    border: none !important;
    border-top: 1px solid {T["border"]} !important;
    margin: 1.75rem 0 !important;
}}

/* ── Caption ───────────────────────────────────────── */
[data-testid="stCaptionContainer"] {{
    color: {T["text_muted"]} !important;
    font-size: 0.75rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

/* ── Custom signal badge ───────────────────────────── */
.signal-wrap {{
    display: flex;
    justify-content: center;
    margin: 1.25rem 0;
}}
.signal-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 0.85rem 2.5rem;
    border-radius: 12px;
    border: 1px solid;
    position: relative;
    overflow: hidden;
}}
.signal-badge::before {{
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.06;
    background: radial-gradient(ellipse at 30% 50%, white, transparent 70%);
}}

/* ── News card ─────────────────────────────────────── */
.news-card {{
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 10px;
    padding: 1rem 1.15rem;
    margin-bottom: 0.65rem;
    transition: border-color 0.18s, box-shadow 0.18s, transform 0.15s;
    position: relative;
    overflow: hidden;
}}
.news-card::before {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: {T["border"]};
    border-radius: 0 2px 2px 0;
    transition: background 0.2s;
}}
.news-card:hover {{
    border-color: {T["border_accent"]}55;
    box-shadow: 0 4px 20px {T["rail_glow"]}20;
    transform: translateX(2px);
}}
.news-card.positive::before {{ background: {T["accent_green"]}; }}
.news-card.negative::before {{ background: {T["accent_red"]}; }}
.news-card.neutral::before  {{ background: {T["text_muted"]}; }}
.news-card-header {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.4rem;
}}
.news-card-title {{
    font-size: 0.9rem;
    font-weight: 500;
    color: {T["text_primary"]};
    line-height: 1.45;
    flex: 1;
}}
.news-card-meta {{
    font-size: 0.75rem;
    color: {T["text_muted"]};
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.35rem;
}}
.news-card-meta .dot {{
    width: 3px; height: 3px;
    border-radius: 50%;
    background: {T["text_muted"]};
    display: inline-block;
}}
.sentiment-pill {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    padding: 2px 9px;
    border-radius: 999px;
    letter-spacing: 0.03em;
}}
.pill-positive {{
    background: {T["pos_pill_bg"]};
    color: {T["accent_green"]};
    border: 1px solid {T["accent_green"]}33;
}}
.pill-negative {{
    background: {T["neg_pill_bg"]};
    color: {T["accent_red"]};
    border: 1px solid {T["accent_red"]}33;
}}
.pill-neutral {{
    background: {T["neu_pill_bg"]};
    color: {T["text_secondary"]};
    border: 1px solid {T["border"]};
}}

/* ── Forecast table enhancements ───────────────────── */
.forecast-row-positive {{ color: {T["accent_green"]} !important; }}
.forecast-row-negative {{ color: {T["accent_red"]} !important; }}

/* ── Stats bar (sentiment) ─────────────────────────── */
.sentiment-bar-wrap {{
    margin: 0.75rem 0 1.5rem;
}}
.sentiment-bar-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 0.73rem;
    font-family: 'Space Grotesk', sans-serif;
    color: {T["text_muted"]};
    margin-bottom: 0.35rem;
}}
.sentiment-bar {{
    display: flex;
    height: 6px;
    border-radius: 3px;
    overflow: hidden;
    gap: 2px;
}}
.sb-pos {{ background: {T["accent_green"]}; border-radius: 3px 0 0 3px; }}
.sb-neu {{ background: {T["text_muted"]}; }}
.sb-neg {{ background: {T["accent_red"]}; border-radius: 0 3px 3px 0; }}

/* ── Driver grid ───────────────────────────────────── */
.driver-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 0.65rem;
    margin-bottom: 1rem;
}}

/* ── Disclaimer ────────────────────────────────────── */
.disclaimer {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: {"rgba(245,166,35,0.07)" if is_dark else "rgba(192,123,0,0.06)"};
    border: 1px solid {T["accent_amber"]}33;
    border-radius: 8px;
    padding: 0.65rem 1rem;
    font-size: 0.78rem;
    color: {T["accent_amber"]};
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    margin: 1rem 0;
}}
</style>
""", unsafe_allow_html=True)


# ── Plotly chart theme helper ──────────────────────────────────────────────────
def chart_layout(title: str, height: int = 380, **kwargs) -> dict:
    return dict(
        title=dict(text=title, font=dict(
            family="Space Grotesk, sans-serif", size=14,
            color=T["text_secondary"],
        )),
        template=T["plotly_theme"],
        height=height,
        paper_bgcolor=T["chart_paper"],
        plot_bgcolor=T["chart_bg"],
        margin=dict(l=0, r=0, t=44, b=0),
        xaxis=dict(gridcolor=T["chart_grid"], linecolor=T["border"],
                   tickfont=dict(family="JetBrains Mono", size=10, color=T["text_muted"])),
        yaxis=dict(gridcolor=T["chart_grid"], linecolor=T["border"],
                   tickfont=dict(family="JetBrains Mono", size=10, color=T["text_muted"])),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(family="Space Grotesk", size=11,
                      color=T["text_secondary"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(family="Space Grotesk, sans-serif",
                  color=T["text_secondary"]),
        hoverlabel=dict(
            bgcolor=T["bg_card"],
            bordercolor=T["border"],
            font=dict(family="JetBrains Mono", size=12,
                      color=T["text_primary"]),
        ),
        **kwargs,
    )


# ── Helper: signal badge HTML ──────────────────────────────────────────────────
def signal_badge_html(signal: str, color: str) -> str:
    sig_lower = signal.lower()
    if "buy" in sig_lower:
        bg = T["badge_buy_bg"]
        bd = T["badge_buy_bd"]
        col = T["accent_green"]
        ico = icon("trending-up", 22, T["accent_green"])
    elif "sell" in sig_lower:
        bg = T["badge_sell_bg"]
        bd = T["badge_sell_bd"]
        col = T["accent_red"]
        ico = icon("trending-down", 22, T["accent_red"])
    else:
        bg = T["badge_hold_bg"]
        bd = T["badge_hold_bd"]
        col = T["accent_amber"]
        ico = icon("minus-circle", 22, T["accent_amber"])
    return f"""
<div class="signal-wrap">
  <div class="signal-badge" style="background:{bg}; border-color:{bd}; color:{col};">
    {ico}&nbsp;{signal}
  </div>
</div>
"""


# ── Helper: sentiment pill HTML ────────────────────────────────────────────────
def pill_html(label: str) -> str:
    l = label.lower()
    if "positive" in l:
        cls = "pill-positive"
    elif "negative" in l:
        cls = "pill-negative"
    else:
        cls = "pill-neutral"
    ico = sentiment_icon(label)
    return f'<span class="sentiment-pill {cls}">{ico}&nbsp;{label}</span>'


# ── Helper: news card HTML ─────────────────────────────────────────────────────
def news_card_html(article: dict, *, show_link: bool = True) -> str:
    label = article.get("sentiment_label", "Neutral")
    l = label.lower()
    cls = "positive" if "positive" in l else (
        "negative" if "negative" in l else "neutral")
    score = article.get("sentiment_score", 0)
    url = article.get("url", "")
    link = (
        f'<a href="{url}" target="_blank" rel="noopener" '
        f'style="display:inline-flex;align-items:center;gap:4px;font-size:0.75rem;'
        f'color:{T["accent_blue"]};text-decoration:none;font-family:Space Grotesk,sans-serif;'
        f'font-weight:500;margin-top:0.35rem;">'
        f'{icon("external-link", 12, T["accent_blue"])} Read article</a>'
        if url and show_link else ""
    )
    return f"""
<div class="news-card {cls}">
  <div class="news-card-header">
    <div class="news-card-title">{article.get("title","")}</div>
  </div>
  <div class="news-card-meta">
    {article.get("publisher","")}
    <span class="dot"></span>
    {article.get("published_at","")}
    <span class="dot"></span>
    {pill_html(label)}
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:{T["text_muted"]};">
      {score:+.3f}
    </span>
  </div>
  {link}
</div>
"""


# ── Helper: section header ─────────────────────────────────────────────────────
def rail_header(title: str, ico: str | None = None) -> None:
    ico_html = f"&nbsp;{ico}&nbsp;" if ico else ""
    st.markdown(f"""
<div class="rail-header">
  <span class="rail-header-title">{ico_html}{title}</span>
  <span class="rail-header-line"></span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TOP NAV
# ══════════════════════════════════════════════════════════════════════════════
toggle_icon = icon("sun", 15, T["accent_amber"]) if is_dark else icon(
    "moon", 15, T["accent_blue"])
toggle_label = "Light mode" if is_dark else "Dark mode"

nav_left, nav_right = st.columns([6, 1])
with nav_left:
    st.markdown(f"""
<div class="topnav">
  <div>
    <div class="topnav-brand">
      <span class="brand-dot"></span>Foresight
    </div>
    <div class="topnav-sub">LSTM &nbsp;·&nbsp; 2-year window &nbsp;·&nbsp; 7-day forecast</div>
  </div>
</div>
""", unsafe_allow_html=True)

with nav_right:
    st.markdown("<div style='padding-top:1.35rem;'>", unsafe_allow_html=True)
    if st.button(f"{toggle_label}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH ROW
# ══════════════════════════════════════════════════════════════════════════════
col_input, col_btn = st.columns([5, 1])
with col_input:
    ticker = st.text_input(
        "Ticker",
        value="AAPL",
        placeholder="Ticker symbol — AAPL · TSLA · 600519.SS",
        label_visibility="collapsed",
    ).strip().upper()
with col_btn:
    run = st.button("Run analysis", type="primary", use_container_width=True)

if not run:
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.65rem;margin-top:1.5rem;padding:1rem 1.2rem;
background:{T["bg_card"]};border:1px solid {T["border"]};border-radius:10px;
font-size:0.88rem;color:{T["text_secondary"]};font-family:Inter,sans-serif;">
  {icon("info", 16, T["text_muted"])}
  Enter a ticker symbol and click <strong style="color:{T["text_primary"]};font-family:Space Grotesk,sans-serif;">
  Run analysis</strong> to generate a 7-day LSTM forecast with news sentiment.
</div>
""", unsafe_allow_html=True)
    st.stop()

if not ticker:
    st.error("Please enter a ticker symbol.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCH
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner(f"Fetching 2-year market data for {ticker}…"):
    try:
        df = fetch_stock_data(ticker)
        info = get_stock_info(ticker)
    except ValueError as e:
        st.error(str(e))
        st.stop()

prices = df["Close"].values.astype(float)
dates = df.index.tz_localize(None) if df.index.tzinfo else df.index
currency = info["currency"]
current_price = info["current_price"]


# ══════════════════════════════════════════════════════════════════════════════
#  STOCK HEADER + METRICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:1.5rem 0 0.25rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.55rem;
    font-weight:700;color:{T["text_primary"]};letter-spacing:-0.02em;line-height:1.2;">
    {info["name"]}
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
    color:{T["text_muted"]};margin-top:2px;letter-spacing:0.08em;">
    {ticker} &nbsp;&nbsp;·&nbsp;&nbsp; {currency}
  </div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Current price",
          f"{currency} {current_price:.2f}" if current_price else "N/A")
m2.metric("Data points",     f"{len(prices)} days")
m3.metric("2Y high",         f"{currency} {prices.max():.2f}")
m4.metric("2Y low",          f"{currency} {prices.min():.2f}")

st.markdown("<hr/>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 1: HISTORICAL PRICE
# ══════════════════════════════════════════════════════════════════════════════
rail_header("Historical closing price — 2 years",
            icon("activity", 14, T["text_muted"]))
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=dates, y=prices,
    mode="lines", name="Close",
    line=dict(color=T["accent_blue"], width=1.6),
    fill="tozeroy",
    fillcolor=f"rgba({int(T['accent_blue'][1:3],16)},{int(T['accent_blue'][3:5],16)},{int(T['accent_blue'][5:7],16)},0.07)",
    hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f} " +
    currency + "<extra></extra>",
))
fig1.update_layout(**chart_layout("", height=340))
st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig1, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LSTM TRAINING
# ══════════════════════════════════════════════════════════════════════════════
rail_header("LSTM model training", icon("brain", 14, T["text_muted"]))
progress_bar = st.progress(0)
status_text = st.empty()


def on_epoch(epoch, total):
    progress_bar.progress(epoch / total)
    status_text.markdown(
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.82rem;'
        f'color:{T["text_muted"]};">Training &nbsp;·&nbsp; epoch {epoch} / {total}</span>',
        unsafe_allow_html=True,
    )


result = run_prediction(df, future_days=7, epoch_callback=on_epoch)
progress_bar.progress(1.0)
status_text.markdown(
    f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.82rem;color:{T["accent_green"]};">'
    f'{icon("check-circle", 14, T["accent_green"])} &nbsp;Training complete</span>',
    unsafe_allow_html=True,
)

test_preds = result["test_preds"]
test_start = result["test_start_idx"]
train_end = result["train_end_idx"]
future_preds = result["future_preds"]
test_dates = dates[test_start:]
predicted_return_pct = (future_preds[-1] - current_price) / current_price * 100


# ══════════════════════════════════════════════════════════════════════════════
#  FORECAST SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<hr/>", unsafe_allow_html=True)
rail_header("Forecast summary")

c1, c2 = st.columns(2)
c1.metric(
    "Expected return — 7 days",
    f"{predicted_return_pct:+.2f}%",
    delta=f"{predicted_return_pct:+.2f}%",
)
c2.metric(
    f"Predicted price — day 7",
    f"{currency} {future_preds[-1]:.2f}",
)
st.markdown("<hr/>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 2: ACTUAL VS PREDICTED
# ══════════════════════════════════════════════════════════════════════════════
rail_header("Model fit — actual vs predicted",
            icon("layers", 14, T["text_muted"]))
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=dates, y=prices,
    mode="lines", name="Actual",
    line=dict(color=T["accent_blue"], width=1.6),
    hovertemplate="<b>%{x|%b %d %Y}</b><br>Actual: %{y:.2f}<extra></extra>",
))
fig2.add_trace(go.Scatter(
    x=test_dates, y=test_preds,
    mode="lines", name="Predicted",
    line=dict(color=T["accent_green"], width=1.6, dash="dot"),
    hovertemplate="<b>%{x|%b %d %Y}</b><br>Predicted: %{y:.2f}<extra></extra>",
))
fig2.add_vline(
    x=dates[train_end],
    line_dash="dot",
    line_color=T["text_muted"],
    annotation_text="Train / Test split",
    annotation_position="top left",
    annotation_font=dict(color=T["text_muted"],
                         size=11, family="Space Grotesk"),
)
fig2.update_layout(**chart_layout("", height=400))
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig2, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 3: 7-DAY FORECAST
# ══════════════════════════════════════════════════════════════════════════════
rail_header("7-day price forecast", icon("chart-line", 14, T["text_muted"]))
last_date = pd.Timestamp(dates[-1])
future_dates = pd.bdate_range(start=last_date + timedelta(days=1), periods=7)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=dates[-60:], y=prices[-60:],
    mode="lines", name="Last 60 days",
    line=dict(color=T["accent_blue"], width=1.6),
    hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f}<extra></extra>",
))
fig3.add_trace(go.Scatter(
    x=[dates[-1], future_dates[0]],
    y=[prices[-1], future_preds[0]],
    mode="lines", showlegend=False,
    line=dict(color=T["accent_green"], width=1.2, dash="dot"),
))
fig3.add_trace(go.Scatter(
    x=future_dates, y=future_preds,
    mode="lines+markers", name="7-day forecast",
    line=dict(color=T["accent_green"], width=2.2),
    marker=dict(size=8, symbol="circle", color=T["accent_green"],
                line=dict(color=T["bg_base"], width=2)),
    hovertemplate="<b>%{x|%b %d %Y}</b><br>Forecast: %{y:.2f}<extra></extra>",
))
fig3.add_vrect(
    x0=future_dates[0], x1=future_dates[-1],
    fillcolor=T["accent_green"], opacity=0.04,
    layer="below", line_width=0,
)
fig3.update_layout(**chart_layout("", height=380))
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig3, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FORECAST TABLE
# ══════════════════════════════════════════════════════════════════════════════
rail_header("7-day forecast details", icon("calendar", 14, T["text_muted"]))
prev_prices = [prices[-1]] + list(future_preds[:-1])
forecast_df = pd.DataFrame({
    "Date":                        future_dates.strftime("%Y-%m-%d"),
    f"Predicted price ({currency})": [f"{p:.2f}" for p in future_preds],
    "Daily change":                [
        f"{(future_preds[i] - prev_prices[i]) / prev_prices[i] * 100:+.2f}%"
        for i in range(7)
    ],
    "vs today":                    [
        f"{(future_preds[i] - current_price) / current_price * 100:+.2f}%"
        for i in range(7)
    ],
})
st.dataframe(forecast_df, use_container_width=True, hide_index=True)

st.markdown(f"""
<div class="disclaimer">
  {icon("alert", 14, T["accent_amber"])}
  For educational and research purposes only — not investment advice.
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  NEWS SENTIMENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<hr/>", unsafe_allow_html=True)
rail_header("News & sentiment analysis", icon(
    "newspaper", 14, T["text_muted"]))

with st.spinner("Fetching latest news and analysing sentiment…"):
    news_result = get_news_sentiment(ticker)
    rec = generate_recommendation(
        current_price, list(future_preds), news_result)

# Signal badge
st.markdown(signal_badge_html(rec["signal"],
            rec["color"]), unsafe_allow_html=True)

# Recommendation metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Combined score",     f"{rec['combined_score']:+.2f}")
c2.metric("Forecast return",    f"{rec['price_change_pct']:+.2f}%")
c3.metric("News sentiment",     news_result["sentiment_label"])
c4.metric("Articles analysed",  (
    f"{news_result['positive_count']} pos  "
    f"{news_result['neutral_count']} neu  "
    f"{news_result['negative_count']} neg"
))

# Rationale
st.markdown(f"""
<div style="margin:1rem 0;padding:1rem 1.2rem;background:{T["bg_card"]};
border:1px solid {T["border"]};border-radius:10px;
font-size:0.88rem;line-height:1.65;color:{T["text_secondary"]};
font-family:Inter,sans-serif;">
{rec["rationale"]}
</div>
""", unsafe_allow_html=True)

# Sentiment bar
total = (
    news_result["positive_count"]
    + news_result["neutral_count"]
    + news_result["negative_count"]
)
if total:
    pos_pct = news_result["positive_count"] / total * 100
    neu_pct = news_result["neutral_count"] / total * 100
    neg_pct = news_result["negative_count"] / total * 100
    st.markdown(f"""
<div class="sentiment-bar-wrap">
  <div class="sentiment-bar-labels">
    <span>{news_result["positive_count"]} positive</span>
    <span>{news_result["neutral_count"]} neutral</span>
    <span>{news_result["negative_count"]} negative</span>
  </div>
  <div class="sentiment-bar">
    <div class="sb-pos" style="width:{pos_pct:.1f}%;"></div>
    <div class="sb-neu" style="width:{neu_pct:.1f}%;"></div>
    <div class="sb-neg" style="width:{neg_pct:.1f}%;"></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TOP MARKET DRIVERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<hr/>", unsafe_allow_html=True)
rail_header("Top market drivers")

SENTIMENT_STYLES = {
    "Very Positive": ("#2ECC71", "#0d2e1a"),
    "Positive":      ("#58D68D", "#0d2e1a"),
    "Neutral":       ("#8b949e", "#1c2128"),
    "Negative":      ("#F39C12", "#2e1f0d"),
    "Very Negative": ("#E74C3C", "#2e0d0d"),
}

drivers = extract_market_drivers(news_result)

st.markdown('<div class="driver-grid">', unsafe_allow_html=True)
for article in drivers:
    st.markdown(news_card_html(article, show_link=True),
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ALL RECENT ARTICLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<hr/>", unsafe_allow_html=True)
rail_header("All recent articles")

for article in news_result["articles"]:
    label = article.get("sentiment_label", "Neutral")
    l = label.lower()
    ico = sentiment_icon(label)

    with st.expander(article.get("title", "Article")):
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"""
<div style="font-size:0.85rem;line-height:1.7;color:{T["text_secondary"]};font-family:Inter,sans-serif;">
  <span style="color:{T["text_muted"]};font-family:'Space Grotesk',sans-serif;font-size:0.72rem;
  text-transform:uppercase;letter-spacing:0.07em;">Publisher</span><br>
  <span style="color:{T["text_primary"]};">{article.get("publisher","—")}</span>
  <br><br>
  <span style="color:{T["text_muted"]};font-family:'Space Grotesk',sans-serif;font-size:0.72rem;
  text-transform:uppercase;letter-spacing:0.07em;">Published</span><br>
  <span style="color:{T["text_primary"]};">{article.get("published_at","—")}</span>
  <br><br>
  <span style="color:{T["text_muted"]};font-family:'Space Grotesk',sans-serif;font-size:0.72rem;
  text-transform:uppercase;letter-spacing:0.07em;">Sentiment</span><br>
  {pill_html(label)}
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:{T["text_muted"]};margin-left:8px;">
    score {article.get("sentiment_score", 0):+.3f}
  </span>
</div>
""", unsafe_allow_html=True)
        with col_b:
            if article.get("url"):
                st.link_button("Open article", article["url"])
>>>>>>> Stashed changes
