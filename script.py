import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# ================= LOAD ENV =================
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dbname": os.getenv("DB_NAME"),
}

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

# 👉 ONLY 3 COINS
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

INTERVAL = "15m"
LIMIT = 1000


# ================= DB CONNECTION =================
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ================= FETCH DATA =================
def fetch_klines(symbol, start_time=None):
    try:
        params = {
            "symbol": symbol,
            "interval": INTERVAL,
            "limit": LIMIT
        }

        if start_time:
            params["startTime"] = int(start_time)

        response = requests.get(BINANCE_API_URL, params=params, timeout=10)

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return []

        return response.json()

    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return []


# ================= INSERT DATA =================
def insert_rows(symbol, rows):
    conn = get_connection()
    cur = conn.cursor()

    table_name = f"market_data_{symbol.lower()}"

    query = f"""
    INSERT INTO {table_name} (
        open_time, open_price, high_price,
        low_price, close_price, volume,
        close_time, number_of_trades
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (open_time) DO NOTHING;
    """

    try:
        cur.executemany(query, rows)
        conn.commit()
    except Exception as e:
        print(f"❌ Insert error ({symbol}): {e}")
    finally:
        cur.close()
        conn.close()


# ================= SEED FUNCTION =================
def seed_symbol(symbol, days=90):   # 👉 3 MONTHS
    print(f"\n🚀 Seeding {symbol}...")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    current_time = start_time
    total_rows = 0

    while current_time < end_time:
        start_ms = int(current_time.timestamp() * 1000)

        data = fetch_klines(symbol, start_ms)

        if not data:
            print("⚠️ No data received, retrying...")
            time.sleep(2)
            continue

        rows = []
        for d in data:
            rows.append((
                d[0], float(d[1]), float(d[2]), float(d[3]),
                float(d[4]), float(d[5]),
                d[6], int(d[8])
            ))

        insert_rows(symbol, rows)
        total_rows += len(rows)

        print(f"✅ {symbol}: Inserted {len(rows)} rows")

        # Move forward
        last_open_time = data[-1][0]
        current_time = datetime.utcfromtimestamp(last_open_time / 1000) + timedelta(minutes=15)

        time.sleep(0.3)  # avoid rate limits

    print(f"🎉 Done {symbol}: {total_rows} rows inserted")


# ================= MAIN =================
if __name__ == "__main__":
    print("🔥 Starting Binance Data Seeding (3 Months)...\n")

    for symbol in SYMBOLS:
        seed_symbol(symbol, days=90)

    print("\n🎯 All data seeded successfully!")