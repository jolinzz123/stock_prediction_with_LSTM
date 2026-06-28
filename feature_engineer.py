import numpy as np
import pandas as pd

from data_fetcher import clean_ohlcv

LOOKBACK = 45
FUTURE_DAYS = 7

FEATURE_COLUMNS = [
    "Open", "High", "Low", "Close", "Adj Close", "Volume",
    "Return_1", "Return_2", "Return_3", "Return_5",
    "Delta_1", "Delta_2", "Delta_3", "Delta_5",
    "Momentum_3", "Momentum_5", "Momentum_10",
    "CloseToSMA_5", "CloseToSMA_10", "CloseToSMA_20",
    "Volatility_5", "Volatility_10", "Volatility_20",
    "Position_10", "Position_20",
    "RangePct", "BodyPct", "GapPct",
    "RSI_14", "MACD", "MACDSignal", "MACDHist", "ATR_14",
    "VolumeChange_1", "VolumeToSMA_5", "VolumeToSMA_20",
    "Sentiment",
]


def _safe_div(numerator, denominator):
    return numerator / denominator.replace(0, np.nan)


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def build_feature_frame(data, sentiment=None) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        df = clean_ohlcv(data.copy())
    else:
        close = np.asarray(data, dtype=float).reshape(-1)
        df = clean_ohlcv(pd.DataFrame({
            "Open": close, "High": close, "Low": close,
            "Close": close, "Adj Close": close, "Volume": 0.0,
        }))

    df = df.sort_index()
    close = df["Close"].astype(float)
    high = df["High"]
    low = df["Low"]
    open_ = df["Open"]
    volume = df["Volume"]

    features = df[["Open", "High", "Low",
                   "Close", "Adj Close", "Volume"]].copy()
    for period in [1, 2, 3, 5]:
        features[f"Return_{period}"] = close.pct_change(period)
        features[f"Delta_{period}"] = close.diff(period)

    for period in [3, 5, 10]:
        features[f"Momentum_{period}"] = _safe_div(
            close - close.shift(period), close.shift(period))

    for period in [5, 10, 20]:
        sma = close.rolling(period).mean()
        features[f"CloseToSMA_{period}"] = _safe_div(close - sma, sma)
        features[f"Volatility_{period}"] = close.pct_change().rolling(
            period).std()

    for period in [10, 20]:
        rolling_high = high.rolling(period).max()
        rolling_low = low.rolling(period).min()
        features[f"Position_{period}"] = _safe_div(
            close - rolling_low, rolling_high - rolling_low)

    features["RangePct"] = _safe_div(high - low, close)
    features["BodyPct"] = _safe_div(close - open_, open_)
    features["GapPct"] = _safe_div(open_ - close.shift(1), close.shift(1))
    features["RSI_14"] = _rsi(close)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    features["MACD"] = ema12 - ema26
    features["MACDSignal"] = features["MACD"].ewm(span=9, adjust=False).mean()
    features["MACDHist"] = features["MACD"] - features["MACDSignal"]

    true_range = pd.concat(
        [(high - low), (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
        axis=1,
    ).max(axis=1)
    features["ATR_14"] = true_range.rolling(14).mean()
    features["VolumeChange_1"] = volume.pct_change()
    features["VolumeToSMA_5"] = _safe_div(volume, volume.rolling(5).mean()) - 1
    features["VolumeToSMA_20"] = _safe_div(
        volume, volume.rolling(20).mean()) - 1

    if sentiment is None:
        features["Sentiment"] = 0.0
    elif isinstance(sentiment, (int, float)):
        features["Sentiment"] = float(sentiment)
    else:
        s = pd.Series(sentiment, dtype=float)
        features["Sentiment"] = s.reindex(
            features.index, fill_value=0.0).values

    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.ffill().fillna(0.0)
    return features[FEATURE_COLUMNS]


def make_supervised_data(
    feature_frame: pd.DataFrame,
    lookback: int = LOOKBACK,
    future_days: int = FUTURE_DAYS,
):
    features = feature_frame[FEATURE_COLUMNS].astype(float)
    close = feature_frame["Close"].astype(float).to_numpy()

    X_seq, X_flat, y = [], [], []
    for i in range(lookback, len(features) - future_days + 1):
        window = features.iloc[i - lookback:i]
        X_seq.append(window.to_numpy())

        latest = window.iloc[-1].to_numpy()
        short_mean = window.tail(5).mean().to_numpy()
        medium_mean = window.tail(12).mean().to_numpy()
        short_std = window.tail(5).std(ddof=0).to_numpy()
        raw_close_window = window["Close"].tail(10).to_numpy()
        X_flat.append(np.concatenate(
            [latest, short_mean, medium_mean, short_std, raw_close_window]))

        current_price = close[i - 1]
        future_prices = close[i:i + future_days]
        y.append((future_prices - current_price) / current_price)

    return np.asarray(X_seq), np.asarray(X_flat), np.asarray(y)
