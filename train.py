"""
train.py — Per-symbol AutoML model store (PyCaret).

Each symbol gets its own model slot in the _models dict.
All models are kept in memory only — nothing is saved to disk.
A per-symbol RLock prevents read/write races in concurrent APScheduler threads.
"""

import logging
import threading
from typing import Optional, Tuple, Dict

import pandas as pd

import config
from features import FEATURE_COLS, TARGET_COL

logger = logging.getLogger(__name__)

# ── In-memory model registry ──────────────────────────────────────────────────
# { "BTCUSDT": <pycaret pipeline>, ... }
_models: Dict[str, object]           = {}
_locks:  Dict[str, threading.RLock]  = {}

# Initialise one lock per symbol at import time
for _sym in config.SYMBOLS:
    _locks[_sym] = threading.RLock()


def _lock(symbol: str) -> threading.RLock:
    return _locks.setdefault(symbol, threading.RLock())


def is_trained(symbol: str) -> bool:
    return symbol in _models and _models[symbol] is not None


# ── Training ──────────────────────────────────────────────────────────────────

def train_model(symbol: str, df: pd.DataFrame) -> bool:
    """
    Run PyCaret AutoML for `symbol` on `df`.
    Stores the finalised model in _models[symbol] — never touches disk.
    """
    try:
        from pycaret.classification import setup, compare_models, finalize_model, pull

        logger.info("[%s] AutoML training on %d rows × %d features…",
                    symbol, len(df), len(FEATURE_COLS))

        train_df = df[FEATURE_COLS + [TARGET_COL]].copy()

        setup(
            data           = train_df,
            target         = TARGET_COL,
            session_id     = config.PYCARET_SESSION_ID,
            verbose        = False,
            html           = False,
            normalize      = True,
            fix_imbalance  = True,
        )

        logger.info("[%s] Comparing top %d classifiers…", symbol, config.N_SELECT_MODELS)
        best = compare_models(n_select=config.N_SELECT_MODELS, sort="AUC", verbose=False)
        best_single = best[0] if isinstance(best, list) else best

        # Log leaderboard
        lb = pull()
        logger.info("[%s] Leaderboard:\n%s", symbol, lb.head(5).to_string())

        final = finalize_model(best_single)

        with _lock(symbol):
            _models[symbol] = final

        logger.info("[%s] Model updated in memory ✓", symbol)
        return True

    except Exception as exc:
        logger.exception("[%s] Training failed: %s", symbol, exc)
        return False


# ── Prediction ────────────────────────────────────────────────────────────────

def predict(symbol: str, feature_row: pd.DataFrame) -> Optional[Tuple[str, float]]:
    """
    Run inference for `symbol`.
    Returns ("UP"/"DOWN", confidence) or None if model not available.
    """
    with _lock(symbol):
        model = _models.get(symbol)

    if model is None:
        logger.warning("[%s] No model in memory — skipping predict.", symbol)
        return None

    try:
        from pycaret.classification import predict_model
        result = predict_model(model, data=feature_row, verbose=False)
        label  = int(result["prediction_label"].iloc[0])
        score  = float(result["prediction_score"].iloc[0])
        direction = "UP" if label == 1 else "DOWN"
        logger.info("[%s] Prediction: %s | Confidence: %.4f", symbol, direction, score)
        return direction, score

    except Exception as exc:
        logger.exception("[%s] Prediction failed: %s", symbol, exc)
        return None