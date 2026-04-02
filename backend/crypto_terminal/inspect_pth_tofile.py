"""
inspect_pth_tofile.py — Writes complete architecture to arch_output.txt
"""
import pickle, torch, sys

MODEL_PATH = "../models/btc_lstm_final_full.pth"

class FakeModule(object):
    def __init__(self, *a, **k): pass
    def __setstate__(self, d): self.__dict__.update(d)

class _FakePkl:
    class Unpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module == "__main__": return FakeModule
            return super().find_class(module, name)
    @staticmethod
    def loads(b, **kw):
        import io
        return _FakePkl.Unpickler(io.BytesIO(b)).load()

def walk(obj, prefix=""):
    params = {}
    if not hasattr(obj, "__dict__"): return params
    for k, v in (getattr(obj, "_parameters", {}) or {}).items():
        if v is not None: params[f"{prefix}{k}"] = v
    for k, v in (getattr(obj, "_buffers", {}) or {}).items():
        if v is not None: params[f"{prefix}{k}[buf]"] = v
    for k, child in (getattr(obj, "_modules", {}) or {}).items():
        params.update(walk(child, prefix=f"{prefix}{k}."))
    return params

raw = torch.load(MODEL_PATH, map_location="cpu", weights_only=False, pickle_module=_FakePkl)

lines = []
lines.append(f"Modules: {list((getattr(raw,'_modules',{}) or {}).keys())}")
all_params = walk(raw)
total = 0
for name, tensor in all_params.items():
    n = tensor.numel()
    total += n
    lines.append(f"  {name}  shape={list(tensor.shape)}  n={n}")
lines.append(f"TOTAL params: {total}")

with open("arch_output.txt", "w") as f:
    f.write("\n".join(lines))
print("Written to arch_output.txt")
