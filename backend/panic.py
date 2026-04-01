import os
import requests
import pandas as pd
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

if not API_KEY:
    raise ValueError("❌ CRYPTOPANIC_API_KEY not found in .env")

# ================= SYMBOLS =================
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
currencies = ",".join([s.replace("USDT", "") for s in SYMBOLS])

# ================= BASE URL =================
base_url = f"https://cryptopanic.com/api/developer/v2/posts/?auth_token={API_KEY}&kind=news&currencies={currencies}"

# ================= FETCH MULTIPLE PAGES =================
news_list = []

for page in range(1, 6):  # fetch ~100+ news
    url = f"{base_url}&page={page}"
    
    response = requests.get(url, timeout=10)
    data = response.json()
    
    results = data.get("results", [])
    
    if not results:
        break
    
    news_list.extend(results)

print(f"📊 Total news fetched: {len(news_list)}")

# limit for speed (important)
news_list = news_list[:50]

# ================= TIME FILTER =================
now = datetime.now(UTC)
cutoff_date = now - timedelta(days=4)

# ================= LLM SENTIMENT =================
def get_llm_sentiment(text):
    if not text:
        return 0.5, "NEUTRAL"

    text = text[:500]

    prompt = f"""
You are a crypto trading analyst.

Classify the sentiment into:
BULLISH, BEARISH, NEUTRAL, FUD

Give confidence score (0–1).

STRICT FORMAT:
LABEL: <...>
SCORE: <...>

News:
{text}
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral:7b-instruct-q4_K_M",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        output = res.json().get("response", "")

        label = "NEUTRAL"
        score = 0.5

        for line in output.split("\n"):
            if "LABEL" in line.upper():
                label = line.split(":")[-1].strip().upper()
            if "SCORE" in line.upper():
                try:
                    score = float(line.split(":")[-1].strip())
                except:
                    pass

        return score, label

    except Exception as e:
        print("⚠️ LLM error:", e)
        return 0.5, "NEUTRAL"

# ================= PROCESS DATA =================
filtered_news = []

for news in news_list:
    title = news.get("title", "")
    description = news.get("body", "")
    published_at = news.get("published_at", "")

    if not published_at:
        continue

    published_dt = datetime.strptime(
        published_at, "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=UTC)

    if published_dt < cutoff_date:
        continue

    date = published_dt.strftime("%Y-%m-%d")
    time = published_dt.strftime("%H:%M:%S")

    full_text = f"{title}. {description}"

    score, label = get_llm_sentiment(full_text)

    filtered_news.append({
        "Date": date,
        "Time": time,
        "News": title,
        "Score": round(score, 3),
        "Sentiment": label
    })

# ================= DATAFRAME =================
df = pd.DataFrame(filtered_news)

if not df.empty:
    df = df.sort_values(by=["Date", "Time"], ascending=False)

# ================= OUTPUT =================
print("\n📊 Classified Samples:", len(df))
print(df.to_string(index=False))

# ================= SAVE =================
df.to_csv("last_4_days_crypto_sentiment.csv", index=False)

print("\n✅ Saved as last_4_days_crypto_sentiment.csv")