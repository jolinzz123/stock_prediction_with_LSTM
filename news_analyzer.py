import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience only
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"
ALPHAVANTAGE_TIMEOUT_SECONDS = 20

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


def get_alphavantage_api_key() -> str | None:
    direct_value = (
        os.getenv("ALPHAVANTAGE_API_KEY")
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    )
    if direct_value:
        return direct_value

    for env_path in (Path(".env"), Path(__file__).resolve().with_name(".env")):
        if not env_path.exists():
            continue
        try:
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() in {"ALPHAVANTAGE_API_KEY", "ALPHA_VANTAGE_API_KEY"}:
                    return value.strip().strip('"').strip("'")
        except OSError:
            continue

    return None


def format_publish_time(timestamp) -> str:
    try:
        if isinstance(timestamp, str) and "T" in timestamp:
            dt = datetime.strptime(timestamp, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "Unknown"


def _empty_result() -> dict:
    return {
        "articles": [],
        "sentiment_score": 0.0,
        "aggregate_score": 0.0,
        "sentiment_label": "Neutral",
        "positive_count": 0,
        "negative_count": 0,
        "neutral_count": 0,
        "source": "none",
    }


def _alpha_vantage_query(**params) -> dict:
    api_key = get_alphavantage_api_key()
    if not api_key:
        raise RuntimeError("Missing ALPHAVANTAGE_API_KEY.")

    response = requests.get(
        ALPHAVANTAGE_BASE_URL,
        params={**params, "apikey": api_key},
        timeout=ALPHAVANTAGE_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    message = (
        data.get("Information")
        or data.get("Note")
        or data.get("Error Message")
    )
    if message:
        raise RuntimeError(str(message))

    return data


def fetch_alpha_vantage_news_feed(
    ticker: str,
    *,
    limit: int = 50,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
    sort: str = "LATEST",
) -> list[dict]:
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker.upper(),
        "limit": int(limit),
        "sort": sort,
    }
    if start is not None:
        params["time_from"] = pd.Timestamp(start).strftime("%Y%m%dT%H%M")
    if end is not None:
        params["time_to"] = pd.Timestamp(end).strftime("%Y%m%dT%H%M")

    data = _alpha_vantage_query(**params)
    return list(data.get("feed", []))


def _extract_ticker_score(article: dict, ticker: str) -> tuple[float, float]:
    normalized = ticker.upper()
    for item in article.get("ticker_sentiment", []):
        if str(item.get("ticker", "")).upper() == normalized:
            score = float(item.get("ticker_sentiment_score", 0.0))
            weight = float(item.get("relevance_score", 1.0))
            return score, max(weight, 1e-6)

    score = float(article.get("overall_sentiment_score", 0.0))
    return score, 1.0


def _parse_published_at(article: dict) -> pd.Timestamp | None:
    raw_value = article.get("time_published")
    if not raw_value:
        return None
    try:
        return pd.Timestamp(datetime.strptime(raw_value, "%Y%m%dT%H%M%S"))
    except Exception:
        return None


def _summarize_alpha_vantage_feed(
    ticker: str,
    feed: list[dict],
    max_items: int = 10,
) -> dict:
    if not feed:
        return _empty_result()

    articles = []
    scores = []
    positive = negative = neutral = 0

    for article in feed[:max_items]:
        title = str(article.get("title", "")).strip()
        if not title:
            continue

        score, _ = _extract_ticker_score(article, ticker)
        label = sentiment_label(score)

        if score >= 0.05:
            positive += 1
        elif score <= -0.05:
            negative += 1
        else:
            neutral += 1

        scores.append(score)
        articles.append(
            {
                "title": title,
                "publisher": article.get("source", "Unknown"),
                "url": article.get("url", ""),
                "published_at": format_publish_time(article.get("time_published")),
                "sentiment_score": score,
                "sentiment_label": label,
                "summary": article.get("summary", ""),
            }
        )

    avg_score = sum(scores) / len(scores) if scores else 0.0
    return {
        "articles": articles,
        "sentiment_score": avg_score,
        "aggregate_score": avg_score,
        "sentiment_label": sentiment_label(avg_score),
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "source": "alphavantage",
    }


def _build_daily_sentiment_series_from_feed(
    ticker: str,
    feed: list[dict],
    price_index,
) -> pd.Series:
    if not isinstance(price_index, pd.DatetimeIndex):
        aligned_index = pd.to_datetime(price_index)
    else:
        aligned_index = price_index

    if aligned_index.tz is not None:
        aligned_index = aligned_index.tz_localize(None)

    aligned_index = pd.DatetimeIndex(aligned_index).normalize()
    if len(aligned_index) == 0:
        return pd.Series(dtype=float)

    if not feed:
        return pd.Series(0.0, index=aligned_index, dtype=float)

    rows = []
    for article in feed:
        published_at = _parse_published_at(article)
        if published_at is None:
            continue

        score, weight = _extract_ticker_score(article, ticker)
        rows.append(
            {
                "date": published_at.normalize(),
                "weighted_score": score * weight,
                "weight": weight,
            }
        )

    if not rows:
        return pd.Series(0.0, index=aligned_index, dtype=float)

    daily = pd.DataFrame(rows).groupby("date").sum()
    series = daily["weighted_score"] / daily["weight"].replace(0, pd.NA)
    series = series.fillna(0.0).astype(float)

    series = series.reindex(aligned_index, fill_value=0.0)
    series = series.ewm(span=3, adjust=False).mean()
    return series.clip(-1.0, 1.0)


def _get_yfinance_news_sentiment(ticker: str, max_items: int = 10) -> dict:
    stock = yf.Ticker(ticker)
    news_items = stock.news or []

    if not news_items:
        return _empty_result()

    articles = []
    scores = []
    positive = negative = neutral = 0

    for item in news_items[:max_items]:
        content = item.get("content", {})

        title = (
            item.get("title", "")
            or content.get("title", "")
        ).strip()

        publisher = (
            item.get("publisher", "")
            or content.get("provider", {}).get("displayName", "")
            or "Unknown"
        )

        url = (
            item.get("link", "")
            or content.get("canonicalUrl", {}).get("url", "")
            or content.get("clickThroughUrl", {}).get("url", "")
            or ""
        )

        publish_time = item.get("providerPublishTime", 0) or 0

        if not title:
            continue

        score = analyzer.polarity_scores(title)["compound"]
        label = sentiment_label(score)

        if score >= 0.05:
            positive += 1
        elif score <= -0.05:
            negative += 1
        else:
            neutral += 1

        scores.append(score)
        articles.append(
            {
                "title": title,
                "publisher": publisher,
                "url": url,
                "published_at": format_publish_time(publish_time),
                "sentiment_score": score,
                "sentiment_label": label,
            }
        )

    avg_score = sum(scores) / len(scores) if scores else 0.0

    return {
        "articles": articles,
        "sentiment_score": avg_score,
        "aggregate_score": avg_score,
        "sentiment_label": sentiment_label(avg_score),
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "source": "yfinance",
    }


def get_news_sentiment(ticker: str, max_items: int = 10) -> dict:
    """
    Return recent article-level sentiment for the UI.

    Preferred source: Alpha Vantage NEWS_SENTIMENT.
    Fallback source: yfinance headlines scored with VADER.
    """
    try:
        if get_alphavantage_api_key():
            feed = fetch_alpha_vantage_news_feed(
                ticker,
                limit=max(max_items, 20),
                sort="LATEST",
            )
            return _summarize_alpha_vantage_feed(ticker, feed, max_items=max_items)
        return _get_yfinance_news_sentiment(ticker, max_items=max_items)
    except Exception as exc:
        try:
            result = _get_yfinance_news_sentiment(ticker, max_items=max_items)
            result["fallback_error"] = str(exc)
            return result
        except Exception as fallback_exc:
            return {**_empty_result(), "error": str(fallback_exc), "fallback_error": str(exc)}


def get_historical_sentiment_series(
    ticker: str,
    price_index,
    article_limit: int = 1000,
) -> pd.Series:
    """
    Build a daily sentiment series aligned to trading dates for model features.

    The free Alpha Vantage tier can be sparse, so missing days are filled with 0 and
    a short EMA is applied to let important news decay across the next few sessions.
    """
    if not isinstance(price_index, pd.DatetimeIndex):
        aligned_index = pd.to_datetime(price_index)
    else:
        aligned_index = price_index

    if aligned_index.tz is not None:
        aligned_index = aligned_index.tz_localize(None)

    aligned_index = pd.DatetimeIndex(aligned_index)
    if len(aligned_index) == 0:
        return pd.Series(dtype=float)

    if not get_alphavantage_api_key():
        return pd.Series(0.0, index=aligned_index.normalize(), dtype=float)

    start = aligned_index.min().normalize()
    end = (aligned_index.max().normalize() + timedelta(days=1)).replace(hour=23, minute=59)

    try:
        feed = fetch_alpha_vantage_news_feed(
            ticker,
            limit=article_limit,
            start=start,
            end=end,
            sort="LATEST",
        )
        return _build_daily_sentiment_series_from_feed(ticker, feed, aligned_index)
    except Exception:
        return pd.Series(0.0, index=aligned_index.normalize(), dtype=float)


def get_ticker_sentiment_context(
    ticker: str,
    price_index,
    max_items: int = 10,
    article_limit: int = 1000,
) -> dict:
    """
    Fetch both:
    - recent article sentiment for display
    - historical daily sentiment series for model features

    Uses a single Alpha Vantage feed when the API key is available.
    """
    if not isinstance(price_index, pd.DatetimeIndex):
        aligned_index = pd.to_datetime(price_index)
    else:
        aligned_index = price_index

    if aligned_index.tz is not None:
        aligned_index = aligned_index.tz_localize(None)

    if len(aligned_index) == 0:
        return {
            "news_result": get_news_sentiment(ticker, max_items=max_items),
            "sentiment_series": pd.Series(dtype=float),
        }

    if not get_alphavantage_api_key():
        return {
            "news_result": get_news_sentiment(ticker, max_items=max_items),
            "sentiment_series": pd.Series(0.0, index=aligned_index.normalize(), dtype=float),
        }

    start = aligned_index.min().normalize()
    end = (aligned_index.max().normalize() + timedelta(days=1)).replace(hour=23, minute=59)

    try:
        feed = fetch_alpha_vantage_news_feed(
            ticker,
            limit=article_limit,
            start=start,
            end=end,
            sort="LATEST",
        )
        return {
            "news_result": _summarize_alpha_vantage_feed(ticker, feed, max_items=max_items),
            "sentiment_series": _build_daily_sentiment_series_from_feed(ticker, feed, aligned_index),
        }
    except Exception:
        return {
            "news_result": get_news_sentiment(ticker, max_items=max_items),
            "sentiment_series": pd.Series(0.0, index=aligned_index.normalize(), dtype=float),
        }


def extract_market_drivers(news_result: dict, top_n: int = 5) -> list[dict]:
    """
    Return the headlines with the strongest absolute sentiment values.
    """
    return sorted(
        news_result.get("articles", []),
        key=lambda article: abs(article["sentiment_score"]),
        reverse=True,
    )[:top_n]


def generate_recommendation(
    current_price: float,
    future_predictions: list[float],
    news_result: dict,
) -> dict:
    """
    Combine the quantitative forecast (70%) and recent news sentiment (30%).
    """
    predicted_price = future_predictions[-1]
    price_change_pct = (predicted_price - current_price) / current_price * 100

    prediction_score = price_change_pct / 10
    sentiment_score = news_result.get("sentiment_score", 0.0)
    combined_score = prediction_score * 0.7 + sentiment_score * 0.3

    if combined_score >= 0.60:
        signal, color = "STRONG BUY", "#2ECC71"
    elif combined_score >= 0.20:
        signal, color = "BUY", "#58D68D"
    elif combined_score > -0.20:
        signal, color = "HOLD", "#F4D03F"
    elif combined_score > -0.60:
        signal, color = "REDUCE", "#F39C12"
    else:
        signal, color = "AVOID", "#E74C3C"

    return {
        "signal": signal,
        "color": color,
        "combined_score": combined_score,
        "price_change_pct": price_change_pct,
        "predicted_price": predicted_price,
        "rationale": "",
    }
