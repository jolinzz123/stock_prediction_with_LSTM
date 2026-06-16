"""
Run this script to pre-train models for a list of tickers.
Usage:  python pretrain.py
Results are saved to cache/ and loaded instantly in the app.
"""

from data_fetcher import fetch_stock_data, get_stock_info
from predictor import run_prediction
import cache_manager
from main import WATCHLIST

TICKERS = WATCHLIST


def pretrain(ticker: str) -> None:
    print(f"[{ticker}] Fetching data...", flush=True)
    df = fetch_stock_data(ticker)
    info = get_stock_info(ticker)

    print(f"[{ticker}] Training model...", flush=True)
    result = run_prediction(df, future_days=7)

    cache_manager.save(ticker, {"df": df, "info": info, "result": result})
    print(f"[{ticker}] Done — cached.", flush=True)


if __name__ == "__main__":
    for ticker in TICKERS:
        try:
            pretrain(ticker)
        except Exception as e:
            print(f"[{ticker}] FAILED: {e}", flush=True)
