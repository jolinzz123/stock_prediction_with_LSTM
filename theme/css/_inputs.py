def css_inputs(T: dict) -> str:
    return f"""
/* ── Inputs ─ */
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] input[type="text"],
.stTextInput input {{
    background: {T["bg_input"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    color: {T["text_primary"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    height: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    line-height: 44px !important;
    box-sizing: border-box !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
[data-testid="stTextInput"] label,
.stTextInput label {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
[data-testid="stTextInput"] div[data-testid="InputInstructions"],
[data-testid="stTextInput"] .stTextInput-instructions {{
    display: none !important;
}}

/* ── Primary button height match ─ */
[data-testid="stButton"] button[kind="primary"],
[data-testid="baseButton-primary"] {{
    min-height: 44px !important;
    max-height: 44px !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {T["accent_blue"]} !important;
    box-shadow: 0 0 0 3px {T["glow_blue"]} !important;
    outline: none !important;
}}
[data-testid="stTextInput"] input::placeholder {{
    color: {T["text_muted"]} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
    font-size: 0.87rem !important;
}}
"""
