# app_web.py
# Flask web interface for the Stock Price Prediction System.
# Flask docs: https://flask.palletsprojects.com/
# News fetching via Google News RSS feed (no API key required):
# https://news.google.com/rss

import os
import io
import base64
import threading
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd

from data_fetcher import fetch_stock_data, preprocess_data, train_test_split_timeseries
from model import build_model, train_model, load_saved_model, MODEL_SAVE_PATH
from predictor import predict_on_test_set, predict_future, calculate_metrics, get_trend_signal
from visualizer import plot_prediction_results, plot_training_loss, plot_future_only

app = Flask(__name__)
_lock = threading.Lock()

LOOK_BACK   = 60
SPLIT_RATIO = 0.8


def chart_to_base64(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def fetch_stock_news(ticker: str, max_articles: int = 6) -> list:
    """
    Fetch recent news articles for a stock ticker via Google News RSS.
    Source: https://news.google.com/rss

    Parameters:
        ticker (str): Stock ticker symbol.
        max_articles (int): Maximum number of articles to return.

    Returns:
        list: List of dicts with keys: title, link, source, published.
    """
    url = (
        f"https://news.google.com/rss/search"
        f"?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    )
    articles = []
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=6)
        root = ET.fromstring(response.read())

        for item in root.findall(".//item")[:max_articles]:
            title   = item.findtext("title", "").strip()
            link    = item.findtext("link",  "").strip()
            pub_raw = item.findtext("pubDate", "")
            source  = item.findtext("source", "Google News")

            # Parse and reformat the date
            try:
                dt = datetime.strptime(pub_raw, "%a, %d %b %Y %H:%M:%S %Z")
                published = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                published = pub_raw[:16] if pub_raw else "—"

            if title and link:
                articles.append({
                    "title":     title,
                    "link":      link,
                    "source":    source,
                    "published": published,
                })
    except Exception:
        # Return empty list silently; UI handles the empty state
        pass

    return articles


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/news/<ticker>")
def news(ticker: str):
    """Return latest news articles for a given ticker as JSON."""
    ticker = ticker.strip().upper()
    if not ticker.isalpha() or len(ticker) > 5:
        return jsonify({"error": "Invalid ticker"}), 400
    articles = fetch_stock_news(ticker)
    return jsonify({"ticker": ticker, "articles": articles})


@app.route("/predict", methods=["POST"])
def predict():
    data    = request.get_json()
    ticker  = str(data.get("ticker", "")).strip().upper()
    days    = int(data.get("days", 10))
    retrain = bool(data.get("retrain", True))

    if not ticker or not ticker.isalpha() or len(ticker) > 5:
        return jsonify({"error": "Invalid ticker symbol."}), 400
    if not (1 <= days <= 30):
        return jsonify({"error": "Forecast days must be 1–30."}), 400

    with _lock:
        try:
            df = fetch_stock_data(ticker)
            last_price = float(df['Close'].iloc[-1])

            X, y, scaler = preprocess_data(df, look_back=LOOK_BACK)
            X_train, X_test, y_train, y_test = train_test_split_timeseries(X, y, SPLIT_RATIO)

            if retrain or not os.path.exists(MODEL_SAVE_PATH):
                model = build_model(look_back=LOOK_BACK)
                model, history = train_model(model, X_train, y_train, epochs=30)
                plot_training_loss(history, ticker)
            else:
                model = load_saved_model()

            test_predicted = predict_on_test_set(model, X_test, scaler)
            test_actual    = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
            metrics        = calculate_metrics(test_actual, test_predicted)

            future_prices = predict_future(model, df, scaler, days, LOOK_BACK)
            trend         = get_trend_signal(future_prices)

            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            plot_prediction_results(df, test_actual, test_predicted,
                                    future_prices, ticker, LOOK_BACK, SPLIT_RATIO)
            plot_future_only(df, future_prices, ticker)

            last_date    = pd.to_datetime(df.index[-1])
            future_dates = pd.bdate_range(
                start=last_date + pd.Timedelta(days=1), periods=days)

            forecast_table = []
            prev = last_price
            for i, (price, date) in enumerate(zip(future_prices.tolist(), future_dates), 1):
                change = price - prev
                forecast_table.append({
                    "day":    i,
                    "date":   date.strftime("%d %b %Y"),
                    "price":  f"${price:.2f}",
                    "change": f"+${change:.2f}" if change >= 0 else f"-${abs(change):.2f}",
                    "up":     change >= 0,
                })
                prev = price

            return jsonify({
                "ticker":         ticker,
                "current_price":  f"${last_price:.2f}",
                "target_price":   f"${future_prices[-1]:.2f}",
                "trend":          trend,
                "rmse":           metrics["RMSE"],
                "mae":            metrics["MAE"],
                "mape":           f"{metrics['MAPE']:.2f}%",
                "forecast":       forecast_table,
                "chart_pred":     chart_to_base64(os.path.join(assets_dir, f"{ticker}_prediction.png")),
                "chart_forecast": chart_to_base64(os.path.join(assets_dir, f"{ticker}_forecast.png")),
                "chart_loss":     chart_to_base64(os.path.join(assets_dir, f"{ticker}_loss.png")),
            })

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


def run_web(host="127.0.0.1", port=5000, debug=False):
    print(f"\n  🌐  Web app running at: http://{host}:{port}")
    print("  Open the URL above in your browser.")
    print("  Press Ctrl+C to stop.\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_web()
