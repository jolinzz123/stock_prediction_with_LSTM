# predictor.py
# Handles future price prediction using a trained LSTM model.
# Rolling/recursive multi-step forecasting approach adapted from:
# https://machinelearningmastery.com/multi-step-time-series-forecasting/

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf


def predict_on_test_set(model: tf.keras.Model,
                        X_test: np.ndarray,
                        scaler: MinMaxScaler) -> np.ndarray:
    """
    Generate predictions on the held-out test set and inverse-transform to real prices.

    Parameters:
        model (tf.keras.Model): Trained LSTM model.
        X_test (np.ndarray): Test input sequences.
        scaler (MinMaxScaler): Fitted scaler used during preprocessing.

    Returns:
        np.ndarray: Predicted closing prices in original price scale.
    """
    scaled_predictions = model.predict(X_test, verbose=0)
    predictions = scaler.inverse_transform(scaled_predictions)
    return predictions.flatten()


def predict_future(model: tf.keras.Model,
                   df: pd.DataFrame,
                   scaler: MinMaxScaler,
                   future_days: int,
                   look_back: int = 60) -> np.ndarray:
    """
    Recursively predict future stock prices beyond the available historical data.

    Each predicted value is fed back as input for the next prediction step
    (rolling forecast strategy).

    Parameters:
        model (tf.keras.Model): Trained LSTM model.
        df (pd.DataFrame): Full historical closing price DataFrame.
        scaler (MinMaxScaler): Fitted scaler used during preprocessing.
        future_days (int): Number of future days to predict.
        look_back (int): Number of time steps the model expects as input.

    Returns:
        np.ndarray: Array of future predicted prices (in original scale).
    """
    # Use the most recent `look_back` days as the seed sequence
    last_sequence = scaler.transform(df.values)[-look_back:]
    current_sequence = last_sequence.flatten().tolist()

    future_predictions = []

    for _ in range(future_days):
        # Prepare input: shape (1, look_back, 1)
        input_array = np.array(current_sequence[-look_back:]).reshape(1, look_back, 1)

        # Predict next scaled value
        next_scaled = model.predict(input_array, verbose=0)[0][0]

        future_predictions.append(next_scaled)

        # Append prediction to the rolling window
        current_sequence.append(next_scaled)

    # Inverse-transform back to real price scale
    future_array = np.array(future_predictions).reshape(-1, 1)
    future_prices = scaler.inverse_transform(future_array).flatten()

    return future_prices


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    """
    Compute evaluation metrics comparing actual vs. predicted prices.

    Parameters:
        actual (np.ndarray): True closing prices.
        predicted (np.ndarray): Model-predicted closing prices.

    Returns:
        dict: Dictionary containing RMSE, MAE, and MAPE metrics.
    """
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mae  = np.mean(np.abs(actual - predicted))

    # Avoid division by zero when computing MAPE
    mask = actual != 0
    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

    return {
        "RMSE": round(float(rmse), 4),
        "MAE":  round(float(mae),  4),
        "MAPE": round(float(mape), 2)
    }


def get_trend_signal(future_prices: np.ndarray) -> str:
    """
    Generate a simple trend signal based on the predicted price trajectory.

    Parameters:
        future_prices (np.ndarray): Array of predicted future prices.

    Returns:
        str: One of 'BULLISH 📈', 'BEARISH 📉', or 'SIDEWAYS ➡️'.
    """
    if len(future_prices) < 2:
        return "INSUFFICIENT DATA"

    first_price = future_prices[0]
    last_price  = future_prices[-1]
    change_pct  = ((last_price - first_price) / first_price) * 100

    if change_pct > 1.5:
        return f"BULLISH 📈  (+{change_pct:.2f}%)"
    elif change_pct < -1.5:
        return f"BEARISH 📉  ({change_pct:.2f}%)"
    else:
        return f"SIDEWAYS ➡️  ({change_pct:+.2f}%)"
