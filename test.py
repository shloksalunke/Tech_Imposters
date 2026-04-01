import requests

API_KEY = "74HIK4QIJTTHZQAQR8FTW99FSU83P54P38"

url = "https://api.etherscan.io/v2/api"

# Binance hot wallet (very active = whales guaranteed)
address = "0x28C6c06298d514Db089934071355E5743bf21d60"

params = {
    "chainid": "1",
    "module": "account",
    "action": "txlist",
    "address": address,
    "startblock": 0,
    "endblock": 99999999,
    "page": 1,
    "offset": 100,   # more data = higher chance
    "sort": "desc",
    "apikey": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

# QUICK TEST: print ANY big transactions (>10 ETH)
found = False

for tx in data["result"]:
    value_eth = int(tx["value"]) / 10**18
    
    if value_eth > 1:   # low threshold so it ALWAYS prints
        print(f"🐋 Whale Tx: {value_eth:.2f} ETH")
        print(f"From: {tx['from']}")
        print(f"To: {tx['to']}")
        print(f"Tx Hash: {tx['hash']}")
        print("-" * 40)

if not found:
    print("API working ✅ but no whale in this batch")