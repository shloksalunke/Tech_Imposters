import asyncio, sys, os
from collections import deque
from typing import List

log_buffer: deque = deque(maxlen=1000)
_subscribers: List[asyncio.Queue] = []
_tasks: List[asyncio.Task] = []

# backend/services/ → go up one level → backend/ → crypto_terminal/
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crypto_terminal")

# (script_name, periodic, interval_seconds)
PIPELINES = [
    ("sentiment_pipeline.py", False, 0),
    ("whale_pipeline.py",     False, 0),
    ("signal_generator.py",   False, 0),
    ("lstm_predict.py",       True,  300),  # no internal loop — we restart every 5 min
]

async def _broadcast(msg: str):
    log_buffer.append(msg)
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait(msg)
        except asyncio.QueueFull:
            dead.append(q)
    for d in dead:
        _subscribers.remove(d)

def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=300)
    _subscribers.append(q)
    return q

def unsubscribe(q: asyncio.Queue):
    if q in _subscribers:
        _subscribers.remove(q)

async def _run_once(script: str) -> int:
    path = os.path.join(SCRIPTS_DIR, script)

    # path exist karta hai check karo
    if not os.path.exists(path):
        raise FileNotFoundError(f"Script not found: {path}")

    proc = await asyncio.create_subprocess_exec(
        sys.executable, path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=SCRIPTS_DIR,
    )
    async for raw in proc.stdout:
        await _broadcast(f"[{script}] {raw.decode(errors='replace').rstrip()}")
    return await proc.wait()

async def _loop(script: str, periodic: bool, interval: int):
    await _broadcast(f"[manager] 🚀 Starting {script}")
    while True:
        try:
            if periodic:
                await _run_once(script)
                await _broadcast(f"[manager] ✅ {script} done — next in {interval}s")
                await asyncio.sleep(interval)
            else:
                rc = await _run_once(script)
                await _broadcast(f"[manager] ⚠️ {script} exited (rc={rc}), restarting in 5s")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            # ab proper error dikhega
            await _broadcast(f"[manager] ❌ {script} crashed: {type(e).__name__}: {e} — retry in 10s")
            await asyncio.sleep(10)
async def start_all():
    for script, periodic, interval in PIPELINES:
        _tasks.append(asyncio.create_task(_loop(script, periodic, interval)))
    await _broadcast("[manager] ✅ All 4 pipelines launched")

async def stop_all():
    for t in _tasks:
        t.cancel()
    await asyncio.gather(*_tasks, return_exceptions=True)
    _tasks.clear()