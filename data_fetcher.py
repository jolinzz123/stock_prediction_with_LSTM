# data_fetcher.py
# Handles stock data retrieval and preprocessing for the LSTM model.
# Data fetching approach adapted from yfinance documentation:
# https://pypi.org/project/yfinance/
# Normalization approach adapted from:
# https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html

import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical closing price data for a given stock ticker.

    Parameters:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'TSLA').
        period (str): Historical period to fetch (default: 2 years).

    Returns:
        pd.DataFrame: DataFrame containing the 'Close' price column.

    Raises:
        ValueError: If the ticker is invalid or no data is returned.
    """
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)

    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}'. Please check the symbol and try again.")

    # Keep only the closing price
    close_df = df[['Close']].copy()

    # Drop any rows with missing values
    close_df.dropna(inplace=True)

    if len(close_df) < 100:
        raise ValueError(f"Insufficient data for '{ticker}'. Only {len(close_df)} records found (minimum 100 required).")

    return close_df


def preprocess_data(df: pd.DataFrame, look_back: int = 60):
    """
    Normalize data and create sliding-window sequences for LSTM training.

    Parameters:
        df (pd.DataFrame): Raw closing price DataFrame.
        look_back (int): Number of past days used as input features.

    Returns:
        tuple: (X, y, scaler)
            X (np.ndarray): Input sequences of shape (samples, look_back, 1).
            y (np.ndarray): Target values of shape (samples, 1).
            scaler (MinMaxScaler): Fitted scaler for inverse transformation.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df.values)

    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    X = np.array(X)
    y = np.array(y)

    # Reshape X to (samples, timesteps, features) as required by LSTM
    X = X.reshape((X.shape[0], X.shape[1], 1))

    return X, y, scaler


def train_test_split_timeseries(X: np.ndarray, y: np.ndarray, split_ratio: float = 0.8):
    """
    Split data into training and testing sets while preserving time order.

    Parameters:
        X (np.ndarray): Input sequences.
        y (np.ndarray): Target values.
        split_ratio (float): Proportion of data for training (default: 80%).

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    split_index = int(len(X) * split_ratio)

    X_train = X[:split_index]
    X_test  = X[split_index:]
    y_train = y[:split_index]
    y_test  = y[split_index:]

    return X_train, X_test, y_train, y_test
