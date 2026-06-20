def css_metrics(T: dict) -> str:
    return f"""
/* ── Metric cards ─ */
[data-testid="stMetric"] {{
    background: {T["bg_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
    height: 100% !important;
    box-sizing: border-box !important;
}}
[data-testid="stMetric"]::after {{
    display: none !important;
}}
[data-testid="stMetric"]:hover {{
    border-color: {T["border_accent"]}55 !important;
    box-shadow: {T["shadow"]} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {T["text_secondary"]} !important;
    font-size: 0.72rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}}
[data-testid="stMetricValue"] {{
    color: {T["text_primary"]} !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.03em !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.03em !important;
}}
"""
