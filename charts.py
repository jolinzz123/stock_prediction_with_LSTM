import pandas as pd
import plotly.graph_objects as go

from theme import get_tokens, chart_layout


# Candlestick chart adapted from https://plotly.com/python/candlestick-charts/
def build_candlestick(df: pd.DataFrame) -> go.Figure:
    """Build an interactive OHLC candlestick chart with SMA-20 and SMA-50 overlays.

    Includes a range slider and time-period selector (1M / 3M / 6M / YTD / 1Y / All).
    """
    T = get_tokens()
    fig = go.Figure()

    # Main candlestick trace: green = up day, red = down day
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name="OHLC",
        increasing=dict(
            line=dict(color=T["accent_green"], width=1), fillcolor=T["accent_green"]),
        decreasing=dict(
            line=dict(color=T["accent_red"],   width=1), fillcolor=T["accent_red"]),
    ))

    # Simple Moving Average overlays for trend identification
    sma20 = df["Close"].rolling(20).mean()
    sma50 = df["Close"].rolling(50).mean()
    fig.add_trace(go.Scatter(x=df.index, y=sma20, mode="lines",
                             name="SMA 20", line=dict(color=T["accent_amber"], width=1.2)))
    fig.add_trace(go.Scatter(x=df.index, y=sma50, mode="lines",
                             name="SMA 50", line=dict(color="#A78BFA", width=1.2)))

    # Layout: range slider + time-period selector buttons
    layout = chart_layout(height=480)
    layout.update(
        margin=dict(l=0, r=0, t=40, b=0),
        modebar=dict(orientation="v", bgcolor="rgba(0,0,0,0)"),
        xaxis_rangeslider_visible=True,
        xaxis_rangeselector=dict(
            buttons=[
                dict(count=1,  label="1M", step="month", stepmode="backward"),
                dict(count=3,  label="3M", step="month", stepmode="backward"),
                dict(count=6,  label="6M", step="month", stepmode="backward"),
                dict(count=1,  label="YTD", step="year", stepmode="todate"),
                dict(count=1,  label="1Y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ],
            bgcolor=T["bg_surface"],
            activecolor=T["accent_blue"],
            font=dict(color=T["text_secondary"], family="Space Grotesk", size=11),
            y=1.06,
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        hovermode="x unified",
        dragmode="zoom",
    )
    fig.update_layout(**layout)
    return fig


# Line chart with forecast overlay adapted from https://plotly.com/python/line-charts/
def build_forecast_chart(dates, prices, future_dates, future_preds) -> go.Figure:
    """Build a chart showing the last 60 days of prices plus a 7-day forecast line.

    The forecast region is highlighted with a translucent green background.
    """
    T = get_tokens()
    fig = go.Figure()

    # Historical prices: last 60 trading days
    fig.add_trace(go.Scatter(
        x=dates[-60:], y=prices[-60:],
        mode="lines", name="Last 60 days",
        line=dict(color=T["accent_blue"], width=1.6),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f}<extra></extra>",
    ))

    # Bridge segment connecting the last actual price to the first forecast point
    fig.add_trace(go.Scatter(
        x=[dates[-1], future_dates[0]],
        y=[prices[-1], future_preds[0]],
        mode="lines", name="7-day forecast",
        line=dict(color=T["accent_blue"], width=1.6),
        showlegend=False, hoverinfo="skip",
    ))

    # Forecast line with circle markers
    fig.add_trace(go.Scatter(
        x=list(future_dates),
        y=list(future_preds),
        mode="lines+markers", name="7-day forecast",
        line=dict(color=T["accent_green"], width=2.2),
        marker=dict(size=8, symbol="circle", color=T["accent_green"],
                    line=dict(color=T["bg_base"], width=2)),
        showlegend=True,
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Forecast: %{y:.2f}<extra></extra>",
    ))

    # Translucent green rectangle behind the forecast region
    fig.add_shape(
        type="rect",
        x0=future_dates[0], x1=future_dates[-1],
        y0=0, y1=1, yref="paper",
        fillcolor=T["accent_green"], opacity=0.08,
        layer="below", line_width=0,
    )
    fig.update_layout(**chart_layout(380))
    return fig


def build_backtest_chart(dates, prices, bt_anchor_date, bt_anchor_price,
                         bt_dates_7d, bt_actual_7d, bt_pred_7d) -> go.Figure:
    """Build a chart comparing actual vs predicted prices for the most recent 7-day window.

    Shows 60 days of context, then overlays actual and predicted paths
    starting from the anchor point.
    """
    T = get_tokens()
    fig = go.Figure()

    # 60-day historical context
    fig.add_trace(go.Scatter(
        x=dates[-60:], y=prices[-60:],
        mode="lines", name="Last 60 days",
        line=dict(color=T["accent_blue"], width=1.6),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f}<extra></extra>",
    ))

    # Actual prices over the 7-day backtest window
    fig.add_trace(go.Scatter(
        x=[bt_anchor_date] + list(bt_dates_7d),
        y=[bt_anchor_price] + list(bt_actual_7d),
        mode="lines+markers", name="Actual (7d)",
        line=dict(color=T["accent_blue"], width=1.6),
        marker=dict(size=6, color=T["accent_blue"]),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Actual: %{y:.2f}<extra></extra>",
    ))

    # Model's predicted prices over the same window (dotted line)
    fig.add_trace(go.Scatter(
        x=[bt_anchor_date] + list(bt_dates_7d),
        y=[bt_anchor_price] + list(bt_pred_7d),
        mode="lines+markers", name="Predicted (7d)",
        line=dict(color=T["accent_green"], width=2.2, dash="dot"),
        marker=dict(size=8, symbol="circle", color=T["accent_green"],
                    line=dict(color=T["bg_base"], width=2)),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Predicted: %{y:.2f}<extra></extra>",
    ))

    # Highlight the backtest region
    fig.add_shape(
        type="rect",
        x0=bt_anchor_date, x1=bt_dates_7d[-1],
        y0=0, y1=1, yref="paper",
        fillcolor=T["accent_green"], opacity=0.08,
        layer="below", line_width=0,
    )
    fig.update_layout(**chart_layout(400))
    return fig


# Area chart adapted from https://plotly.com/python/filled-area-plots/
def build_history_chart(dates, prices, currency: str) -> go.Figure:
    """Build a 2-year historical closing price chart with a filled area beneath the line."""
    T = get_tokens()
    fig = go.Figure()

    # Close price line with translucent fill to zero
    fig.add_trace(go.Scatter(
        x=dates, y=prices, mode="lines", name="Close",
        line=dict(color=T["accent_blue"], width=1.6),
        fill="tozeroy",
        fillcolor=f"rgba({int(T['accent_blue'][1:3],16)},{int(T['accent_blue'][3:5],16)},{int(T['accent_blue'][5:7],16)},0.07)",
        hovertemplate="<b>%{x|%b %d %Y}</b><br>%{y:.2f} " + currency + "<extra></extra>",
    ))
    fig.update_layout(**chart_layout(340))
    return fig


# Radar chart adapted from https://plotly.com/python/radar-chart/
def build_radar_chart(report: dict) -> go.Figure:
    """Build a radar (spider) chart comparing two stocks across four dimensions:
    Predicted Return, Risk, Confidence, and Sentiment.

    Each axis is normalized to 0–100 for visual comparison.
    """
    T = get_tokens()
    fig = go.Figure()
    ta = report["ticker_a"]
    tb = report["ticker_b"]
    sc = report["scores"]

    # Map score dimensions to radar axes
    axes = ["Predicted Return", "Risk", "Confidence", "Sentiment"]
    kv = {"predicted_return": 0, "volatility": 1,
          "model_confidence": 2, "sentiment": 3}

    # Collect normalized scores for each stock
    ra, rb = [], []
    for dk, idx in kv.items():
        dd = sc.get(dk, {})
        ra.append(dd.get("norm_a", 50) or 50)
        rb.append(dd.get("norm_b", 50) or 50)

    # Close the polygon by repeating the first point
    ra.append(ra[0])
    rb.append(rb[0])
    axes.append(axes[0])

    # Ticker A polygon (blue)
    fig.add_trace(go.Scatterpolar(
        r=ra, theta=axes, fill="toself",
        name=ta, line=dict(color=T["accent_blue"], width=2),
        fillcolor=f"rgba({int(T['accent_blue'][1:3],16)},{int(T['accent_blue'][3:5],16)},{int(T['accent_blue'][5:7],16)},0.22)",
    ))

    # Ticker B polygon (amber)
    fig.add_trace(go.Scatterpolar(
        r=rb, theta=axes, fill="toself",
        name=tb, line=dict(color=T["accent_amber"], width=2),
        fillcolor=f"rgba({int(T['accent_amber'][1:3],16)},{int(T['accent_amber'][3:5],16)},{int(T['accent_amber'][5:7],16)},0.15)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(family="JetBrains Mono", size=9, color=T["text_muted"]),
                            gridcolor=T["border"]),
            angularaxis=dict(tickfont=dict(family="Space Grotesk", size=11, color=T["text_secondary"])),
            bgcolor=T["bg_card"],
        ),
        template=T["plotly_theme"], height=340,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=50, t=50, b=80),
        font=dict(color=T["text_secondary"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=T["text_primary"])),
    )
    return fig


