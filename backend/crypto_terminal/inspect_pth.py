"""
inspect_pth2.py — Recursively extracts ALL parameter shapes from the loaded .pth model.
From the shapes we can infer the exact LSTM architecture.
"""
import pickle
import torch
import collections

MODEL_PATH = "../models/btc_lstm_final_full.pth"

class FakeModule(object):
    def __init__(self, *a, **k): pass
    def __setstate__(self, d): self.__dict__.update(d)

class _FakePkl:
    class Unpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == "__main__":
                return FakeModule
            return super().find_class(module, name)
    @staticmethod
    def loads(b, **kw):
        import io
        return _FakePkl.Unpickler(io.BytesIO(b)).load()

def walk(obj, prefix=""):
    """Recursively collect (name, tensor) from a FakeModule tree."""
    params = {}
    if not hasattr(obj, "__dict__"):
        return params

    # Direct parameters
    for k, v in (getattr(obj, "_parameters", {}) or {}).items():
        if v is not None:
            params[f"{prefix}{k}"] = v

    # Buffers (non-param tensors like running_mean)
    for k, v in (getattr(obj, "_buffers", {}) or {}).items():
        if v is not None:
            params[f"{prefix}{k} [buf]"] = v

    # Recurse into child modules
    for k, child in (getattr(obj, "_modules", {}) or {}).items():
        child_prefix = f"{prefix}{k}."
        params.update(walk(child, prefix=child_prefix))

    return params

print("=" * 70)
print(f"Loading {MODEL_PATH}")
print("=" * 70)

raw = torch.load(MODEL_PATH, map_location="cpu",
                 weights_only=False, pickle_module=_FakePkl)

print(f"Top-level type  : {type(raw)}")
print(f"Top-level attrs : {[k for k in raw.__dict__ if not k.startswith('_')]}")
print(f"Child modules   : {list((getattr(raw,'_modules',{}) or {}).keys())}")
print()

all_params = walk(raw)
if all_params:
    print("ALL PARAMETERS (name → shape):")
    total = 0
    for name, tensor in all_params.items():
        n = tensor.numel()
        total += n
        print(f"  {name:60s}  shape={str(list(tensor.shape)):25s}  n={n:,}")
    print(f"\n  TOTAL params: {total:,}")
else:
    print("No parameters found via walk(). Dumping raw __dict__:")
    for k, v in raw.__dict__.items():
        if isinstance(v, torch.Tensor):
            print(f"  {k}: tensor shape={list(v.shape)}")
        elif isinstance(v, (dict, collections.OrderedDict)):
            print(f"  {k}: dict keys={list(v.keys())[:10]}")
        else:
            print(f"  {k}: {type(v).__name__} = {str(v)[:80]}")
