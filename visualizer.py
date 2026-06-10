# visualizer.py
# Generates all matplotlib charts for the stock prediction application.
# Matplotlib styling approach adapted from:
# https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def _ensure_assets_dir():
    """Create the assets directory if it doesn't exist."""
    os.makedirs(ASSETS_DIR, exist_ok=True)


def plot_prediction_results(df: pd.DataFrame,
                             test_actual: np.ndarray,
                             test_predicted: np.ndarray,
                             future_prices: np.ndarray,
                             ticker: str,
                             look_back: int = 60,
                             split_ratio: float = 0.8) -> str:
    """
    Plot historical prices, test-set predictions, and future forecast on one chart.

    Parameters:
        df (pd.DataFrame): Full historical closing price DataFrame.
        test_actual (np.ndarray): Actual prices for the test period.
        test_predicted (np.ndarray): Model predictions for the test period.
        future_prices (np.ndarray): Predicted prices for future days.
        ticker (str): Stock ticker symbol (used in title and filename).
        look_back (int): Look-back window used in preprocessing.
        split_ratio (float): Train/test split ratio.

    Returns:
        str: File path of the saved chart image.
    """
    _ensure_assets_dir()

    # --- Build date indices ---
    all_dates = pd.to_datetime(df.index)
    split_idx = int(len(df) * split_ratio)

    # Test period dates (aligned with predictions)
    test_start_idx = split_idx + look_back
    test_dates = all_dates[test_start_idx: test_start_idx + len(test_actual)]

    # Future dates: business days following last historical date
    last_date = all_dates[-1]
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1),
                                  periods=len(future_prices))

    # --- Plot ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 6))

    # Historical training data
    ax.plot(all_dates[:test_start_idx],
            df.values[:test_start_idx],
            color='#4FC3F7', linewidth=1.2, label='Historical (Train)', alpha=0.8)

    # Actual test prices
    ax.plot(test_dates,
            test_actual,
            color='#81C784', linewidth=1.5, label='Actual (Test)')

    # Model predictions on test set
    ax.plot(test_dates,
            test_predicted,
            color='#FFD54F', linewidth=1.5, linestyle='--', label='Predicted (Test)')

    # Future forecast
    ax.plot(future_dates,
            future_prices,
            color='#FF8A65', linewidth=2.0, linestyle=':', label=f'Forecast (+{len(future_prices)}d)',
            marker='o', markersize=3)

    # Vertical divider between historical and forecast
    ax.axvline(x=last_date, color='white', linestyle='--', alpha=0.4, linewidth=1)
    ax.text(last_date, ax.get_ylim()[1] * 0.98, ' Forecast →',
            color='white', fontsize=9, alpha=0.7, va='top')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=30)

    ax.set_title(f'{ticker} — LSTM Stock Price Prediction', fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Closing Price (USD)', fontsize=11)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(alpha=0.2)

    plt.tight_layout()

    save_path = os.path.join(ASSETS_DIR, f"{ticker}_prediction.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_training_loss(history, ticker: str) -> str:
    """
    Plot training and validation loss curves across epochs.

    Parameters:
        history: Keras History object returned by model.fit().
        ticker (str): Stock ticker symbol (used in filename).

    Returns:
        str: File path of the saved chart image.
    """
    _ensure_assets_dir()

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))

    epochs = range(1, len(history.history['loss']) + 1)
    ax.plot(epochs, history.history['loss'],     color='#4FC3F7', label='Training Loss')
    ax.plot(epochs, history.history['val_loss'], color='#FF8A65', label='Validation Loss', linestyle='--')

    ax.set_title(f'{ticker} — Model Training Loss', fontsize=13, fontweight='bold')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('MSE Loss', fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.2)

    plt.tight_layout()

    save_path = os.path.join(ASSETS_DIR, f"{ticker}_loss.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_future_only(df: pd.DataFrame,
                     future_prices: np.ndarray,
                     ticker: str) -> str:
    """
    A focused chart showing just the recent 90 days of history plus the future forecast.

    Parameters:
        df (pd.DataFrame): Full historical DataFrame.
        future_prices (np.ndarray): Predicted future prices.
        ticker (str): Stock ticker symbol.

    Returns:
        str: File path of the saved chart image.
    """
    _ensure_assets_dir()

    recent_df   = df.tail(90)
    recent_dates = pd.to_datetime(recent_df.index)
    last_date    = recent_dates[-1]

    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1),
                                  periods=len(future_prices))

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(recent_dates, recent_df.values,
            color='#4FC3F7', linewidth=1.8, label='Recent History (90d)')

    # Shade the forecast region
    ax.fill_between(future_dates, future_prices * 0.97, future_prices * 1.03,
                    alpha=0.15, color='#FF8A65')
    ax.plot(future_dates, future_prices,
            color='#FF8A65', linewidth=2.2, linestyle='--',
            marker='o', markersize=5, label=f'Forecast (+{len(future_prices)}d)')

    # Annotate start and end forecast price
    ax.annotate(f"${future_prices[0]:.2f}",
                xy=(future_dates[0], future_prices[0]),
                xytext=(8, 8), textcoords='offset points',
                color='#FF8A65', fontsize=9)
    ax.annotate(f"${future_prices[-1]:.2f}",
                xy=(future_dates[-1], future_prices[-1]),
                xytext=(8, -14), textcoords='offset points',
                color='#FF8A65', fontsize=9)

    ax.axvline(x=last_date, color='white', linestyle=':', alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=30)

    ax.set_title(f'{ticker} — {len(future_prices)}-Day Forecast', fontsize=13, fontweight='bold')
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Price (USD)', fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.2)

    plt.tight_layout()

    save_path = os.path.join(ASSETS_DIR, f"{ticker}_forecast.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path
