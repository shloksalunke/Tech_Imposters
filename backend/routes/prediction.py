# routes/prediction.py
from fastapi import APIRouter, HTTPException
from services.db_service import get_pool

router = APIRouter(prefix="/api/prediction", tags=["prediction"])

VALID_COINS = {"BTC", "ETH", "BNB"}


@router.get("/{symbol}")
async def get_prediction(symbol: str):
    """Latest LSTM forecast for a given coin (BTC, ETH, BNB)."""
    coin = symbol.upper().replace("USDT", "")
    if coin not in VALID_COINS:
        raise HTTPException(status_code=404, detail=f"Unknown coin: {symbol}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT
                coin,
                current_price,
                predicted_1h,  change_pct_1h,  direction_1h,
                predicted_4h,  change_pct_4h,  direction_4h,
                predicted_24h, change_pct_24h, direction_24h,
                model_used,
                forecasted_at
            FROM price_forecasts
            WHERE coin = $1
            ORDER BY forecasted_at DESC
            LIMIT 1
        """, coin)

    if not row:
        raise HTTPException(status_code=404, detail=f"No forecast found for {coin}")

    return {
        "coin":           row["coin"],
        "current_price":  float(row["current_price"]),
        "pred_1h":        float(row["predicted_1h"])  if row["predicted_1h"]  else None,
        "change_pct_1h":  float(row["change_pct_1h"]) if row["change_pct_1h"] else 0.0,
        "direction_1h":   row["direction_1h"]  or "SIDEWAYS",
        "pred_4h":        float(row["predicted_4h"])  if row["predicted_4h"]  else None,
        "change_pct_4h":  float(row["change_pct_4h"]) if row["change_pct_4h"] else 0.0,
        "direction_4h":   row["direction_4h"]  or "SIDEWAYS",
        "pred_24h":       float(row["predicted_24h"]) if row["predicted_24h"] else None,
        "change_pct_24h": float(row["change_pct_24h"]) if row["change_pct_24h"] else 0.0,
        "direction_24h":  row["direction_24h"] or "SIDEWAYS",
        "model_used":     row["model_used"],
        "forecasted_at":  row["forecasted_at"].isoformat() if row["forecasted_at"] else None,
    }
