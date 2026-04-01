import requests
import pandas as pd
from textblob import TextBlob
from datetime import datetime, timedelta

# 🔐 Your CryptoPanic API key
API_KEY = "62c36d3e58ac1f4a4c089e449e24b5e436b2ff7e"

# 🌐 API URL
url = f"https://cryptopanic.com/api/developer/v2/posts/?auth_token={API_KEY}&kind=news&currencies=BTC,ETH"
# 📡 Fetch data
response = requests.get(url)
data = response.json()

news_list = data.get("results", [])

# 🗓️ Time filter (last 4 days)
now = datetime.utcnow()
cutoff_date = now - timedelta(days=4)

# 🧠 Sentiment function
def get_sentiment(text):
    if not text:
        return 0.0, "Neutral"
    
    score = TextBlob(text).sentiment.polarity

    if score > 0.1:
        return score, "Bullish"
    elif score < -0.1:
        return score, "Bearish"
    else:
        return score, "Neutral"

# 📊 Process data
filtered_news = []

for news in news_list:
    title = news.get("title", "")
    description = news.get("body", "")
    published_at = news.get("published_at", "")

    # ⏱ Convert time
    if published_at:
        published_dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
    else:
        continue

    # 🔍 Filter last 4 days
    if published_dt < cutoff_date:
        continue

    # 📅 Format date & time
    date = published_dt.strftime("%Y-%m-%d")
    time = published_dt.strftime("%H:%M:%S")

    full_text = f"{title}. {description}"

    score, label = get_sentiment(full_text)

    filtered_news.append({
        "Date": date,
        "Time": time,
        "News": title,
        "Score": round(score, 3),
        "Sentiment": label
    })

# 📄 Create DataFrame
df = pd.DataFrame(filtered_news)

# 🔽 Sort latest first
df = df.sort_values(by=["Date", "Time"], ascending=False)

# 📢 Display table
print(df.to_string(index=False))

# 💾 Save file
df.to_csv("last_4_days_crypto_sentiment.csv", index=False)

print("\n✅ Saved as last_4_days_crypto_sentiment.csv")