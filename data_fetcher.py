import time

import pandas as pd
import yfinance as yf

# Maximum number of retry attempts when a download fails
_MAX_RETRIES = 3
# Base delay (seconds) between retries; actual delay = _RETRY_DELAY * attempt
_RETRY_DELAY = 2


class TickerNotFoundError(ValueError):
    pass


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"].astype(float)

    # Ensure all price columns exist; fill gaps with the close price
    for col in ["Open", "High", "Low", "Adj Close"]:
        if col in df:
            df[col] = df[col].astype(float).fillna(close)
        else:
            df[col] = close

    # Ensure Volume column exists and has no NaN
    if "Volume" not in df:
        df["Volume"] = 0.0
    df["Volume"] = df["Volume"].astype(float).fillna(0.0)

    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].dropna(subset=["Close"])


# yfinance download API adapted from https://ranaroussi.github.io/yfinance/reference/functions.html
def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    
    ticker = ticker.strip().upper()
    last_err = None

    for attempt in range(_MAX_RETRIES):
        try:
            # Download historical market data from Yahoo Finance
            df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=False)

            if df.empty:
                raise TickerNotFoundError(
                    f"No data found for ticker '{ticker}'. "
                    f"Please check the symbol.")

            # yfinance may return MultiIndex columns when downloading a single ticker
            if isinstance(df.columns, pd.MultiIndex):
                df = df.droplevel("Ticker", axis=1)

            return clean_ohlcv(df)

        except TickerNotFoundError:
            raise  # No point retrying an invalid ticker
        except Exception as e:
            last_err = e
            # Linear backoff: wait longer on each successive failure
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_DELAY * (attempt + 1))

    raise ValueError(
        f"Failed to fetch data for '{ticker}' after "
        f"{_MAX_RETRIES} attempts."
    ) from last_err


def get_stock_info(ticker: str) -> dict:
    
    ticker = ticker.strip().upper()
    result = {"name": ticker, "currency": "USD", "current_price": None}

    t = yf.Ticker(ticker)

    # fast_info is a lightweight call that avoids the full info scrape
    try:
        fi = t.fast_info
        result["currency"] = fi.get("currency", "USD")
        result["current_price"] = fi.get("lastPrice") or fi.get("regularMarketPrice")
    except Exception:
        pass

    # Full info scrape for the human-readable company name
    try:
        info = t.info or {}
        name = info.get("longName") or info.get("shortName")
        if name:
            result["name"] = name
    except Exception:
        pass

    return result
