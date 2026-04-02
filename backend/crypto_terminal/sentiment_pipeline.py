import os
import sys
import re
import time
import requests
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
from config import OLLAMA_MODEL, SENTIMENT_POLL_INTERVAL

# ================= LOAD ENV =================
load_dotenv()

# ================= CONFIG =================
OLLAMA_URL = "http://localhost:11434/api/chat"
API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

# ================= SYMBOLS =================
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
currencies = ",".join([s.replace("USDT", "") for s in SYMBOLS])

# ================= COIN KEYWORDS =================
COIN_KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth", "ether"],
    "BNB": ["bnb", "binance"],
}

# ================= DETECT COINS =================
def detect_coins(text: str) -> list:
    text_lower = text.lower()
    return [
        coin for coin, keywords in COIN_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]

# ================= FETCH NEWS (UPDATED) =================
def fetch_news() -> list:
    """Fetch news from CryptoPanic API"""
    
    if not API_KEY:
        print("❌ Missing CRYPTOPANIC_API_KEY")
        return []

    base_url = f"https://cryptopanic.com/api/developer/v2/posts/?auth_token={API_KEY}&kind=news&currencies={currencies}"

    articles = []
    seen_titles = set()

    for page in range(1, 4):  # 3 pages = fast + enough
        try:
            url = f"{base_url}&page={page}"
            res = requests.get(url, timeout=10)
            data = res.json()

            results = data.get("results", [])
            if not results:
                break

            for news in results:
                title = news.get("title", "").strip()
                if not title or title in seen_titles:
                    continue

                seen_titles.add(title)

                description = news.get("body", "") or ""
                published_at = news.get("published_at", "")

                try:
                    published_dt = datetime.strptime(
                        published_at, "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=UTC)
                except:
                    continue

                articles.append({
                    "title": title,
                    "summary": description[:400],
                    "published_dt": published_dt,
                    "source": "CryptoPanic"
                })

            print(f"📡 Page {page}: {len(results)} articles")

        except Exception as e:
            print(f"⚠️ API fetch error: {e}")

    print(f"📰 Total articles fetched: {len(articles)}")
    return articles[:60]

# ================= OLLAMA SENTIMENT =================
def get_llm_sentiment(text: str) -> tuple:
    if not text:
        return 0.5, "NEUTRAL"

    text = text[:500]

    prompt = f"""You are an expert cryptocurrency market analyst with deep knowledge of crypto markets, trading psychology, and market sentiment.

Analyze the following crypto news and classify its market sentiment.

SENTIMENT DEFINITIONS:
- BULLISH: Positive news — price increase expected, adoption, partnerships, ETF approvals, whale buying, regulatory clarity
- BEARISH: Negative news — price drop expected, hacks, bans, sell-offs, negative regulation, FUD confirmed
- NEUTRAL: Balanced or insignificant news — minor updates, factual reports with no clear price impact
- FUD: Fear/Uncertainty/Doubt — unverified threats, speculation of bans, quantum threats, panic news

CONFIDENCE SCORING:
- 0.9–1.0 : Extremely clear signal (e.g. ETF approved, major exchange hacked)
- 0.7–0.89: Strong signal with minor ambiguity
- 0.5–0.69: Moderate signal, mixed indicators
- 0.3–0.49: Weak signal, mostly noise
- 0.0–0.29: Very unclear, insufficient information

ANALYSIS STEPS (think step by step):
1. Identify the key event described
2. Determine direct impact on crypto price
3. Assess market psychology (fear vs greed)
4. Assign label and confidence

STRICT OUTPUT FORMAT (no extra text, no explanation):
LABEL: <BULLISH|BEARISH|NEUTRAL|FUD>
SCORE: <0.00 to 1.00>

News to analyze:
{text}
"""

    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=60
        )

        res.raise_for_status()
        output = res.json()["message"]["content"]

        label = "NEUTRAL"
        score = 0.5

        for line in output.split("\n"):
            upper = line.upper()
            if "LABEL" in upper:
                raw = line.split(":")[-1].strip().upper()
                for valid in ["BULLISH", "BEARISH", "NEUTRAL", "FUD"]:
                    if valid in raw:
                        label = valid
                        break
            if "SCORE" in upper:
                try:
                    score = float(re.findall(r"[\d.]+", line)[0])
                except:
                    pass

        return max(0, min(1, score)), label

    except Exception as e:
        print(f"⚠️ Ollama error: {e}")
        return 0.5, "NEUTRAL"

# ================= INSERT =================
def insert_sentiment(conn, coin, published_at, title, score, label, source):
    sql = """
        INSERT INTO news_sentiment
        (coin, published_at, title, score, label, model_used, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (coin, published_at, title[:500], score, label, OLLAMA_MODEL, source))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"⚠️ DB insert error: {e}")

# ================= MAIN LOOP =================
def run():
    print("=" * 60)
    print("🧠 Sentiment Pipeline (CryptoPanic → Ollama → DB)")
    print("=" * 60)
    print(f"Model: {OLLAMA_MODEL}")

    while True:
        print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Fetching news...")

        try:
            conn = get_connection("crypto_terminal")
        except Exception as e:
            print("❌ DB error:", e)
            time.sleep(SENTIMENT_POLL_INTERVAL)
            continue

        cutoff = datetime.now(UTC) - timedelta(days=4)
        articles = fetch_news()

        saved = 0

        for article in articles:
            if article["published_dt"] < cutoff:
                continue

            text = f"{article['title']}. {article['summary']}"
            coins = detect_coins(text)

            if not coins:
                continue

            score, label = get_llm_sentiment(text)

            for coin in coins:
                insert_sentiment(
                    conn,
                    coin,
                    article["published_dt"],
                    article["title"],
                    score,
                    label,
                    article["source"]
                )
                print(f"✅ {coin} | {label} ({score:.2f}) | {article['title'][:60]}")
                saved += 1

        conn.close()

        print(f"\n💾 Saved: {saved}")
        print(f"⏳ Sleeping {SENTIMENT_POLL_INTERVAL}s...\n")
        time.sleep(SENTIMENT_POLL_INTERVAL)

if __name__ == "__main__":
    run()