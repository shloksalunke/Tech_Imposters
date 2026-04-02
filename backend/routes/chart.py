# routes/chart.py — Historical prices + LSTM predictions for chart
import os, datetime
from fastapi import APIRouter, HTTPException
import asyncpg

router = APIRouter(prefix="/api/chart", tags=["chart"])

# binance_data DB (historical OHLCV)
HIST = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
    user=os.getenv("DB_USER", "binance_user"),
    password=os.getenv("DB_PASSWORD", "secure_password_123"),
    database=os.getenv("DB_NAME", "binance_data"),
)

# crypto_terminal DB (predictions)
CRYPTO = dict(
    host="localhost",
    port=5432,
    user="crypto_user",
    password="crypto_pass_123",
    database="crypto_terminal",
)


@router.get("/{symbol}")
async def get_chart(symbol: str, days: int = 90):
    symbol = symbol.upper()
    table = f"market_data_{symbol.lower()}usdt"  # market_data_btcusdt etc.

    # ── historical prices ─────────────────────────────────────────
    try:
        h = await asyncpg.connect(**HIST)

        exists = await h.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name=$1)",
            table
        )
        if not exists:
            await h.close()
            raise HTTPException(404, f"Table {table} not found in binance_data")

        cutoff_ms = int((
            datetime.datetime.utcnow() -
            datetime.timedelta(days=days)
        ).timestamp() * 1000)

        rows = await h.fetch(f"""
            SELECT
                to_timestamp(open_time / 1000.0) AS ts,
                close_price                       AS price
            FROM   {table}
            WHERE  open_time >= $1
            ORDER  BY open_time ASC
        """, cutoff_ms)
        await h.close()

        historical = [
            {"ts": r["ts"].isoformat(), "price": float(r["price"]), "type": "actual"}
            for r in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        historical = []

    # ── LSTM predictions (correct column names) ───────────────────
    try:
        c = await asyncpg.connect(**CRYPTO)
        preds = await c.fetch("""
            SELECT forecasted_at, predicted_1h, predicted_4h, predicted_24h
            FROM   price_forecasts
            WHERE  coin = $1
            ORDER  BY forecasted_at DESC
            LIMIT  100
        """, symbol)
        await c.close()
        predictions = [
            {
                "ts":       r["forecasted_at"].isoformat(),
                "pred_1h":  float(r["predicted_1h"]) if r["predicted_1h"] else 0,
                "pred_4h":  float(r["predicted_4h"]) if r["predicted_4h"] else 0,
                "pred_24h": float(r["predicted_24h"]) if r["predicted_24h"] else 0,
            }
            for r in preds
        ]
    except Exception:
        predictions = []

    return {"symbol": symbol, "historical": historical, "predictions": predictions}