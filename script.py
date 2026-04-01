import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

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

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
INTERVAL = "15m"
LIMIT = 1000  # max per request


# ================= DB CONNECTION =================
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ================= FETCH DATA =================
def fetch_klines(symbol, start_time=None):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    if start_time:
        params["startTime"] = int(start_time)

    response = requests.get(BINANCE_API_URL, params=params, timeout=10)
    data = response.json()

    return data


# ================= INSERT DATA =================
def insert_rows(rows):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO market_data (
        symbol, open_time, open_price, high_price,
        low_price, close_price, volume,
        close_time, number_of_trades
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (symbol, open_time) DO NOTHING;
    """

    cur.executemany(query, rows)

    conn.commit()
    cur.close()
    conn.close()


# ================= SEED FUNCTION =================
def seed_symbol(symbol, days=180):
    print(f"\n🚀 Seeding {symbol}...")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    current_time = start_time

    total_rows = 0

    while current_time < end_time:
        start_ms = int(current_time.timestamp() * 1000)

        data = fetch_klines(symbol, start_ms)

        if not data:
            print("⚠️ No data received")
            break

        rows = []
        for d in data:
            rows.append((
                symbol,
                d[0], float(d[1]), float(d[2]), float(d[3]),
                float(d[4]), float(d[5]),
                d[6], int(d[8])
            ))

        insert_rows(rows)
        total_rows += len(rows)

        print(f"Inserted {len(rows)} rows for {symbol}")

        # Move forward
        last_open_time = data[-1][0]
        current_time = datetime.utcfromtimestamp(last_open_time / 1000) + timedelta(minutes=15)

    print(f"✅ Done {symbol}: {total_rows} rows inserted")


# ================= MAIN =================
if __name__ == "__main__":
    print("🔥 Starting Binance Data Seeding...\n")

    for symbol in SYMBOLS:
        seed_symbol(symbol, days=180)  # 6 months

    print("\n🎉 All data seeded successfully!")