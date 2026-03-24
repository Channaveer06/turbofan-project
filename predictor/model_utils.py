import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEQUENCE_LENGTH = 40

FEATURE_COLS = [
    'operational_setting_1', 'operational_setting_2',
    'sensor_2', 'sensor_3', 'sensor_4', 'sensor_6', 'sensor_7',
    'sensor_8', 'sensor_9', 'sensor_11', 'sensor_12', 'sensor_13',
    'sensor_14', 'sensor_15', 'sensor_17', 'sensor_20', 'sensor_21'
]


def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(40, 17)),
        tf.keras.layers.LSTM(128, return_sequences=True),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    return model


# Load model and scaler at module level (cached)
_model = None
_scaler = None


def get_model():
    global _model
    if _model is None:
        _model = build_model()
        weights_path = os.path.join(BASE_DIR, 'turbofan_model.h5')
        _model.load_weights(weights_path)
    return _model


def get_scaler():
    global _scaler
    if _scaler is None:
        scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
        _scaler = joblib.load(scaler_path)
    return _scaler


def predict_rul(df):
    """
    Accepts a DataFrame with required feature columns.
    Returns predicted RUL (float) or None if insufficient data.
    """
    model = get_model()
    scaler = get_scaler()

    df = df[FEATURE_COLS]
    scaled = scaler.transform(df)

    if len(scaled) < SEQUENCE_LENGTH:
        return None, f"Need at least {SEQUENCE_LENGTH} cycles of data (got {len(scaled)})"

    seq = scaled[-SEQUENCE_LENGTH:]
    seq = seq.reshape(1, SEQUENCE_LENGTH, 17)

    prediction = model.predict(seq, verbose=0)
    rul = float(prediction[0][0])

    return max(0.0, rul), None


def get_engine_status(rul):
    """Returns status label, color class, and recommendation."""
    if rul > 80:
        return "HEALTHY", "status-healthy", "Continue normal monitoring schedule."
    elif rul > 30:
        return "WARNING", "status-warning", "Schedule maintenance within the next few cycles."
    else:
        return "CRITICAL", "status-critical", "Immediate maintenance required. Ground the engine."


def get_life_percent(rul, max_rul=125):
    return min(100, int((rul / max_rul) * 100))
