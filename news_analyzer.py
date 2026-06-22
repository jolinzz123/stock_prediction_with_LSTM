from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
from datetime import datetime, timezone

analyzer = SentimentIntensityAnalyzer()


def sentiment_label(score: float) -> str:
    if score >= 0.15:
        return "Very Positive"
    if score >= 0.05:
        return "Positive"
    if score <= -0.15:
        return "Very Negative"
    if score <= -0.05:
        return "Negative"
    return "Neutral"


<<<<<<< Updated upstream
def format_publish_time(timestamp) -> str:
=======
def format_publish_time(timestamp):
>>>>>>> Stashed changes
    try:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "Unknown"
<<<<<<< Updated upstream


def get_time_weight(timestamp: int) -> float:
    try:
        published = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)

        hours_old = (now - published).total_seconds() / 3600

        if hours_old <= 24:
            return 1.0
        elif hours_old <= 72:
            return 0.8
        elif hours_old <= 168:  # 7 days
            return 0.5
        else:
            return 0.2

    except Exception:
        return 0.2


def get_news_sentiment(ticker: str, max_items: int = 10) -> dict:
    """
    Fetch news and calculate weighted sentiment score for a given stock ticker.

    Returns
    -------
    {
        articles       : list[dict]   – per-article data + sentiment
        sentiment_score: float        – average compound score
        sentiment_label: str          – human-readable label
        positive_count : int
        negative_count : int
        neutral_count  : int
        aggregate_score: float        – alias for sentiment_score (legacy compat)
=======


def get_news_sentiment(ticker: str, max_items: int = 10):
    """
    Returns:
    {
        articles,
        sentiment_score,
        sentiment_label,
        positive_count,
        negative_count,
        neutral_count
>>>>>>> Stashed changes
    }
    """
    try:
        stock = yf.Ticker(ticker)
<<<<<<< Updated upstream
        news_items = stock.news or []

        if not news_items:
            return _empty_result()

        articles = []
        weighted_sum = 0.0
        total_weight = 0.0
        raw_scores = []
        positive = negative = neutral = 0

        for item in news_items[:max_items]:
            # yfinance ≥0.2.x may nest everything under "content"
            content = item.get("content", {})

            title = (
                item.get("title", "")
                or content.get("title", "")
            ).strip()

            if not title:
                continue
=======
        news_items = stock.news

        if not news_items:
            return {
                "articles": [],
                "sentiment_score": 0,
                "sentiment_label": "Neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        articles = []
        scores = []
        positive = 0
        negative = 0
        neutral = 0

        for item in news_items[:max_items]:

            # ✅ FIX: yfinance newer versions nest data under "content"
            content = item.get("content", {})

            title = item.get("title", "") or content.get("title", "")
>>>>>>> Stashed changes

            publisher = (
                item.get("publisher", "")
                or content.get("provider", {}).get("displayName", "")
                or "Unknown"
            )

<<<<<<< Updated upstream
=======
            # Resolve URL from multiple possible locations
>>>>>>> Stashed changes
            url = (
                item.get("link", "")
                or content.get("canonicalUrl", {}).get("url", "")
                or content.get("clickThroughUrl", {}).get("url", "")
                or ""
            )

<<<<<<< Updated upstream
            publish_time = item.get("providerPublishTime", 0) or 0
=======
            # Resolve publish time from multiple possible locations
            publish_time = item.get("providerPublishTime", 0) or (
                # Some versions store as ISO string under content
                0
            )
>>>>>>> Stashed changes

            score = analyzer.polarity_scores(title)["compound"]
            label = sentiment_label(score)

            if score >= 0.05:
                positive += 1
            elif score <= -0.05:
                negative += 1
            else:
                neutral += 1

<<<<<<< Updated upstream
            weight = get_time_weight(publish_time)
            weighted_sum += score * weight
            total_weight += weight

            raw_scores.append(score)

            articles.append({
                "title":           title,
                "publisher":       publisher,
                "url":             url,
                "published_at":    format_publish_time(publish_time),
=======
            scores.append(score)
            articles.append({
                "title": title,
                "publisher": publisher,
                "url": url,
                "published_at": format_publish_time(publish_time),
>>>>>>> Stashed changes
                "sentiment_score": score,
                "sentiment_label": label,
            })

<<<<<<< Updated upstream
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        sentiment_confidence = (
            abs(avg_score) * min(len(raw_scores) / 10, 1.0))

        return {
            "articles":        articles,
            "sentiment_score": avg_score,
            "aggregate_score": avg_score,   # legacy alias used by some callers
            "sentiment_label": sentiment_label(avg_score),
            "positive_count":  positive,
            "negative_count":  negative,
            "neutral_count":   neutral,
            "article_count": len(raw_scores),
            "sentiment_confidence": sentiment_confidence,
        }

    except Exception as e:
        return {**_empty_result(), "error": str(e)}


def _empty_result() -> dict:
    return {
        "articles":        [],
        "sentiment_score": 0.0,
        "aggregate_score": 0.0,
        "sentiment_label": "Neutral",
        "positive_count":  0,
        "negative_count":  0,
        "neutral_count":   0,
        "article_count": 0,
        "sentiment_confidence": 0.0,
    }


def extract_market_drivers(news_result: dict, top_n: int = 5) -> list[dict]:
    """
    Return the `top_n` articles with the highest absolute sentiment score —
    these are the headlines that moved the needle most, in either direction.
    """
    return sorted(
        news_result.get("articles", []),
        key=lambda a: abs(a["sentiment_score"]),
        reverse=True,
    )[:top_n]


def generate_recommendation(
    current_price: float,
    future_predictions: list[float],
    news_result: dict,
) -> dict:
    """
    Combine xgboost forecast (70%) and news sentiment (30%) into a single signal.

    The `rationale` field is intentionally left empty — main.py builds a
    richer narrative via `_build_recommendation_text()` using the returned
    numeric fields, so we avoid duplicating that logic here.

    Returns
    -------
    {
        signal          : str    – STRONG BUY / BUY / HOLD / REDUCE / AVOID
        color           : str    – hex colour for the badge
        combined_score  : float
        price_change_pct: float  – XGBoost-predicted 7-day return (%)
        predicted_price : float  – day-7 price
        rationale       : str    – empty; narrative built in main.py
    }
    """
    if not future_predictions:
        return {
            "signal": "HOLD",
            "color": "#F4D03F",
            "combined_score": 0,
            "price_change_pct": 0,
            "predicted_price": current_price,
            "rationale": "",
        }

    predicted_price = future_predictions[-1]
    price_change_pct = (predicted_price - current_price) / current_price * 100

    # Normalise prediction score: 10 % move → score of 1.0
    prediction_score = price_change_pct / 10
    sentiment_score = news_result.get("sentiment_score", 0.0)
    combined_score = prediction_score * 0.7 + sentiment_score * 0.3

    if combined_score >= 0.60:
        signal, color = "STRONG BUY", "#2ECC71"
    elif combined_score >= 0.20:
        signal, color = "BUY",        "#58D68D"
    elif combined_score > -0.20:
        signal, color = "HOLD",       "#F4D03F"
    elif combined_score > -0.60:
        signal, color = "REDUCE",     "#F39C12"
    else:
        signal, color = "AVOID",      "#E74C3C"

    return {
        "signal":           signal,
        "color":            color,
        "combined_score": round(combined_score, 4),
        "prediction_score": round(prediction_score, 4),
        "sentiment_score": round(sentiment_score, 4),
        "price_change_pct": round(price_change_pct, 2),
        "predicted_price":  predicted_price,
        "rationale":        "",   # narrative rendered by main.py
=======
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "articles": articles,
            "sentiment_score": avg_score,
            "sentiment_label": sentiment_label(avg_score),
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
        }

    except Exception as e:
        return {
            "articles": [],
            "sentiment_score": 0,
            "sentiment_label": "Neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "error": str(e),
        }


def extract_market_drivers(news_result):
    """Return top 5 articles sorted by absolute sentiment score."""
    articles = news_result["articles"]
    sorted_articles = sorted(
        articles,
        key=lambda x: abs(x["sentiment_score"]),
        reverse=True,
    )
    return sorted_articles[:5]


def generate_recommendation(current_price, future_predictions, news_result):
    """
    Combines:
    - LSTM prediction (70%)
    - News sentiment (30%)
    """
    predicted_price = future_predictions[-1]
    price_change_pct = (predicted_price - current_price) / current_price * 100
    prediction_score = price_change_pct / 10
    sentiment_score = news_result["sentiment_score"]
    combined_score = prediction_score * 0.7 + sentiment_score * 0.3

    if combined_score >= 0.60:
        signal = "STRONG BUY"
        color = "#2ECC71"
    elif combined_score >= 0.20:
        signal = "BUY"
        color = "#58D68D"
    elif combined_score > -0.20:
        signal = "HOLD"
        color = "#F4D03F"
    elif combined_score > -0.60:
        signal = "REDUCE"
        color = "#F39C12"
    else:
        signal = "AVOID"
        color = "#E74C3C"

    rationale = f"""
### AI Recommendation

**Forecast Return:** {price_change_pct:+.2f}%

**News Sentiment:** {news_result['sentiment_label']}

**Combined Score:** {combined_score:+.2f}

The recommendation combines:
- 70% LSTM price prediction
- 30% recent news sentiment
"""

    return {
        "signal": signal,
        "color": color,
        "combined_score": combined_score,
        "price_change_pct": price_change_pct,
        "predicted_price": predicted_price,
        "rationale": rationale,
>>>>>>> Stashed changes
    }
