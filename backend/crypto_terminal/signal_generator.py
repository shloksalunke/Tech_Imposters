# signal_generator.py — Fusion Signal Engine
# Reads price_forecasts, news_sentiment, whale_transactions.
# Writes BUY/SELL/HOLD signal to the signals table.
# Runs every 5 minutes for BTC, ETH, BNB.
# Run: python signal_generator.py

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
from config import (
    COINS,
    SIGNAL_BUY_THRESHOLD,
    SIGNAL_SELL_THRESHOLD,
    SENTIMENT_BULLISH_THRESHOLD,
    SENTIMENT_BEARISH_THRESHOLD,
    SIGNAL_POLL_INTERVAL
)


# ─── Data fetchers ────────────────────────────────────────────────────────────

def get_forecast(conn, coin: str) -> dict:
    """Latest LSTM forecast for the coin."""
    sql = """
        SELECT current_price, predicted_4h, change_pct_4h, direction_4h
        FROM price_forecasts
        WHERE coin = %s
        ORDER BY forecasted_at DESC
        LIMIT 1
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (coin,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return None

        return {
            "current_price":  float(row[0]),
            "predicted_4h":   float(row[1]) if row[1] is not None else None,
            "change_pct_4h":  float(row[2]) if row[2] is not None else 0.0,
            "direction_4h":   row[3] or "SIDEWAYS"
        }
    except Exception as e:
        print(f"  ⚠️ [get_forecast] {coin}: {e}")
        return None


def get_sentiment(conn, coin: str) -> tuple[float, str]:
    """
    Average sentiment score + dominant label from the last 3 hours.
    Returns (avg_score, label). Defaults to (0.5, 'NEUTRAL') if no data.
    """
    sql = """
        SELECT AVG(score) AS avg_score, label
        FROM news_sentiment
        WHERE coin = %s
          AND published_at > NOW() - INTERVAL '3 hours'
        GROUP BY label
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (coin,))
        row = cur.fetchone()
        cur.close()

        if not row or row[0] is None:
            return 0.5, "NEUTRAL"

        return float(row[0]), row[1]
    except Exception as e:
        print(f"  ⚠️ [get_sentiment] {coin}: {e}")
        return 0.5, "NEUTRAL"


def get_whale_signal(conn, coin: str) -> str:
    """
    Aggregate ETH from OUTFLOW (accumulating) vs INFLOW (distributing)
    over the last 6 hours. Returns ACCUMULATING / DISTRIBUTING / NEUTRAL.
    """
    sql = """
        SELECT
            COALESCE(SUM(CASE WHEN direction = 'OUTFLOW' THEN value_eth ELSE 0 END), 0) AS outflow,
            COALESCE(SUM(CASE WHEN direction = 'INFLOW'  THEN value_eth ELSE 0 END), 0) AS inflow
        FROM whale_transactions
        WHERE coin = %s
          AND detected_at > NOW() - INTERVAL '6 hours'
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (coin,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return "NEUTRAL"

        outflow, inflow = float(row[0]), float(row[1])

        if outflow > inflow * 1.5:
            return "ACCUMULATING"
        elif inflow > outflow * 1.5:
            return "DISTRIBUTING"
        else:
            return "NEUTRAL"

    except Exception as e:
        print(f"  ⚠️ [get_whale_signal] {coin}: {e}")
        return "NEUTRAL"


# ─── Signal computation ───────────────────────────────────────────────────────

def compute_signal(
    avg_score: float, sentiment_label: str,
    direction_4h: str, change_pct_4h: float,
    whale_signal: str
) -> tuple[str, float, list]:
    """
    Weighted scoring:

      Sentiment:    ±2 pts
      LSTM 4h dir:  ±2 pts
      Whale:        ±1 pt

    Thresholds:
      score ≥  3 → BUY
      score ≤ -3 → SELL
      else       → HOLD

    Returns (signal, confidence, reasons)
    """
    score   = 0
    reasons = []

    # ── Sentiment ─────────────────────────────────────────────────
    if avg_score > SENTIMENT_BULLISH_THRESHOLD:
        score += 2
        reasons.append(f"Sentiment BULLISH ({avg_score:.2f})")
    elif avg_score < SENTIMENT_BEARISH_THRESHOLD:
        score -= 2
        reasons.append(f"Sentiment BEARISH ({avg_score:.2f})")

    # ── LSTM price direction ──────────────────────────────────────
    if direction_4h == "UP":
        score += 2
        reasons.append(f"LSTM: +{change_pct_4h:.2f}% in 4h")
    elif direction_4h == "DOWN":
        score -= 2
        reasons.append(f"LSTM: {change_pct_4h:.2f}% in 4h")

    # ── Whale flow ────────────────────────────────────────────────
    if whale_signal == "ACCUMULATING":
        score += 1
        reasons.append("Whales accumulating")
    elif whale_signal == "DISTRIBUTING":
        score -= 1
        reasons.append("Whales distributing")

    # ── Final signal ──────────────────────────────────────────────
    if score >= SIGNAL_BUY_THRESHOLD:
        signal = "BUY"
    elif score <= SIGNAL_SELL_THRESHOLD:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = round(abs(score) / 5.0, 3)
    return signal, confidence, reasons


# ─── DB insert ────────────────────────────────────────────────────────────────

def insert_signal(conn, coin: str, signal: str, confidence: float,
                  avg_score: float, sentiment_label: str,
                  direction_4h: str, current_price: float,
                  predicted_4h: float, change_pct_4h: float,
                  whale_signal: str, reason_text: str):
    sql = """
        INSERT INTO signals
            (coin, signal, confidence,
             sentiment_score, sentiment_label,
             price_direction, current_price,
             predicted_price_4h, change_pct_4h,
             whale_signal, reason_text)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            coin, signal, confidence,
            avg_score, sentiment_label,
            direction_4h, current_price,
            predicted_4h, change_pct_4h,
            whale_signal, reason_text
        ))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"  ⚠️ [insert_signal] {coin}: {e}")


