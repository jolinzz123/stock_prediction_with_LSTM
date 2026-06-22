def css_buttons(T: dict) -> str:
    return f"""
/* ── Buttons ─ */
[data-testid="stButton"] button[kind="primary"],
[data-testid="baseButton-primary"] {{
    background: {T["accent_blue"]} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0 1rem !important;
    height: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    line-height: 44px !important;
    box-sizing: border-box !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 14px {T["glow_blue"]} !important;
    transition: opacity 0.18s, transform 0.12s !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover {{
    opacity: 0.87 !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stButton"] button[kind="secondary"],
[data-testid="baseButton-secondary"] {{
    background: {T["bg_card"]} !important;
    color: {T["text_secondary"]} !important;
    border: 2px solid {T["border"]} !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    transition: border-color 0.18s, color 0.18s, background 0.18s, box-shadow 0.18s !important;
}}
[data-testid="stButton"] button[kind="secondary"]:hover {{
    border-color: {T["accent_blue"]} !important;
    color: {T["accent_blue"]} !important;
    background: rgba(76,155,232,0.08) !important;
    box-shadow: 0 0 0 3px rgba(76,155,232,0.25) !important;
}}
[data-testid="stButton"] button[kind="secondary"]:focus,
[data-testid="stButton"] button[kind="secondary"]:active,
[data-testid="stButton"] button[kind="secondary"]:focus-visible,
[data-testid="stButton"] button:focus,
[data-testid="stButton"] button:active,
[data-testid="stButton"] button:focus-visible,
[data-testid="baseButton-secondary"]:focus,
[data-testid="baseButton-secondary"]:active {{
    border-color: {T["accent_blue"]} !important;
    border-width: 2px !important;
    box-shadow: 0 0 0 4px rgba(76,155,232,0.45), 0 0 20px rgba(76,155,232,0.30) !important;
    background: rgba(76,155,232,0.12) !important;
    outline: none !important;
    color: {T["accent_blue"]} !important;
}}

/* ── Link buttons ─ */
[data-testid="stLinkButton"] a {{
    background: {T["bg_card"]} !important;
    color: {T["accent_blue"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 0.38rem 0.85rem !important;
    transition: border-color 0.18s !important;
}}
[data-testid="stLinkButton"] a:hover {{
    border-color: {T["accent_blue"]} !important;
}}
"""
