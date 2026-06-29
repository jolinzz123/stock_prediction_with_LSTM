import numpy as np
import pandas as pd

from data_fetcher import clean_ohlcv

# Number of trading days the model looks back to form one input sample
LOOKBACK = 45
# Number of trading days ahead the model predicts
FUTURE_DAYS = 7

# All engineered feature column names in the order the model expects
FEATURE_COLUMNS = [
    # Raw OHLCV prices
    "Open", "High", "Low", "Close", "Adj Close", "Volume",
    # Percentage returns over different horizons
    "Return_1", "Return_2", "Return_3", "Return_5",
    # Absolute price changes over different horizons
    "Delta_1", "Delta_2", "Delta_3", "Delta_5",
    # Momentum: relative change vs N days ago
    "Momentum_3", "Momentum_5", "Momentum_10",
    # Distance from simple moving averages (normalized)
    "CloseToSMA_5", "CloseToSMA_10", "CloseToSMA_20",
    # Rolling standard deviation of daily returns
    "Volatility_5", "Volatility_10", "Volatility_20",
    # Position within rolling high-low range (0 = low, 1 = high)
    "Position_10", "Position_20",
    # Candlestick-derived ratios
    "RangePct", "BodyPct", "GapPct",
    # Technical indicators
    "RSI_14", "MACD", "MACDSignal", "MACDHist", "ATR_14",
    # Volume-based features
    "VolumeChange_1", "VolumeToSMA_5", "VolumeToSMA_20",
    # External news sentiment score
    "Sentiment",
]


def _safe_div(numerator, denominator):
    """Divide two Series, replacing zero denominators with NaN to avoid ZeroDivisionError."""
    return numerator / denominator.replace(0, np.nan)


# RSI calculation adapted from https://www.investopedia.com/terms/r/rsi.asp
def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Compute the Relative Strength Index over a rolling window.

    RSI ranges from 0 to 100; values above 70 suggest overbought,
    below 30 suggest oversold conditions.
    """
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()   # average gain
    loss = (-delta.clip(upper=0)).rolling(window).mean() # average loss
    rs = gain / loss.replace(0, np.nan)                  # relative strength
    return 100 - (100 / (1 + rs))


def build_feature_frame(data, sentiment=None) -> pd.DataFrame:
    """Transform raw OHLCV data into a feature matrix with 38 columns.

    Accepts either a DataFrame or a 1-D array of close prices.
    Optionally incorporates an external sentiment signal.
    """
    # Normalize input into a clean OHLCV DataFrame
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

    # Start with the raw OHLCV columns
    features = df[["Open", "High", "Low",
                   "Close", "Adj Close", "Volume"]].copy()

    # --- Return & delta features: capture short-term price changes ---
    for period in [1, 2, 3, 5]:
        features[f"Return_{period}"] = close.pct_change(period)
        features[f"Delta_{period}"] = close.diff(period)

    # --- Momentum: relative price change vs N days ago ---
    for period in [3, 5, 10]:
        features[f"Momentum_{period}"] = _safe_div(
            close - close.shift(period), close.shift(period))

    # --- SMA distance & volatility: trend and risk measures ---
    for period in [5, 10, 20]:
        sma = close.rolling(period).mean()
        features[f"CloseToSMA_{period}"] = _safe_div(close - sma, sma)
        features[f"Volatility_{period}"] = close.pct_change().rolling(
            period).std()

    # --- Stochastic-style position within rolling high-low range ---
    for period in [10, 20]:
        rolling_high = high.rolling(period).max()
        rolling_low = low.rolling(period).min()
        features[f"Position_{period}"] = _safe_div(
            close - rolling_low, rolling_high - rolling_low)

    # --- Candlestick ratios ---
    features["RangePct"] = _safe_div(high - low, close)          # intraday range as % of close
    features["BodyPct"] = _safe_div(close - open_, open_)        # candle body as % of open
    features["GapPct"] = _safe_div(open_ - close.shift(1), close.shift(1))  # overnight gap

    # --- RSI: momentum oscillator (0-100) ---
    features["RSI_14"] = _rsi(close)

    # MACD indicator adapted from https://www.investopedia.com/terms/m/macd.asp
    ema12 = close.ewm(span=12, adjust=False).mean()   # fast EMA
    ema26 = close.ewm(span=26, adjust=False).mean()   # slow EMA
    features["MACD"] = ema12 - ema26                   # MACD line
    features["MACDSignal"] = features["MACD"].ewm(span=9, adjust=False).mean()  # signal line
    features["MACDHist"] = features["MACD"] - features["MACDSignal"]             # histogram

    # ATR calculation adapted from https://www.investopedia.com/terms/a/atr.asp
    # True Range = max(H-L, |H-prevC|, |L-prevC|)
    true_range = pd.concat(
        [(high - low), (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
        axis=1,
    ).max(axis=1)
    features["ATR_14"] = true_range.rolling(14).mean()

    # --- Volume features: detect unusual trading activity ---
    features["VolumeChange_1"] = volume.pct_change()
    features["VolumeToSMA_5"] = _safe_div(volume, volume.rolling(5).mean()) - 1
    features["VolumeToSMA_20"] = _safe_div(
        volume, volume.rolling(20).mean()) - 1

    # --- Sentiment: external news signal (0.0 if unavailable) ---
    if sentiment is None:
        features["Sentiment"] = 0.0
    elif isinstance(sentiment, (int, float)):
        features["Sentiment"] = float(sentiment)
    else:
        s = pd.Series(sentiment, dtype=float)
        features["Sentiment"] = s.reindex(
            features.index, fill_value=0.0).values

    # Clean up any inf/NaN introduced by rolling calculations
    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.ffill().fillna(0.0)
    return features[FEATURE_COLUMNS]


def make_supervised_data(
    feature_frame: pd.DataFrame,
    lookback: int = LOOKBACK,
    future_days: int = FUTURE_DAYS,
):
    """Convert the feature frame into supervised learning arrays.

    Returns:
        X_seq:  (N, LOOKBACK, n_features) — sequential input for GRU
        X_flat: (N, flattened_dim)         — tabular input for XGBoost
        y:      (N, FUTURE_DAYS)           — target returns (percentage change)
    """
    features = feature_frame[FEATURE_COLUMNS].astype(float)
    close = feature_frame["Close"].astype(float).to_numpy()

    X_seq, X_flat, y = [], [], []

    # Slide a window of size LOOKBACK across the feature frame
    for i in range(lookback, len(features) - future_days + 1):
        window = features.iloc[i - lookback:i]

        # Sequential features: full LOOKBACK x n_features matrix (for GRU)
        X_seq.append(window.to_numpy())

        # Flattened features: summary statistics of the window (for XGBoost)
        latest = window.iloc[-1].to_numpy()              # most recent row
        short_mean = window.tail(5).mean().to_numpy()     # 5-day average
        medium_mean = window.tail(12).mean().to_numpy()   # 12-day average
        short_std = window.tail(5).std(ddof=0).to_numpy() # 5-day std dev
        raw_close_window = window["Close"].tail(10).to_numpy()  # last 10 close prices
        X_flat.append(np.concatenate(
            [latest, short_mean, medium_mean, short_std, raw_close_window]))

        # Target: forward returns for the next FUTURE_DAYS relative to current price
        current_price = close[i - 1]
        future_prices = close[i:i + future_days]
        y.append((future_prices - current_price) / current_price)

    return np.asarray(X_seq), np.asarray(X_flat), np.asarray(y)
