import numpy as np
import pandas as pd

from model import (
    LOOKBACK,
    FUTURE_DAYS,
    build_feature_frame,
    make_supervised_data,
    predict_xgboost,
    predict_residual_gru,
    predict_meta_stacker,
    train_xgboost,
    train_residual_gru,
    train_meta_stacker,
    train_predict_arima,
)


def compute_strategy_metrics(
    test_preds_7d: np.ndarray,
    y_test: np.ndarray,
    close_arr: np.ndarray,
    test_start_idx: int,
    transaction_cost: float = 0.001,
) -> dict:
    """
    Evaluate whether a model has genuine predictive power beyond delayed replication.

    All inputs use price levels (return predictions must be converted to prices before
    calling this function). Direction and IC are computed from implied 1-day returns,
    so the analysis is invariant to the price level and correctly measures signal quality.

    Rolling walk-forward sub-windows give stability estimates across the test period.
    """
    N = len(test_preds_7d)
    if N < 10:
        return {}

    pred_next = test_preds_7d[:, 0]
    actual_next = y_test[:, 0]

    # Price just before each prediction window (the "known" price at signal time)
    current_prices = close_arr[test_start_idx - 1: test_start_idx + N - 1]

    # --- Direction accuracy ---
    pred_dir = np.sign(pred_next - current_prices)
    actual_dir = np.sign(actual_next - current_prices)
    dir_acc = float(np.mean(pred_dir == actual_dir))

    # Naive momentum baseline: predict the same direction as the prior day's move
    prev_prices = close_arr[test_start_idx - 2: test_start_idx + N - 2]
    naive_dir = np.sign(current_prices - prev_prices)
    naive_acc = float(np.mean(naive_dir == actual_dir))

    # --- Information Coefficient (IC) ---
    # Measures whether predicted *returns* correlate with actual *returns*.
    # A model that just outputs yesterday's price has pred_return ≈ 0 → IC ≈ 0.
    pred_return = (pred_next - current_prices) / \
        np.maximum(current_prices, 1e-8)
    actual_return = (actual_next - current_prices) / \
        np.maximum(current_prices, 1e-8)
    if pred_return.std() > 1e-10 and actual_return.std() > 1e-10:
        ic = float(np.corrcoef(pred_return, actual_return)[0, 1])
    else:
        ic = 0.0

    # --- RMSE vs naive lag baseline (predict no change) ---
    model_rmse = float(np.sqrt(np.mean((pred_next - actual_next) ** 2)))
    naive_rmse = float(np.sqrt(np.mean((current_prices - actual_next) ** 2)))

    # --- Long-only strategy simulation ---
    signals = (pred_next > current_prices).astype(float)  # 1 = long, 0 = cash

    strategy_daily = np.zeros(N)
    prev_sig = 0.0
    for i in range(N):
        cost = transaction_cost if signals[i] != prev_sig else 0.0
        strategy_daily[i] = signals[i] * actual_return[i] - cost
        prev_sig = signals[i]

    bnh_daily = actual_return
    strategy_cum = (np.cumprod(1 + strategy_daily) - 1).tolist()
    bnh_cum = (np.cumprod(1 + bnh_daily) - 1).tolist()
    excess_return = float(strategy_cum[-1] - bnh_cum[-1])

    sharpe = (
        float(strategy_daily.mean() / strategy_daily.std() * np.sqrt(252))
        if strategy_daily.std() > 1e-10 else 0.0
    )
    bnh_sharpe = (
        float(bnh_daily.mean() / bnh_daily.std() * np.sqrt(252))
        if bnh_daily.std() > 1e-10 else 0.0
    )

    # --- Rolling walk-forward sub-windows (stability via time-series CV) ---
    win = max(20, N // 4)
    step = max(5, win // 2)
    windows = []
    for s in range(0, N - win + 1, step):
        e = s + win
        wp, wa, wc = pred_next[s:e], actual_next[s:e], current_prices[s:e]
        w_dir = float(np.mean(np.sign(wp - wc) == np.sign(wa - wc)))
        wpr = (wp - wc) / np.maximum(wc, 1e-8)
        war = (wa - wc) / np.maximum(wc, 1e-8)
        w_ic = (
            float(np.corrcoef(wpr, war)[0, 1])
            if wpr.std() > 1e-10 and war.std() > 1e-10 else 0.0
        )
        windows.append({"dir_acc": w_dir, "ic": w_ic})

    return {
        "direction_accuracy": dir_acc,
        "naive_direction_accuracy": naive_acc,
        "information_coefficient": ic,
        "model_rmse": model_rmse,
        "naive_rmse": naive_rmse,
        "sharpe_ratio": sharpe,
        "bnh_sharpe_ratio": bnh_sharpe,
        "excess_return": excess_return,
        "strategy_cum": strategy_cum,
        "bnh_cum": bnh_cum,
        "n_test": N,
        "transaction_cost": transaction_cost,
        "windows": windows,
    }


def _as_price_frame(data) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        close = np.asarray(data, dtype=float).reshape(-1)
        df = pd.DataFrame({
            "Open": close, "High": close, "Low": close,
            "Close": close, "Adj Close": close, "Volume": 0.0,
        })

    close = df["Close"].astype(float)
    for col in ["Open", "High", "Low", "Adj Close"]:
        if col not in df:
            df[col] = close
        df[col] = df[col].astype(float).fillna(close)
    if "Volume" not in df:
        df["Volume"] = 0.0
    df["Volume"] = df["Volume"].astype(float).fillna(0.0)
    return df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].dropna(subset=["Close"])


def _flat_from_window(window: pd.DataFrame) -> np.ndarray:
    latest = window.iloc[-1].to_numpy()
    short_mean = window.tail(5).mean().to_numpy()
    medium_mean = window.tail(12).mean().to_numpy()
    short_std = window.tail(5).std(ddof=0).to_numpy()
    raw_close_window = window["Close"].tail(10).to_numpy()
    return np.concatenate([latest, short_mean, medium_mean, short_std, raw_close_window])


def _arima_walkforward_returns(
    close_arr: np.ndarray, start_idx: int, n_steps: int, future_days: int
) -> np.ndarray:
    """Walk-forward ARIMA forecasts converted to returns vs the price known at each step."""
    out = np.zeros((n_steps, future_days))
    for k in range(n_steps):
        history = close_arr[: start_idx + k]
        price_preds = train_predict_arima(history, future_days=future_days)
        current = close_arr[start_idx + k - 1]
        out[k] = (price_preds - current) / max(current, 1e-8)
    return out


def _forecast_future_stacked(
    df: pd.DataFrame,
    xgb_model, xgb_scaler,
    gru_model, gru_fscaler, gru_tscaler,
    meta_model, meta_scaler,
    close_arr: np.ndarray,
    future_days: int,
    current_sentiment: float = 0.0,
) -> np.ndarray:
    """Return 7-day return predictions from the stacked ensemble for the live forecast."""
    feature_frame = build_feature_frame(df, sentiment=current_sentiment)
    window = feature_frame.tail(LOOKBACK)
    X_seq = window.to_numpy().reshape(1, LOOKBACK, -1)
    X_flat = _flat_from_window(window).reshape(1, -1)

    xgb_pred = predict_xgboost(
        xgb_model, xgb_scaler, X_flat)                        # (1, 7)
    gru_pred = predict_residual_gru(
        gru_model, gru_fscaler, gru_tscaler, X_seq)       # (1, 7)
    # (1, 7)
    xgb_gru = xgb_pred + gru_pred

    arima_prices = train_predict_arima(close_arr, future_days=future_days)
    current = close_arr[-1]
    arima_ret = ((arima_prices - current) / max(current, 1e-8)
                 ).reshape(1, -1)        # (1, 7)

    # (1, 14)
    meta_features = np.hstack([xgb_gru, arima_ret])
    # (7,)
    return predict_meta_stacker(meta_model, meta_scaler, meta_features)[0]


def run_prediction(data, future_days: int = FUTURE_DAYS, epoch_callback=None, sentiment_series=None) -> dict:
    df = _as_price_frame(data)
    if len(df) < LOOKBACK + 50:
        raise ValueError("Not enough historical data to train the model.")

    feature_frame = build_feature_frame(df, sentiment=sentiment_series)
    X_seq, X_flat, y_returns = make_supervised_data(
        feature_frame, future_days=future_days)

    close_arr = df["Close"].to_numpy(dtype=float)
    n = len(y_returns)

    # Time-ordered three-way split:
    #   70% → level-0 training (XGBoost + GRU)
    #   10% → meta-training (out-of-fold predictions for stacking)
    #   20% → held-out test (final evaluation, never touched during training)
    l0_end = int(n * 0.70)
    meta_end = int(n * 0.80)

    # ── Level-0: XGBoost base + GRU residual ──────────────────────────────
    xgb_model, xgb_scaler = train_xgboost(X_flat[:l0_end], y_returns[:l0_end])

    xgb_l0_pred = predict_xgboost(xgb_model, xgb_scaler, X_flat[:l0_end])
    gru_model, gru_fscaler, gru_tscaler = train_residual_gru(
        X_seq[:l0_end],
        y_returns[:l0_end] - xgb_l0_pred,
        epoch_callback=epoch_callback,
    )

    # ── Meta-train: generate out-of-fold predictions on the 10% meta set ──
    xgb_meta = predict_xgboost(xgb_model, xgb_scaler, X_flat[l0_end:meta_end])
    gru_meta = predict_residual_gru(
        gru_model, gru_fscaler, gru_tscaler, X_seq[l0_end:meta_end])
    xgb_gru_meta = xgb_meta + gru_meta

    l0_idx = LOOKBACK + l0_end
    n_meta = meta_end - l0_end
    arima_meta_returns = _arima_walkforward_returns(
        close_arr, l0_idx, n_meta, future_days)

    # Stacking meta-learner: learns optimal combination weights per future day
    meta_features_train = np.hstack(
        [xgb_gru_meta, arima_meta_returns])   # (n_meta, 14)
    meta_model, meta_scaler = train_meta_stacker(
        meta_features_train, y_returns[l0_end:meta_end]
    )

    # ── Test: stacked predictions on the 20% held-out set ─────────────────
    test_start_idx = LOOKBACK + meta_end
    n_test = n - meta_end

    xgb_test = predict_xgboost(xgb_model, xgb_scaler, X_flat[meta_end:])
    gru_test = predict_residual_gru(
        gru_model, gru_fscaler, gru_tscaler, X_seq[meta_end:])
    xgb_gru_test = xgb_test + gru_test

    arima_test_returns = _arima_walkforward_returns(
        close_arr, test_start_idx, n_test, future_days
    )

    test_meta_features = np.hstack(
        [xgb_gru_test, arima_test_returns])    # (n_test, 14)
    stacked_test_returns = predict_meta_stacker(
        meta_model, meta_scaler, test_meta_features
    )                                                                       # (n_test, 7)

    # Convert return predictions → price arrays (for display and metrics)
    current_prices_test = close_arr[test_start_idx -
                                    1: test_start_idx + n_test - 1]
    test_preds_7d = current_prices_test[:, None] * (1.0 + stacked_test_returns)
    y_test = current_prices_test[:, None] * (1.0 + y_returns[meta_end:])
    test_preds = test_preds_7d[:, 0]

    # ── Live forecast: next 7 trading days ────────────────────────────────
    current_sentiment = (
        float(sentiment_series.iloc[-1])
        if sentiment_series is not None and len(sentiment_series) > 0
        else 0.0
    )
    future_returns = _forecast_future_stacked(
        df, xgb_model, xgb_scaler,
        gru_model, gru_fscaler, gru_tscaler,
        meta_model, meta_scaler,
        close_arr, future_days,
        current_sentiment=current_sentiment,
    )
    future_preds = close_arr[-1] * (1.0 + future_returns)

    # ── Per-model strategy metrics (rolling walk-forward CV within test set)
    xgb_test_prices = current_prices_test[:, None] * (1.0 + xgb_test)
    xgb_gru_test_prices = current_prices_test[:, None] * (1.0 + xgb_gru_test)
    arima_test_prices = current_prices_test[:,
                                            None] * (1.0 + arima_test_returns)

    strategy_metrics = {
        "xgb":     compute_strategy_metrics(xgb_test_prices,     y_test, close_arr, test_start_idx),
        "xgb_gru": compute_strategy_metrics(xgb_gru_test_prices, y_test, close_arr, test_start_idx),
        "arima":   compute_strategy_metrics(arima_test_prices,   y_test, close_arr, test_start_idx),
        "stacked": compute_strategy_metrics(test_preds_7d,       y_test, close_arr, test_start_idx),
    }

    return {
        "test_preds":      test_preds,
        "test_preds_7d":   test_preds_7d,
        "y_test":          y_test,
        "test_start_idx":  test_start_idx,
        # vertical line: where level-0 training ended
        "train_end_idx":   LOOKBACK + l0_end,
        "future_preds":    future_preds,
        "strategy_metrics": strategy_metrics,
    }
