# routes/whales.py
from fastapi import APIRouter
from services.db_service import get_pool

router = APIRouter(prefix="/api/whales", tags=["whales"])


@router.get("")
async def get_whale_transactions():
    """Last 30 whale transactions with direction and value."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                id,
                coin,
                tx_hash,
                from_address,
                to_address,
                value_eth,
                direction,
                whale_signal,
                detected_at
            FROM whale_transactions
            ORDER BY detected_at DESC
            LIMIT 30
        """)
    return [
        {
            "id":           r["id"],
            "coin":         r["coin"],
            "tx_hash":      r["tx_hash"],
            "from_address": (r["from_address"] or "")[:10] + "...",
            "to_address":   (r["to_address"] or "")[:10] + "...",
            "value_eth":    float(r["value_eth"]) if r["value_eth"] else 0.0,
            "direction":    r["direction"] or "UNKNOWN",
            "whale_label":  r["whale_signal"] or "",
            "detected_at":  r["detected_at"].isoformat() if r["detected_at"] else None,
        }
        for r in rows
    ]