# ─── Main loop ────────────────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("🎯 Signal Generator  (3-source fusion → signals DB)")
    print("=" * 60)

    SIGNAL_ICONS = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}

    while True:
        print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Generating signals ...")

        try:
            conn = get_connection("crypto_terminal")
        except ConnectionError as e:
            print(f"❌ DB connection failed: {e}")
            print(f"⏳ Retrying in {SIGNAL_POLL_INTERVAL}s ...")
            time.sleep(SIGNAL_POLL_INTERVAL)
            continue

        for coin in COINS:
            try:
                # ── 1. Get LSTM forecast ───────────────────────────
                forecast = get_forecast(conn, coin)
                if not forecast:
                    print(f"  ⏭️  [{coin}] No forecast data yet — skipping")
                    continue

                current_price  = forecast["current_price"]
                predicted_4h   = forecast["predicted_4h"]
                change_pct_4h  = forecast["change_pct_4h"]
                direction_4h   = forecast["direction_4h"]

                # ── 2. Get news sentiment ──────────────────────────
                avg_score, sentiment_label = get_sentiment(conn, coin)

                # ── 3. Get whale signal ────────────────────────────
                whale_signal = get_whale_signal(conn, coin)

                # ── 4. Compute signal ──────────────────────────────
                signal, confidence, reasons = compute_signal(
                    avg_score, sentiment_label,
                    direction_4h, change_pct_4h,
                    whale_signal
                )
                reason_text = " · ".join(reasons) if reasons else "Insufficient signals"

                # ── 5. Write to DB ─────────────────────────────────
                insert_signal(
                    conn, coin, signal, confidence,
                    avg_score, sentiment_label,
                    direction_4h, current_price,
                    predicted_4h, change_pct_4h,
                    whale_signal, reason_text
                )

                # ── 6. Print summary ───────────────────────────────
                icon = SIGNAL_ICONS.get(signal, "⚪")
                print(
                    f"  {icon} [{coin}] {signal} ({confidence:.2f}) — {reason_text}"
                )

            except Exception as e:
                print(f"  ❌ [{coin}] Unexpected error: {e}")

        conn.close()
        print(f"\n⏳ Sleeping {SIGNAL_POLL_INTERVAL}s ...")
        time.sleep(SIGNAL_POLL_INTERVAL)


if __name__ == "__main__":
    run()
