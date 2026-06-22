def css_widgets(T: dict, is_dark: bool) -> str:
    return f"""
/* ── Watchlist table ─ */
.wl-wrap {{
    border: 1px solid {T["wl_border"]};
    border-radius: 12px;
    overflow: hidden;
    margin-top: 0.5rem;
}}
.wl-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.83rem;
}}
.wl-table th {{
    text-align: right;
    color: {T["text_muted"]};
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.7rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid {T["border"]};
    background: {T["bg_surface"]};
    white-space: nowrap;
}}
.wl-table th:first-child {{ text-align: left; }}
.wl-table td {{
    padding: 0;
    border-bottom: 1px solid {T["border"]};
    text-align: right;
    vertical-align: middle;
    color: {T["text_primary"]};
    font-family: 'JetBrains Mono', monospace;
    background: {T["bg_card"]};
    white-space: nowrap;
}}
.wl-table td:first-child {{ text-align: left; font-family: 'Inter', sans-serif; }}
.wl-table tr:last-child td {{ border-bottom: none; }}
.wl-table tbody tr:hover td {{ background: {T["wl_hover"]}; cursor: pointer; }}
.wl-ticker {{ font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.88rem; color: {T["text_primary"]}; }}
.wl-name {{ color: {T["text_muted"]}; font-size: 0.72rem; font-family: 'Inter', sans-serif; margin-top: 1px; }}
.wl-up {{ color: {T["accent_green"]}; }}
.wl-dn {{ color: {T["accent_red"]}; }}
.wl-neutral {{ color: {T["text_muted"]}; }}
.wl-cell-link {{
    display: block;
    width: 100%;
    height: 100%;
    padding: 0.75rem 1rem;
    text-decoration: none !important;
    color: inherit !important;
    font-family: inherit;
    font-size: inherit;
    font-weight: inherit;
}}
.wl-cell-link:hover {{
    color: inherit !important;
    text-decoration: none !important;
}}

/* ── Signal badge ─ */
.signal-wrap {{ display:flex; justify-content:center; margin: 1.25rem 0; }}
.signal-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    padding: 0.8rem 2.4rem;
    border-radius: 12px;
    border: 1px solid;
    position: relative;
    overflow: hidden;
}}
.signal-badge::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 30% 50%, rgba(255,255,255,0.07), transparent 70%);
    pointer-events: none;
}}

/* ── Recommendation narrative box ─ */
.rec-box {{
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    font-size: 0.9rem;
    line-height: 1.75;
    color: {T["text_secondary"]};
    font-family: 'Inter', sans-serif;
    margin: 1rem 0;
}}

/* ── Disclaimer ─ */
.disclaimer {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    background: {T["disclaimer_bg"]};
    border: 1px solid {T["accent_amber"]}33;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.76rem;
    color: {T["accent_amber"]};
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    margin: 0.85rem 0;
}}

/* ── Chart wrapper ─ */
.chart-wrap {{
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 1.8rem 1.2rem 0.4rem;
    margin-bottom: 0.5rem;
    box-shadow: {T["shadow"]};
}}

/* ── Watchlist ticker buttons ─ */
.wl-btn-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 1rem;
}}
.wl-btn {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 6px;
    border: 1px solid {T["border"]};
    background: {T["bg_card"]};
    color: {T["text_secondary"]};
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
}}
.wl-btn:hover {{
    border-color: {T["accent_blue"]}66;
    color: {T["text_primary"]};
}}

/* ── Stock header ─ */
.stock-header {{
    margin: 1.25rem 0 0.5rem;
}}
.stock-name {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: {T["text_primary"]};
    letter-spacing: -0.025em;
    line-height: 1.2;
}}
.stock-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: {T["text_muted"]};
    letter-spacing: 0.07em;
    margin-top: 3px;
}}

/* ── Info hint ─ */
.hint-box {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-top: 1.5rem;
    padding: 1rem 1.2rem;
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 10px;
    font-size: 0.87rem;
    color: {T["text_secondary"]};
    font-family: 'Inter', sans-serif;
}}

/* ── Market / Compare → underline tabs ─ */
.st-key-nav_market button,
.st-key-nav_compare button {{
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: {T["text_secondary"]} !important;
    font-weight: 600 !important;
    width: 100% !important;
}}
.st-key-nav_market button:hover,
.st-key-nav_compare button:hover {{
    background: transparent !important;
    color: {T["accent_blue"]} !important;
    border-bottom-color: {T["accent_blue"]}55 !important;
    box-shadow: none !important;
}}
.st-key-nav_market button:disabled,
.st-key-nav_compare button:disabled {{
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid {T["accent_green"]} !important;
    color: {T["accent_green"]} !important;
    opacity: 1 !important;
    border-radius: 0 !important;
}}
"""
