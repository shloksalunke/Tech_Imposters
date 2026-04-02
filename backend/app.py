# app.py — FastAPI entry point for Crypto Intelligence API
# Pipelines (sentiment, whale, lstm, signal) are run manually in separate terminals.
# This server ONLY serves data from PostgreSQL to the React frontend.

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.db_service import get_pool, close_pool
from routes import sentiment, whales, prediction, signals
from routes.chart import router as chart_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    print("[app] ✅ DB pool ready — server accepting requests")
    yield
    await close_pool()


app = FastAPI(
    title="Crypto Intelligence API",
    description="Real-time crypto signals: LSTM + Ollama sentiment + whale tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentiment.router)
app.include_router(whales.router)
app.include_router(prediction.router)
app.include_router(signals.router)
app.include_router(chart_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-intelligence-api"}