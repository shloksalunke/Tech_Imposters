import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.db_service import get_pool, close_pool
from services.pipeline_manager import start_all, stop_all   # ← new
from routes import sentiment, whales, prediction, signals
from routes.logs import router as logs_router               # ← new
from routes.chart import router as chart_router             # ← new


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    await start_all()          # ← launches all 4 pipeline scripts automatically
    yield
    await stop_all()
    await close_pool()


app = FastAPI(
    title="Crypto Intelligence API",
    description="Real-time crypto signals: LSTM + Ollama sentiment + whale tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentiment.router)
app.include_router(whales.router)
app.include_router(prediction.router)
app.include_router(signals.router)
app.include_router(logs_router)    # GET /api/logs/stream  (SSE)
app.include_router(chart_router)   # GET /api/chart/{BTC|ETH|BNB}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-intelligence-api"}


@app.get("/")
async def root():
    return {
        "endpoints": [
            "/api/sentiment/latest",
            "/api/sentiment/summary",
            "/api/whales",
            "/api/prediction/{symbol}",
            "/api/signals",
            "/api/logs/stream",      # SSE live logs
            "/api/chart/{symbol}",   # historical + predictions
            "/health",
        ]
    }