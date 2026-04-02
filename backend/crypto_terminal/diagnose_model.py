"""
diagnose_model.py — Run once to inspect the model format and find the right loader.
Run from: backend/crypto_terminal/
"""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(__file__))

MODEL_PATH = "../models/btc_lstm_final_full"

print("=" * 60)
print("STEP 1 — Inspect data.pkl contents")
print("=" * 60)
with open(f"{MODEL_PATH}/data.pkl", "rb") as f:
    obj = pickle.load(f)

print(f"Type of data.pkl contents : {type(obj)}")
if isinstance(obj, dict):
    print(f"Keys                      : {list(obj.keys())[:20]}")
elif hasattr(obj, '__class__'):
    print(f"Class                     : {obj.__class__.__module__}.{obj.__class__.__name__}")
    if hasattr(obj, '__dict__'):
        print(f"Attrs                     : {list(obj.__dict__.keys())[:20]}")

print()
print("=" * 60)
print("STEP 2 — Try keras.saving.load_model")
print("=" * 60)
try:
    import keras
    print(f"keras version: {keras.__version__}")
    model = keras.saving.load_model(MODEL_PATH)
    print(f"✅ SUCCESS: {model.summary()}")
except Exception as e:
    print(f"❌ {e}")

print()
print("=" * 60)
print("STEP 3 — Try tf.saved_model.load")
print("=" * 60)
try:
    import tensorflow as tf
    sm = tf.saved_model.load(MODEL_PATH)
    print(f"✅ SUCCESS: {type(sm)}")
    print(f"Signatures: {list(sm.signatures.keys())}")
except Exception as e:
    print(f"❌ {e}")

print()
print("=" * 60)
print("STEP 4 — Try loading data.pkl as a full model")
print("=" * 60)
with open(f"{MODEL_PATH}/data.pkl", "rb") as f:
    raw = pickle.load(f)

import keras
if isinstance(raw, dict) and "model_config" in raw:
    print(f"model_config present — attempting reconstruction ...")
    try:
        model = keras.models.model_from_json(str(raw["model_config"]))
        print(f"✅ Reconstructed architecture: {model.summary()}")
    except Exception as e:
        print(f"❌ {e}")
elif hasattr(raw, 'predict'):
    print("✅ data.pkl is the model itself!")
else:
    print(f"data.pkl full contents:\n{raw}")

print()
print("=" * 60)
print("STEP 5 — data/0 shape (numpy)")
print("=" * 60)
import numpy as np
for i in range(7):
    arr_path = f"{MODEL_PATH}/data/{i}"
    if os.path.exists(arr_path):
        try:
            arr = np.fromfile(arr_path, dtype=np.float32)
            print(f"  data/{i} → {len(arr)} float32 values  ({os.path.getsize(arr_path)} bytes)")
        except Exception as e:
            print(f"  data/{i} → error reading as float32: {e}")
