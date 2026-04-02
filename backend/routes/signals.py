# routes/signals.py
from fastapi import APIRouter
from services.db_service import get_pool

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get("")
async def get_signals():
    """Latest BUY/SELL/HOLD signal per coin with confidence and reasoning."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT ON (coin)
                coin,
                signal,
                confidence,
                sentiment_score,
                sentiment_label,
                price_direction,
                current_price,
                predicted_price_4h,
                whale_signal,
                reason_text,
                created_at
            FROM signals
            ORDER BY coin, created_at DESC
        """)

    return [
        {
            "coin":               r["coin"],
            "signal":             r["signal"],
            "confidence":         round(float(r["confidence"]) * 100, 1) if r["confidence"] else 0.0,
            "sentiment_score":    float(r["sentiment_score"]) if r["sentiment_score"] else 0.5,
            "sentiment_label":    r["sentiment_label"] or "NEUTRAL",
            "price_direction":    r["price_direction"] or "SIDEWAYS",
            "current_price":      float(r["current_price"]) if r["current_price"] else 0.0,
            "predicted_price_4h": float(r["predicted_price_4h"]) if r["predicted_price_4h"] else None,
            "whale_signal":       r["whale_signal"] or "Neutral",
            "reason_text":        r["reason_text"] or "",
            "generated_at":       r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]
