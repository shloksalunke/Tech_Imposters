import os
from dotenv import load_dotenv
from binance.client import Client

# Load env
load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

# Connect
client = Client(api_key, api_secret)

# Test connection
print(client.ping())

# Fetch data
klines = client.get_klines(
    symbol="BTCUSDT",
    interval="15m",
    limit=10
)

print("✅ Data fetched successfully!")