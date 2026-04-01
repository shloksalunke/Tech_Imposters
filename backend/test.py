import os
import requests
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

API_KEY = os.getenv("ETHERSCAN_API_KEY")

url = "https://api.etherscan.io/v2/api"

# Binance hot wallet (whale activity)
address = "0x28C6c06298d514Db089934071355E5743bf21d60"

params = {
    "chainid": "1",
    "module": "account",
    "action": "txlist",
    "address": address,
    "startblock": 0,
    "endblock": 99999999,
    "page": 1,
    "offset": 100,
    "sort": "desc",
    "apikey": API_KEY
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

# ================= PROCESS =================
found = False

for tx in data.get("result", []):
    value_eth = int(tx["value"]) / 10**18
    
    if value_eth > 1:
        found = True
        print(f"🐋 Whale Tx: {value_eth:.2f} ETH")
        print(f"From: {tx['from']}")
        print(f"To: {tx['to']}")
        print(f"Tx Hash: {tx['hash']}")
        print("-" * 40)

if not found:
    print("API working ✅ but no whale in this batch")