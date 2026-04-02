# routes/sentiment.py
from fastapi import APIRouter
from services.db_service import get_pool

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])


@router.get("/latest")
async def get_latest_sentiment():
    """Latest 50 news sentiment rows across all coins."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT coin, title, score, label, source, published_at
            FROM news_sentiment
            ORDER BY published_at DESC
            LIMIT 50
        """)
    return [
        {
            "coin":         r["coin"],
            "title":        r["title"],
            "score":        float(r["score"]) if r["score"] is not None else 0.5,
            "label":        r["label"] or "NEUTRAL",
            "source":       r["source"] or "",
            "published_at": r["published_at"].isoformat() if r["published_at"] else None,
        }
        for r in rows
    ]


@router.get("/summary")
async def get_sentiment_summary():
    """Per-coin avg score + bullish/bearish % from the last 3 hours."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                coin,
                ROUND(AVG(score)::numeric, 3)                                   AS avg_score,
                COUNT(*)                                                         AS total,
                SUM(CASE WHEN label IN ('BULLISH') THEN 1 ELSE 0 END)           AS bullish_count,
                SUM(CASE WHEN label IN ('BEARISH','FUD') THEN 1 ELSE 0 END)     AS bearish_count,
                MAX(published_at)                                                AS last_seen
            FROM news_sentiment
            WHERE published_at > NOW() - INTERVAL '3 hours'
            GROUP BY coin
            ORDER BY coin
        """)

    result = []
    for r in rows:
        total = r["total"] or 1
        result.append({
            "coin":          r["coin"],
            "avg_score":     float(r["avg_score"]) if r["avg_score"] else 0.5,
            "total_news":    total,
            "bullish_pct":   round(r["bullish_count"] / total * 100, 1),
            "bearish_pct":   round(r["bearish_count"] / total * 100, 1),
            "dominant_label": (
                "BULLISH" if r["bullish_count"] > r["bearish_count"]
                else "BEARISH" if r["bearish_count"] > r["bullish_count"]
                else "NEUTRAL"
            ),
            "last_seen":     r["last_seen"].isoformat() if r["last_seen"] else None,
        })
    return result