def build_compare_forecast_chart(report: dict) -> go.Figure:
    """Build a dual-line chart comparing two stocks' 30-day history + 7-day forecast.

    Prices are normalized to cumulative return (%) so stocks at different price
    levels can be compared on the same y-axis. Dashed lines indicate forecasts.
    """
    T = get_tokens()
    ta = report["ticker_a"]
    tb = report["ticker_b"]
    da = report["data_a"]
    db = report["data_b"]
    pa = da.get("predicted_price_7d")
    pb = db.get("predicted_price_7d")
    ha = da.get("historical_prices_30d")
    hb = db.get("historical_prices_30d")

    # Normalize prices to cumulative return % relative to day 1
    base_a = ha[0]
    base_b = hb[0]
    ha_pct = [(p / base_a - 1) * 100 for p in ha]
    pa_pct = [(p / base_a - 1) * 100 for p in pa]
    hb_pct = [(p / base_b - 1) * 100 for p in hb]
    pb_pct = [(p / base_b - 1) * 100 for p in pb]
    hist_days = list(range(1, len(ha) + 1))
    pred_days = list(range(len(ha) + 1, len(ha) + len(pa) + 1))

    fig = go.Figure()

    # Stock A: solid = history, dashed = forecast
    fig.add_trace(go.Scatter(x=hist_days, y=ha_pct,
                             mode="lines", name=ta,
                             line=dict(color=T["accent_blue"], width=2)))
    fig.add_trace(go.Scatter(x=[len(ha)] + pred_days, y=[ha_pct[-1]] + pa_pct,
                             mode="lines", showlegend=False,
                             line=dict(color=T["accent_blue"], width=2, dash="dash")))

    # Stock B: solid = history, dashed = forecast
    fig.add_trace(go.Scatter(x=hist_days, y=hb_pct,
                             mode="lines", name=tb,
                             line=dict(color=T["accent_amber"], width=2)))
    fig.add_trace(go.Scatter(x=[len(hb)] + pred_days, y=[hb_pct[-1]] + pb_pct,
                             mode="lines", showlegend=False,
                             line=dict(color=T["accent_amber"], width=2, dash="dash")))

    # Vertical line marking the boundary between history and forecast
    fig.add_vline(x=len(ha), line_dash="dot", line_color=T["text_muted"],
                  annotation_text="Today", annotation_position="top left",
                  annotation_font=dict(color=T["text_muted"], size=11, family="Space Grotesk"))

    # Horizontal baseline at 0% return
    fig.add_hline(y=0, line_dash="dot", line_color=T["text_muted"], line_width=1)

    fig.update_layout(
        title=dict(text="30-Day History + 7-Day Forecast",
                   font=dict(color=T["text_primary"])),
        xaxis_title="Day", yaxis_title="Cumulative Return (%)",
        template=T["plotly_theme"], height=340,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=T["text_secondary"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=T["text_primary"])),
    )
    return fig
