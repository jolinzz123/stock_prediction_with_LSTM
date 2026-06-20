def css_news(T: dict) -> str:
    return f"""
/* ── News card ─ */
.news-card {{
    background: {T["bg_card"]};
    border: 1px solid {T["border"]};
    border-radius: 10px;
    padding: 0.95rem 1.1rem 0.95rem 1.25rem;
    margin-bottom: 0.6rem;
    position: relative;
    transition: border-color 0.18s, transform 0.14s;
    overflow: hidden;
}}
.news-card::before {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 0 2px 2px 0;
    transition: background 0.2s;
}}
.news-card.pos::before {{ background: {T["accent_green"]}; }}
.news-card.neg::before {{ background: {T["accent_red"]}; }}
.news-card.neu::before {{ background: {T["text_muted"]}; }}
.news-card:hover {{
    border-color: {T["border_accent"]}55;
    transform: translateX(2px);
}}
.news-title {{
    font-size: 0.88rem;
    font-weight: 500;
    color: {T["text_primary"]};
    line-height: 1.45;
    margin-bottom: 0.38rem;
}}
.news-meta {{
    font-size: 0.73rem;
    color: {T["text_muted"]};
    display: flex;
    align-items: center;
    gap: 0.45rem;
    flex-wrap: wrap;
    font-family: 'Space Grotesk', sans-serif;
}}
.news-meta .sep {{ opacity: 0.5; }}
.sentiment-pill {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 0.69rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    padding: 1px 8px;
    border-radius: 999px;
    letter-spacing: 0.03em;
}}
.pill-pos {{ background: {T["pos_pill_bg"]}; color: {T["accent_green"]}; border: 1px solid {T["accent_green"]}33; }}
.pill-neg {{ background: {T["neg_pill_bg"]}; color: {T["accent_red"]}; border: 1px solid {T["accent_red"]}33; }}
.pill-neu {{ background: {T["neu_pill_bg"]}; color: {T["text_secondary"]}; border: 1px solid {T["border"]}; }}

/* ── Sentiment bar ─ */
.sbar-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: {T["text_muted"]};
    font-family: 'Space Grotesk', sans-serif;
    margin-bottom: 0.3rem;
}}
.sbar {{
    display: flex; height: 5px;
    border-radius: 3px; overflow: hidden; gap: 2px;
}}
.sbar-p {{ background: {T["accent_green"]}; border-radius: 3px 0 0 3px; }}
.sbar-n {{ background: {T["text_muted"]}; }}
.sbar-e {{ background: {T["accent_red"]}; border-radius: 0 3px 3px 0; }}
"""
