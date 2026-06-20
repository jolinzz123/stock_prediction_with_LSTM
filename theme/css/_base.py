def css_base(T: dict) -> str:
    return f"""
/* ── Page background sync ─ */
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
section[data-testid="stSidebar"],
.main .block-container {{
    background-color: {T["bg_base"]} !important;
    color: {T["text_primary"]} !important;
}}
[data-testid="stHeader"] {{
    background-color: {T["bg_base"]} !important;
}}
[data-testid="stBottomBlockContainer"] {{
    background-color: {T["bg_base"]} !important;
}}

/* ── Section rail header ─ */
.rail-header {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 1.1rem;
}}
.rail-bar {{
    width: 3px; height: 16px;
    border-radius: 2px;
    background: {T["accent_blue"]};
    box-shadow: 0 0 8px {T["glow_blue"]};
    flex-shrink: 0;
}}
.rail-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    color: {T["text_secondary"]};
    letter-spacing: 0.09em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}}
.rail-line {{
    flex: 1;
    height: 1px;
    background: {T["border"]};
}}

/* ── Column alignment ─ */
[data-testid="stHorizontalBlock"] {{
    align-items: stretch !important;
    gap: 0.5rem !important;
}}
[data-testid="stHorizontalBlock"]:has([data-testid="stTextInput"]) {{
    align-items: end !important;
}}
[data-testid="stHorizontalBlock"] [data-testid="stTextInput"],
[data-testid="stHorizontalBlock"] [data-testid="stButton"] {{
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}}

hr {{ border: none !important; border-top: 1px solid {T["border"]} !important; margin: 1.75rem 0 !important; }}
"""
