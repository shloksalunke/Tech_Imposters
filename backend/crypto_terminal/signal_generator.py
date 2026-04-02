# signal_generator.py — LLM-powered Fusion Signal Engine
# Reads price_forecasts, news_sentiment, whale_transactions.
# Uses Ollama (mistral) as the decision engine with a rich prompt.
# Writes BUY/SELL/HOLD signal to the signals table every 5 minutes.
# Run: python signal_generator.py

import sys
import os
import re
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
from config import (
    COINS,
    OLLAMA_MODEL,
    SIGNAL_POLL_INTERVAL,
    SENTIMENT_BULLISH_THRESHOLD,
    SENTIMENT_BEARISH_THRESHOLD,
)

OLLAMA_URL = "http://localhost:11434/api/generate"


# ─── Data Fetchers ────────────────────────────────────────────────────────────

def get_forecast(conn, coin: str) -> dict:
    """Latest LSTM forecast: current price + 1h/4h/24h predictions."""
    sql = """
        SELECT current_price,
               predicted_1h, change_pct_1h, direction_1h,
               predicted_4h, change_pct_4h, direction_4h,
               predicted_24h, change_pct_24h, direction_24h
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
            "pred_1h":        float(row[1]) if row[1] is not None else None,
            "change_pct_1h":  float(row[2]) if row[2] is not None else 0.0,
            "direction_1h":   row[3] or "SIDEWAYS",
            "pred_4h":        float(row[4]) if row[4] is not None else None,
            "change_pct_4h":  float(row[5]) if row[5] is not None else 0.0,
            "direction_4h":   row[6] or "SIDEWAYS",
            "pred_24h":       float(row[7]) if row[7] is not None else None,
            "change_pct_24h": float(row[8]) if row[8] is not None else 0.0,
            "direction_24h":  row[9] or "SIDEWAYS",
        }
    except Exception as e:
        print(f"  ⚠️ [get_forecast] {coin}: {e}")
        return None


def get_sentiment(conn, coin: str) -> tuple:
    """Average sentiment score + dominant label + top headline (last 3 hours)."""
    sql = """
        SELECT AVG(score) AS avg_score, label, title
        FROM news_sentiment
        WHERE coin = %s
          AND published_at > NOW() - INTERVAL '3 hours'
        GROUP BY label, title
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (coin,))
        row = cur.fetchone()
        cur.close()
        if not row or row[0] is None:
            return 0.5, "NEUTRAL", "No recent news"
        return float(row[0]), row[1], row[2]
    except Exception as e:
        print(f"  ⚠️ [get_sentiment] {coin}: {e}")
        return 0.5, "NEUTRAL", "No recent news"


def get_whale_signal(conn, coin: str) -> str:
    """
    Aggregate ETH from OUTFLOW (accumulating) vs INFLOW (distributing)
    over the last 6 hours. Returns human-readable whale activity label.
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
            return "Neutral"
        outflow, inflow = float(row[0]), float(row[1])
        ratio = outflow / max(inflow, 0.001)
        if ratio > 3:   return "Strong Buying"
        if ratio > 1.5: return "Buying"
        if inflow / max(outflow, 0.001) > 3:   return "Strong Selling"
        if inflow / max(outflow, 0.001) > 1.5: return "Selling"
        return "Neutral"
    except Exception as e:
        print(f"  ⚠️ [get_whale_signal] {coin}: {e}")
        return "Neutral"


# ─── Ollama LLM Decision Engine ───────────────────────────────────────────────

SIGNAL_PROMPT = """You are an advanced crypto trading decision engine.

Your task is to analyze multiple signals and generate a final trading recommendation (BUY / SELL / HOLD) along with a confidence score and explanation.

### INPUT DATA:

- Sentiment Score (0 to 1): {sentiment_score}
- Top News/Reddit Title: "{title}"
- Current Price: {current_price}

- Predicted Price:
    - 1 Hour: {pred_1h}
    - 4 Hours: {pred_4h}
    - 24 Hours: {pred_24h}

- Whale Activity:
    - {whale_signal}
    (Options: "Strong Buying", "Buying", "Neutral", "Selling", "Strong Selling")

---

### DECISION RULES:

1. Sentiment Interpretation:
    - > 0.65 → Bullish
    - 0.4 – 0.65 → Neutral
    - < 0.4 → Bearish

2. Price Trend:
    - If all (1h, 4h, 24h) predictions > current price → Strong Uptrend
    - If all < current price → Strong Downtrend
    - Mixed → Sideways / Uncertain

3. Whale Signal Weight:
    - Strong Buying → Strong Bullish
    - Strong Selling → Strong Bearish

---

### FINAL DECISION LOGIC:

- BUY:
    If (Sentiment is Bullish AND Price Trend is Uptrend)
    OR (Whale Buying + any upward prediction)

- SELL:
    If (Sentiment is Bearish AND Price Trend is Downtrend)
    OR (Whale Selling + downward prediction)

- HOLD:
    If signals are mixed or uncertain

---

### CONFIDENCE SCORE (0–100%):

Calculate based on:
- Sentiment strength
- Agreement between predictions (1h, 4h, 24h)
- Whale activity strength

---

