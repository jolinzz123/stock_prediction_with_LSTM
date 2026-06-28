import streamlit as st
import pandas as pd
from ticker_strip import render_ticker_strip
from comparator import compare_stocks
from charts import build_radar_chart, build_compare_forecast_chart
from theme import get_tokens, get_is_dark, icon, rail_header, render_nav


@st.cache_data(ttl=600, show_spinner=False)
def _cached_compare(ticker_a, ticker_b):
    return compare_stocks(ticker_a, ticker_b)


def _display_compare_results(report):
    T = get_tokens()
    ta = report["ticker_a"]
    tb = report["ticker_b"]
    sc = report["scores"]
    wr = report.get("winner")
    win_tag = wr.get("winner") if isinstance(wr, dict) else wr
    _tsec = T["text_secondary"]

    st.markdown("<hr/>", unsafe_allow_html=True)

    # === Winner banner + score boxes ===========================================
    if win_tag:
        bg_col = T["badge_buy_bg"]
        bd_col = T["badge_buy_bd"]
        txt_col = T["accent_green"]
        txt = f"Recommended: {win_tag}"
    else:
        bg_col = T["badge_hold_bg"]
        bd_col = T["badge_hold_bd"]
        txt_col = T["accent_amber"]
        txt = "⚠ Tie — see suggestions below"
    st.markdown(
        f"<div style='display:grid;grid-template-columns:4fr 0.5fr 2fr 2fr;gap:0.5rem;width:100%;margin-bottom:0.75rem;'>"
        # ── Recommend / Tie box ──
        f"<div style='background:{bg_col};border:1px solid {bd_col};color:{txt_col};"
        f"font-family:Space Grotesk,sans-serif;font-size:1.15rem;font-weight:700;"
        f"box-sizing:border-box;padding:1.2rem 1.2rem;border-radius:10px;"
        f"display:flex;align-items:center;justify-content:center;'>{txt}</div>"
        # ── Spacer ──
        f"<div></div>"
        # ── Score card A ──
        f"<div style='box-sizing:border-box;padding:1.2rem 1rem;border-radius:10px;"
        f"background:{T['bg_card']};border:1px solid {T['border']};"
        f"display:flex;flex-direction:column;align-items:center;justify-content:center;'"
        f" title='Combined weighted score (higher = better)'>"
        f"<div style='font-family:Inter,sans-serif;font-size:0.68rem;color:{_tsec};"
        f"text-transform:uppercase;letter-spacing:0.05em;'>{ta} Score</div>"
        f"<div style='font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;"
        f"color:{T['text_primary']};margin-top:0.25rem;'>{report['score_a']:.0f}/{report['total']}</div>"
        f"</div>"
        # ── Score card B ──
        f"<div style='box-sizing:border-box;padding:1.2rem 1rem;border-radius:10px;"
        f"background:{T['bg_card']};border:1px solid {T['border']};"
        f"display:flex;flex-direction:column;align-items:center;justify-content:center;'"
        f" title='Combined weighted score (higher = better)'>"
        f"<div style='font-family:Inter,sans-serif;font-size:0.68rem;color:{_tsec};"
        f"text-transform:uppercase;letter-spacing:0.05em;'>{tb} Score</div>"
        f"<div style='font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;"
        f"color:{T['text_primary']};margin-top:0.25rem;'>{report['score_b']:.0f}/{report['total']}</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="rec-box">{report["reason"]}</div>', unsafe_allow_html=True)

    # ── Score table + radar ───────────────────────────────────────────────────
    cl, cr = st.columns([1, 1])
    with cl:
        rail_header("Dimension breakdown", icon("layers", 13, T["text_muted"]))
        st.caption("*Total score is a weighted sum of the sub-scores below.*")
        rows = []
        wmap = {"predicted_return": 3, "volatility": 2,
                "model_confidence": 2, "sentiment": 2, "price_trend": 1}
        for dk, dd in sc.items():
            w = wmap.get(dk, 1)
            ww = dd.get("winner")
            better = ta if ww == "a" else (tb if ww == "b" else "Tie")
            pts = f"+{w}" if ww in ("a", "b") else f"+{w/2}"
            rows.append({
                "Dimension": dd["label"],
                ta: dd.get("stars_a", "—"),
                tb: dd.get("stars_b", "—"),
                "Better": better,
                "Weight": pts,
            })
        df = pd.DataFrame(rows)
        html = '<table style="width:100%; border-collapse:collapse; font-size:0.84rem; font-family:Inter,sans-serif;">'
        html += f'<thead><tr>'
        for col_name in ["Dimension", ta, tb, "Better", "Pts (Weight)"]:
            align = "left" if col_name == "Dimension" else "center"
            html += (
                f'<th style="text-align:{align}; padding:0.7rem 0.9rem; background:{T["bg_surface"]}; '
                f'color:{_tsec}; border-bottom:1px solid {T["border"]}; font-weight:600; '
                f'text-transform:uppercase; font-size:0.68rem; letter-spacing:0.06em;">{col_name}</th>'
            )
        html += f'</tr></thead><tbody>'
        for _, row in df.iterrows():
            winner = row["Better"]
            if winner == ta:
                better_color = T["accent_green"]
                row_bg = "rgba(46,204,113,0.05)"
            elif winner == tb:
                better_color = T["accent_blue"]
                row_bg = "rgba(76,155,232,0.05)"
            else:
                better_color = T["text_secondary"]
                row_bg = "transparent"
            html += f'<tr style="background:{row_bg};">'
            html += f'<td style="text-align:left; padding:0.6rem 0.9rem; border-bottom:1px solid {T["border"]}; color:{T["text_primary"]};">{row["Dimension"]}</td>'
            html += f'<td style="text-align:center; padding:0.6rem 0.9rem; border-bottom:1px solid {T["border"]}; color:{T["text_primary"]}; font-family:JetBrains Mono,monospace;">{row[ta]}</td>'
            html += f'<td style="text-align:center; padding:0.6rem 0.9rem; border-bottom:1px solid {T["border"]}; color:{T["text_primary"]}; font-family:JetBrains Mono,monospace;">{row[tb]}</td>'
            html += f'<td style="text-align:center; padding:0.6rem 0.9rem; border-bottom:1px solid {T["border"]}; color:{better_color}; font-weight:600; font-size:0.78rem;">{winner}</td>'
            html += f'<td style="text-align:center; padding:0.6rem 0.9rem; border-bottom:1px solid {T["border"]}; color:{_tsec}; font-family:JetBrains Mono,monospace; font-size:0.78rem;">{row["Weight"]}</td>'
            html += '</tr>'
        html += '</tbody></table>'
        st.markdown(html, unsafe_allow_html=True)
        st.caption(
            "Risk: std-dev of daily returns · Confidence: ensemble backtest MSE")

    with cr:
        rail_header("Radar comparison", icon("activity", 13, T["text_muted"]))
        st.plotly_chart(build_radar_chart(report), use_container_width=True)

    # ── Forecast chart ────────────────────────────────────────────────────────
    da = report["data_a"]
    db = report["data_b"]
    pa = da.get("predicted_price_7d")
    pb = db.get("predicted_price_7d")
    ha = da.get("historical_prices_30d")
    hb = db.get("historical_prices_30d")
    if pa and pb and ha and hb:
        rail_header("30-day history + 7-day forecast",
                    icon("chart-line", 13, T["text_muted"]))
        st.plotly_chart(build_compare_forecast_chart(report), use_container_width=True)



def render_compare_page():
    T = get_tokens()
    render_ticker_strip()
    render_nav(show_back=False, active_page="compare")

    rail_header("Stock comparison", icon("compare", 13, T["text_muted"]))

    st.markdown("### Select Two Stocks to Compare")
    col_a, col_b, col_btn = st.columns([4, 4, 3])
    with col_a:
        ticker_a = st.text_input(
            "Stock A", placeholder="e.g. AAPL", key="comp_a").strip().upper()
    with col_b:
        ticker_b = st.text_input(
            "Stock B", placeholder="e.g. TSLA", key="comp_b").strip().upper()
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>",
                    unsafe_allow_html=True)
        run_compare = st.button("Compare", type="primary",
                                use_container_width=True, key="compare_go")

    if run_compare:
        if ticker_a == ticker_b:
            st.warning("Please enter two different stocks to compare.")
            return

        with st.spinner("Fetching data and running predictions for both stocks (this may take a minute)..."):
            report = _cached_compare(ticker_a, ticker_b)

        if report is None:
            st.error(
                "Could not complete comparison. Check the ticker symbols and try again.")
            return

        _display_compare_results(report)
