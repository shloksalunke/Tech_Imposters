# lstm_predict.py — PyTorch LSTM Price Forecaster
# Architecture reverse-engineered from .pth weight inspection:
#   lstm1(32→128) → drop1 → lstm2(128→64) → drop2 → lstm3(64→32) → drop3 → fc1(32→16) → relu → fc2(16→1)
#
# NOTE: The model was trained with input_size=32 (not 8).
# If predictions look wrong, ask your teammate for the full list of 32 features.
# Currently the 8 known features are padded to 32 with zeros in positions 8-31.
#
# Read from: binance_data (existing DB, read-only)
# Write to : crypto_terminal.price_forecasts
# Run      : python lstm_predict.py

import os
import sys
import io
import pickle
import warnings
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
from config import (
    COINS, COIN_TABLE_MAP, MODEL_DIR, MODEL_MAP,
    SEQUENCE_LENGTH, FEATURE_COLS
)

# ─── Prediction Horizons (in 15-min steps) ───────────────────────────────────
HORIZONS = {"1h": 4, "4h": 16, "24h": 96}

# Model expects 32 input features (padded from 8 known features)
MODEL_INPUT_SIZE = 32


# ─── Model Architecture ───────────────────────────────────────────────────────
class CryptoLSTM(nn.Module):
    """
    3-layer stacked LSTM + 2-layer FC head.
    Architecture inferred from weight inspection of the .pth files:
      lstm1: LSTM(input=32, hidden=128)
      drop1: Dropout
      lstm2: LSTM(input=128, hidden=64)
      drop2: Dropout
      lstm3: LSTM(input=64, hidden=32)
      drop3: Dropout
      fc1:   Linear(32 → 16)
      relu:  ReLU
      fc2:   Linear(16 → 1)
    """
    def __init__(self, input_size: int = 32, dropout: float = 0.2):
        super().__init__()
        self.lstm1 = nn.LSTM(input_size, 128, batch_first=True)
        self.drop1 = nn.Dropout(dropout)
        self.lstm2 = nn.LSTM(128, 64, batch_first=True)
        self.drop2 = nn.Dropout(dropout)
        self.lstm3 = nn.LSTM(64, 32, batch_first=True)
        self.drop3 = nn.Dropout(dropout)
        self.fc1   = nn.Linear(32, 16)
        self.relu  = nn.ReLU()
        self.fc2   = nn.Linear(16, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        h1, _ = self.lstm1(x)
        h1 = self.drop1(h1)
        h2, _ = self.lstm2(h1)
        h2 = self.drop2(h2)
        h3, _ = self.lstm3(h2)
        h3 = self.drop3(h3)
        last = h3[:, -1, :]      # last timestep output
        out  = self.relu(self.fc1(last))
        return self.fc2(out)     # (batch, 1)


# ─── Custom Unpickler (maps __main__ class → CryptoLSTM) ─────────────────────
class _PthPickle:
    """
    torch.load uses pickle_module.Unpickler to deserialise the file.
    The .pth files were saved with torch.save(model, path) where the model
    class lived in __main__ — remapping it to CryptoLSTM lets PyTorch
    reconstruct the full nn.Module correctly.
    """
    class Unpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == "__main__":
                return CryptoLSTM   # remap to our definition
            return super().find_class(module, name)

    @staticmethod
    def loads(data: bytes, **kwargs):
        return _PthPickle.Unpickler(io.BytesIO(data)).load()


# ─── Load model ───────────────────────────────────────────────────────────────
def load_model(coin: str) -> nn.Module:
    pth_path = os.path.join(MODEL_DIR, f"{MODEL_MAP[coin]}.pth")
    print(f"  📦 Loading {pth_path}")
    model = torch.load(pth_path, map_location="cpu",
                       weights_only=False, pickle_module=_PthPickle)
    model.eval()
    print(f"  ✅ Model loaded  (params={sum(p.numel() for p in model.parameters()):,})")
    return model


# ─── Load scaler from data.pkl ────────────────────────────────────────────────
class _PklPickle:
    """Same remapping for the data.pkl scaler file (also saved in __main__)."""
    class Unpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == "__main__":
                return CryptoLSTM
            return super().find_class(module, name)

    @staticmethod
    def loads(data: bytes, **kwargs):
        return _PklPickle.Unpickler(io.BytesIO(data)).load()


def load_scaler(coin: str):
    """Load MinMaxScaler from models/{coin}_lstm_final_full/data.pkl"""
    scaler_path = os.path.join(MODEL_DIR, MODEL_MAP[coin], "data.pkl")
    print(f"  📦 Loading scaler from {scaler_path}")
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    if hasattr(scaler, "transform"):
        print(f"  ✅ Scaler loaded: {type(scaler).__name__}")
        return scaler
    # data.pkl might contain the model, not the scaler — fall back to None
    print(f"  ⚠️  data.pkl does not appear to be a scaler ({type(scaler).__name__}). "
          f"Predictions will be in scaled space.")
    return None


# ─── Fetch OHLCV from binance_data ───────────────────────────────────────────
def fetch_ohlcv(conn, coin: str) -> pd.DataFrame:
    table  = f"market_data_{COIN_TABLE_MAP[coin]}"
    n_rows = SEQUENCE_LENGTH + 40  # extra rows for rolling window

    query = f"""
        SELECT open_time, open_price, high_price, low_price,
               close_price, volume, close_time, number_of_trades
        FROM {table}
        ORDER BY open_time DESC
        LIMIT {n_rows}
    """
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        raise RuntimeError(f"[fetch_ohlcv] DB query failed: {e}")

    if not rows:
        raise RuntimeError(f"[fetch_ohlcv] No data in {table}")

    df = pd.DataFrame(rows, columns=[
        "open_time", "open_price", "high_price", "low_price",
        "close_price", "volume", "close_time", "number_of_trades"
    ])
    df = df.iloc[::-1].reset_index(drop=True)
    for col in ["open_price", "high_price", "low_price", "close_price",
                "volume", "number_of_trades"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ─── Build features ───────────────────────────────────────────────────────────
def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    Compute the 8 known features, then pad to 32 with zeros.
    Returns (feature_df, current_price).
    """
    df = df.copy()
    df["price_range"]  = df["high_price"] - df["low_price"]
    df["price_change"] = df["close_price"] - df["open_price"]
    df["sma_10"]       = df["close_price"].rolling(10).mean()
    df["sma_30"]       = df["close_price"].rolling(30).mean()
    df["vol_ma"]       = df["volume"].rolling(10).mean()

    df = df.dropna(subset=FEATURE_COLS).reset_index(drop=True)

    current_price = float(df["close_price"].iloc[-1])

    # Take last SEQUENCE_LENGTH rows, extract 8 features
    feat_8 = df[FEATURE_COLS].tail(SEQUENCE_LENGTH).values.astype(np.float32)

    # Simple min-max normalise per column (if no external scaler)
    col_min = feat_8.min(axis=0, keepdims=True)
    col_max = feat_8.max(axis=0, keepdims=True)
    col_range = np.where(col_max - col_min == 0, 1, col_max - col_min)
    feat_8_norm = (feat_8 - col_min) / col_range

    # Pad from 8 → MODEL_INPUT_SIZE (32) with zeros
    n_rows = feat_8_norm.shape[0]
    feat_32 = np.zeros((n_rows, MODEL_INPUT_SIZE), dtype=np.float32)
    feat_32[:, :len(FEATURE_COLS)] = feat_8_norm

    return feat_32, current_price


# ─── Iterative prediction ─────────────────────────────────────────────────────
def predict_n_steps(model: nn.Module, window: np.ndarray, n_steps: int) -> float:
    """
    Slide a SEQUENCE_LENGTH window forward n_steps, predicting one step each time.
    Returns the model's raw output for the last step (close_price proxy).

    window: np.ndarray (SEQUENCE_LENGTH, 32), already normalised
    """
    seq = window.copy()
    last_val = 0.0

    with torch.no_grad():
        for _ in range(n_steps):
            x = torch.tensor(seq, dtype=torch.float32).unsqueeze(0)  # (1, 96, 32)
            pred = model(x)[0, 0].item()   # scalar in [0,1] (normalised)
            last_val = pred

            # Slide: shift window, insert prediction at col 0 of new last row
            new_row = seq[-1].copy()
            new_row[0] = pred         # position 0 = close_price (normalised)
            seq = np.vstack([seq[1:], new_row])

    return last_val  # normalised predicted close


def normalised_to_price(pred_norm: float, feat_8: np.ndarray) -> float:
    """Convert normalised output back to price using the window's close_price range."""
    col = feat_8[:, 0]   # close_price column (raw, un-normalised)
    col_min, col_max = col.min(), col.max()
    if col_max == col_min:
        return col_min
    return float(pred_norm * (col_max - col_min) + col_min)


# ─── Insert forecast ──────────────────────────────────────────────────────────
def insert_forecast(conn, coin: str, current_price: float,
                    predictions: dict, changes: dict, directions: dict):
    sql = """
        INSERT INTO price_forecasts
            (coin, current_price,
             predicted_1h,  predicted_4h,  predicted_24h,
             change_pct_1h, change_pct_4h, change_pct_24h,
             direction_1h,  direction_4h,  direction_24h,
             model_used)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'lstm_pytorch')
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            coin, current_price,
            predictions["1h"],  predictions["4h"],  predictions["24h"],
            changes["1h"],      changes["4h"],      changes["24h"],
            directions["1h"],   directions["4h"],   directions["24h"]
        ))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"[insert_forecast] {e}")


def compute_direction(pct: float) -> str:
    if pct > 0.5:  return "UP"
    if pct < -0.5: return "DOWN"
    return "SIDEWAYS"


# ─── Main ─────────────────────────────────────────────────────────────────────
def run():
    print("=" * 60)
    print("🚀 LSTM Price Forecaster  (PyTorch)")
    print("=" * 60)

    try:
        src_conn = get_connection("binance_data")
        dst_conn = get_connection("crypto_terminal")
    except ConnectionError as e:
        print(f"❌ {e}")
        sys.exit(1)

    for coin in COINS:
        print(f"\n⚙️  Processing {coin} ...")
        try:
            # 1. Load model
            model = load_model(coin)

            # 2. Fetch OHLCV
            df_raw = fetch_ohlcv(src_conn, coin)
            print(f"  ✅ Fetched {len(df_raw)} rows from binance_data")

            # 3. Build features
            feat_32, current_price = build_features(df_raw)
            if feat_32.shape[0] < SEQUENCE_LENGTH:
                print(f"  ⚠️  Not enough rows. Skipping.")
                continue
            print(f"  📊 Current price: ${current_price:,.4f}")

            # Also keep raw 8-feature matrix for inverse transform
            df_copy = df_raw.copy()
            df_copy["price_range"]  = df_copy["high_price"] - df_copy["low_price"]
            df_copy["price_change"] = df_copy["close_price"] - df_copy["open_price"]
            df_copy["sma_10"]       = df_copy["close_price"].rolling(10).mean()
            df_copy["sma_30"]       = df_copy["close_price"].rolling(30).mean()
            df_copy["vol_ma"]       = df_copy["volume"].rolling(10).mean()
            df_copy = df_copy.dropna(subset=FEATURE_COLS)
            feat_8_raw = df_copy[FEATURE_COLS].tail(SEQUENCE_LENGTH).values.astype(np.float32)

            # 4. Predict at each horizon
            predictions, changes, directions = {}, {}, {}
            window = feat_32[-SEQUENCE_LENGTH:]  # already (96, 32)

            for label, n_steps in HORIZONS.items():
                pred_norm  = predict_n_steps(model, window, n_steps)
                pred_price = normalised_to_price(pred_norm, feat_8_raw)
                pct        = (pred_price - current_price) / current_price * 100.0

                predictions[label] = round(pred_price, 8)
                changes[label]     = round(pct, 4)
                directions[label]  = compute_direction(pct)

                print(f"  📈 {label}: ${pred_price:,.4f} ({pct:+.2f}%) → {directions[label]}")

            # 5. Write to DB
            insert_forecast(dst_conn, coin, current_price, predictions, changes, directions)
            print(f"  ✅ Saved to crypto_terminal.price_forecasts")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback; traceback.print_exc()

    src_conn.close()
    dst_conn.close()
    print("\n✅ All forecasts complete.")


if __name__ == "__main__":
    run()