### OUTPUT FORMAT:

Return ONLY in this exact format (no extra text):

Signal: BUY / SELL / HOLD
Confidence: XX%

Reason:
- Sentiment: (Bullish / Neutral / Bearish with value)
- Price Trend: (Uptrend / Downtrend / Mixed)
- Whale Activity: (state)
- Key Insight: (1–2 line explanation based on title + data)

---

### IMPORTANT:
- Be logical and consistent
- Do not hallucinate data
- Keep explanation concise but insightful
"""


def ask_ollama(prompt: str) -> str:
    """Send prompt to Ollama and return the raw text response."""
    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model":  OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        res.raise_for_status()
        return res.json().get("response", "").strip()
    except Exception as e:
        print(f"  ⚠️ Ollama error: {e}")
        return ""


def parse_llm_output(output: str) -> tuple:
    """
    Parse the LLM response into (signal, confidence, reason_text).
    Falls back gracefully if format is off.
    """
    signal     = "HOLD"
    confidence = 0.0
    reason     = output.strip()

    for line in output.split("\n"):
        line_upper = line.upper()

        if line_upper.startswith("SIGNAL:"):
            val = line.split(":", 1)[-1].strip().upper()
            if "BUY" in val and "SELL" not in val:
                signal = "BUY"
            elif "SELL" in val:
                signal = "SELL"
            else:
                signal = "HOLD"

        elif line_upper.startswith("CONFIDENCE:"):
            nums = re.findall(r"[\d.]+", line)
            if nums:
                confidence = min(float(nums[0]) / 100.0, 1.0)

    return signal, confidence, reason


# ─── DB Insert ────────────────────────────────────────────────────────────────

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
            coin, signal, round(confidence, 4),
            avg_score, sentiment_label,
            direction_4h, current_price,
            predicted_4h, change_pct_4h,
            whale_signal, reason_text[:2000]
        ))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"  ⚠️ [insert_signal] {coin}: {e}")


# ─── Main Loop ────────────────────────────────────────────────────────────────

SIGNAL_ICONS = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}


def run():
    print("=" * 60)
    print("🧠 LLM Signal Generator  (Ollama → DB)")
    print("=" * 60)
    print(f"  Model  : {OLLAMA_MODEL}")
    print(f"  Coins  : {', '.join(COINS)}")
    print(f"  Interval: {SIGNAL_POLL_INTERVAL}s")

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
                print(f"\n  ── {coin} ──────────────────────────────")

                # 1. LSTM Forecast (1h / 4h / 24h)
                forecast = get_forecast(conn, coin)
                if not forecast:
                    print(f"  ⏭️  No forecast data yet — skipping")
                    continue

                current_price = forecast["current_price"]
                pred_1h       = forecast["pred_1h"]
                pred_4h       = forecast["pred_4h"]
                pred_24h      = forecast["pred_24h"]
                direction_4h  = forecast["direction_4h"]
                change_pct_4h = forecast["change_pct_4h"]

                # 2. News Sentiment
                avg_score, sentiment_label, top_title = get_sentiment(conn, coin)

                # 3. Whale Signal
                whale_signal = get_whale_signal(conn, coin)

                # 4. Build LLM Prompt
                prompt = SIGNAL_PROMPT.format(
                    sentiment_score = round(avg_score, 3),
                    title           = top_title[:120],
                    current_price   = f"${current_price:,.4f}",
                    pred_1h         = f"${pred_1h:,.4f}" if pred_1h else "N/A",
                    pred_4h         = f"${pred_4h:,.4f}" if pred_4h else "N/A",
                    pred_24h        = f"${pred_24h:,.4f}" if pred_24h else "N/A",
                    whale_signal    = whale_signal,
                )

                print(f"  📊 Price: ${current_price:,.2f} | Sentiment: {avg_score:.2f} ({sentiment_label})")
                print(f"  🐋 Whales: {whale_signal}")
                print(f"  📰 News  : {top_title[:70]}")
                print(f"  🤖 Asking Ollama ...")

                # 5. Ask Ollama
                llm_output = ask_ollama(prompt)

                if not llm_output:
                    print(f"  ⚠️  No LLM response — defaulting to HOLD")
                    signal, confidence, reason = "HOLD", 0.0, "Ollama unavailable"
                else:
                    signal, confidence, reason = parse_llm_output(llm_output)

                # 6. Print result
                icon = SIGNAL_ICONS.get(signal, "⚪")
                print(f"  {icon} {coin} → {signal}  (confidence: {confidence*100:.0f}%)")
                print(f"  📝 {reason[:200].replace(chr(10), ' | ')}")

                # 7. Write to DB
                insert_signal(
                    conn, coin, signal, confidence,
                    avg_score, sentiment_label,
                    direction_4h, current_price,
                    pred_4h, change_pct_4h,
                    whale_signal, reason
                )

            except Exception as e:
                import traceback
                print(f"  ❌ [{coin}] Unexpected error: {e}")
                traceback.print_exc()

        conn.close()
        print(f"\n⏳ Sleeping {SIGNAL_POLL_INTERVAL}s ...")
        time.sleep(SIGNAL_POLL_INTERVAL)


if __name__ == "__main__":
    run()
