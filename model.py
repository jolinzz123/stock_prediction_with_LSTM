import numpy as np
import tensorflow as tf
from sklearn.linear_model import RidgeCV
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import GRU, Dense, Dropout, Input
from tensorflow.keras.models import Sequential

from feature_engineer import FUTURE_DAYS

EPOCHS = 120
BATCH_SIZE = 8


class _ProgressCallback(tf.keras.callbacks.Callback):
    def __init__(self, total_epochs, fn):
        super().__init__()
        self._total = total_epochs
        self._fn = fn

    def on_epoch_end(self, epoch, logs=None):
        self._fn(epoch + 1, self._total)


# XGBoost multi-output regression adapted from https://xgboost.readthedocs.io/en/stable/python/python_api.html
def train_xgboost(
    X_flat: np.ndarray,
    y_returns: np.ndarray,
    sample_weight: np.ndarray | None = None,
):
    """XGBoost multi-output regressor trained on return targets."""
    from xgboost import XGBRegressor

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_flat)
    model = MultiOutputRegressor(
        XGBRegressor(
            n_estimators=450,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.9,
            colsample_bytree=0.9,
            min_child_weight=1,
            reg_alpha=0.0,
            reg_lambda=0.8,
            random_state=42,
            n_jobs=1,
        ),
        n_jobs=1,
    )
    model.fit(X_scaled, y_returns, sample_weight=sample_weight)
    return model, scaler


def predict_xgboost(model, scaler, X_flat: np.ndarray) -> np.ndarray:
    return model.predict(scaler.transform(X_flat))


# GRU architecture adapted from https://www.tensorflow.org/api_docs/python/tf/keras/layers/GRU
def train_residual_gru(
    X_seq: np.ndarray,
    residuals: np.ndarray,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    epoch_callback=None,
):
    """GRU trained on the residuals left by XGBoost (return space)."""
    future_days = residuals.shape[1]

    feature_scaler = StandardScaler()
    flat = X_seq.reshape(-1, X_seq.shape[-1])
    scaled = feature_scaler.fit_transform(flat).reshape(X_seq.shape)

    residual_scaler = StandardScaler()
    y = residual_scaler.fit_transform(
        residuals.reshape(-1, 1)).reshape(-1, future_days)

    model = Sequential([
        Input(shape=(X_seq.shape[1], X_seq.shape[2])),
        GRU(96, return_sequences=True),
        Dropout(0.05),
        GRU(48),
        Dense(32, activation="relu"),
        Dense(future_days),
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.0008), loss="mse")

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=10,
                      restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", patience=4,
                          factor=0.5, min_lr=0.00005),
    ]
    if epoch_callback:
        callbacks.append(_ProgressCallback(epochs, epoch_callback))

    model.fit(
        scaled, y,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.10,
        callbacks=callbacks,
        verbose=0,
        shuffle=False,
    )
    return model, feature_scaler, residual_scaler


def predict_residual_gru(model, feature_scaler, residual_scaler, X_seq: np.ndarray) -> np.ndarray:
    flat = X_seq.reshape(-1, X_seq.shape[-1])
    scaled = feature_scaler.transform(flat).reshape(X_seq.shape)
    pred_scaled = model.predict(scaled, verbose=0)
    n, fd = pred_scaled.shape
    return residual_scaler.inverse_transform(pred_scaled.reshape(-1, 1)).reshape(n, fd)


def train_meta_stacker(meta_features: np.ndarray, meta_returns: np.ndarray):
    """
    Ridge meta-learner for Stacking.

    Input:  (N, 3 * future_days) — concatenated return predictions from XGBoost+GRU and ARIMA
    Output: (N, future_days)     — optimally weighted return predictions
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(meta_features)
    model = RidgeCV(alphas=np.logspace(-6, 1, 16))
    model.fit(X_scaled, meta_returns)
    return model, scaler


def predict_meta_stacker(model, scaler, meta_features: np.ndarray) -> np.ndarray:
    return model.predict(scaler.transform(meta_features))


# ARIMA forecasting adapted from https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html
def train_predict_arima(close_prices: np.ndarray, future_days: int = FUTURE_DAYS) -> np.ndarray:
    import warnings
    from statsmodels.tsa.arima.model import ARIMA

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = ARIMA(close_prices, order=(5, 1, 2)).fit()
        forecast = result.forecast(steps=future_days)
    return np.asarray(forecast)
