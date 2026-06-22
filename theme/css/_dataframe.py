def css_dataframe(T: dict) -> str:
    return f"""
/* ── Dataframe ─ */
[data-testid="stDataFrame"] {{
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: {T["bg_card"]} !important;
}}
[data-testid="stDataFrame"] > div {{
    background: {T["bg_card"]} !important;
    border-radius: 12px !important;
}}
[data-testid="stDataFrame"] table {{
    background: {T["bg_surface"]} !important;
    border-collapse: collapse !important;
    width: 100% !important;
}}
[data-testid="stDataFrame"] thead th {{
    background: {T["bg_surface"]} !important;
    color: {T["text_primary"]} !important;
    border-bottom: 1px solid {T["border"]} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1rem !important;
}}
[data-testid="stDataFrame"] tbody td {{
    background: {T["bg_card"]} !important;
    color: {T["text_primary"]} !important;
    border-bottom: 1px solid {T["border"]} !important;
    padding: 0.55rem 1rem !important;
    font-size: 0.84rem !important;
}}
[data-testid="stDataFrame"] tbody tr:hover td {{
    background: {T["bg_card_hover"]} !important;
}}
[data-testid="stDataFrame"] tbody tr:last-child td {{
    border-bottom: none !important;
}}

/* ── Progress bar ─ */
[data-testid="stProgressBar"] > div {{
    background: {T["border"]} !important;
    border-radius: 4px !important;
}}
[data-testid="stProgressBar"] > div > div {{
    background: linear-gradient(90deg, {T["accent_blue"]}, {T["accent_green"]}) !important;
    border-radius: 4px !important;
}}

/* ── Alert / info ─ */
[data-testid="stAlert"] {{
    background: {T["bg_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    color: {T["text_secondary"]} !important;
    font-size: 0.88rem !important;
}}

/* ── Expander ─ */
[data-testid="stExpander"] {{
    background: {T["bg_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}}
[data-testid="stExpander"] summary {{
    color: {T["text_primary"]} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.75rem 1rem !important;
}}
"""
