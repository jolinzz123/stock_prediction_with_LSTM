# model.py
# Defines, trains, and saves the LSTM model for stock price prediction.
# LSTM architecture inspired by:
# https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
# Dropout regularization technique from:
# https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dropout

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "saved_model", "lstm_stock_model.keras")


def build_model(look_back: int = 60) -> tf.keras.Model:
    """
    Build a two-layer stacked LSTM model with dropout regularization.

    Parameters:
        look_back (int): Number of time steps in each input sequence.

    Returns:
        tf.keras.Model: Compiled LSTM model.
    """
    model = Sequential([
        Input(shape=(look_back, 1)),
        LSTM(128, return_sequences=True),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1)
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='mean_squared_error',
        metrics=['mae']
    )

    return model


def train_model(model: tf.keras.Model,
                X_train: np.ndarray,
                y_train: np.ndarray,
                epochs: int = 30,
                batch_size: int = 32) -> tuple:
    """
    Train the LSTM model with early stopping to prevent overfitting.

    Parameters:
        model (tf.keras.Model): Compiled Keras model.
        X_train (np.ndarray): Training input sequences.
        y_train (np.ndarray): Training target values.
        epochs (int): Maximum number of training epochs.
        batch_size (int): Samples per gradient update.

    Returns:
        tuple: (trained model, training history object)
    """
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=0
    )

    checkpoint = ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor='val_loss',
        save_best_only=True,
        verbose=0
    )

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=[early_stop, checkpoint],
        verbose=1,
        shuffle=False  # Important: preserve time order during training
    )

    return model, history


def save_model(model: tf.keras.Model, path: str = MODEL_SAVE_PATH) -> None:
    """Save the trained model to disk."""
    model.save(path)
    print(f"Model saved to: {path}")


def load_saved_model(path: str = MODEL_SAVE_PATH) -> tf.keras.Model:
    """
    Load a previously saved model from disk.

    Returns:
        tf.keras.Model: The loaded model.

    Raises:
        FileNotFoundError: If no saved model exists at the given path.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No saved model found at '{path}'. Please train the model first.")

    return load_model(path)
