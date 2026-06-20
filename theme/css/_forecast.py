def css_forecast(T: dict, is_dark: bool) -> str:
    return f"""
/* ── Custom HTML forecast table ─ */
.forecast-table-wrap {{
    border: 1px solid {T["border"]};
    border-radius: 14px;
    overflow: hidden;
    background: {
        'linear-gradient(160deg, #0F1D2E 0%, #0A1520 60%, #0D1F30 100%)' if is_dark else T["bg_card"]};
    position: relative;
    box-shadow: {'0 0 0 1px rgba(76,155,232,0.08), 0 8px 32px rgba(0,0,0,0.4)' if is_dark else T["shadow"]};
    margin-bottom: 1.25rem;
}}
.forecast-table-wrap::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {T["accent_blue"]}, {T["accent_green"]}80, transparent);
    z-index: 1;
}}
{'/* dark-mode ambient glow */ .forecast-table-wrap::after { content: ""; position: absolute; top: -40px; left: 50%; transform: translateX(-50%); width: 60%; height: 60px; background: radial-gradient(ellipse, rgba(76,155,232,0.12) 0%, transparent 70%); pointer-events: none; z-index: 0; }' if is_dark else ''}
.forecast-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    position: relative;
    z-index: 1;
}}
.forecast-table thead tr {{
    background: {'rgba(76,155,232,0.06)' if is_dark else T["bg_surface"]};
    border-bottom: 1px solid {T["border"]};
}}
.forecast-table th {{
    padding: 0.75rem 1.2rem;
    text-align: left;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: {T["text_muted"]};
    white-space: nowrap;
}}
.forecast-table th:not(:first-child) {{
    text-align: right;
}}
.forecast-table tbody tr {{
    border-bottom: 1px solid {T["border"] if not is_dark else "rgba(30,45,61,0.7)"};
    transition: background 0.15s;
}}
.forecast-table tbody tr:nth-child(odd) {{
    background: {
        'rgba(76,155,232,0.03)' if is_dark else 'rgba(26,114,204,0.025)'};
}}
.forecast-table tbody tr:nth-child(even) {{
    background: {'rgba(46,204,113,0.025)' if is_dark else 'transparent'};
}}
.forecast-table tbody tr:last-child {{
    border-bottom: none;
}}
.forecast-table tbody tr:hover {{
    background: {'rgba(76,155,232,0.09)' if is_dark else T["bg_card_hover"]} !important;
}}
.forecast-table td {{
    padding: 0.78rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.83rem;
    color: {T["text_primary"]};
    white-space: nowrap;
}}
.forecast-table td:not(:first-child) {{
    text-align: right;
}}
.forecast-table td.date-col {{
    color: {T["text_secondary"]};
    font-size: 0.8rem;
    {'border-left: 2px solid rgba(76,155,232,0.15);' if is_dark else ''}
}}
.forecast-table td.chg-pos {{
    color: {T["accent_green"]};
    {'text-shadow: 0 0 12px rgba(46,204,113,0.4);' if is_dark else ''}
}}
.forecast-table td.chg-neg {{
    color: {T["accent_red"]};
    {'text-shadow: 0 0 12px rgba(255,77,109,0.4);' if is_dark else ''}
}}
.forecast-table td.chg-neu {{ color: {T["text_muted"]}; }}

/* ── Forecast summary cards ─ */
.forecast-summary-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin-bottom: 1rem;
}}
.fsc {{
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.fsc:hover {{
    border-color: {T["border_accent"]}55;
    box-shadow: {T["shadow"]};
}}
.fsc-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {T["text_secondary"]};
    margin-bottom: 0.55rem;
}}
.fsc-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: {T["text_primary"]};
    display: flex;
    align-items: center;
    gap: 0.4rem;
    line-height: 1.2;
}}
"""
