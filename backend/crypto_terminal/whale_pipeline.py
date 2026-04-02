# whale_pipeline.py — Etherscan Whale Watcher → whale_transactions DB
# Rewrites test.py: same Etherscan fetch, adds direction logic, stores in DB.
# Runs continuously, polling every 60 seconds.
# Run: python whale_pipeline.py

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
from config import WHALE_POLL_INTERVAL

# ─── Load env ─────────────────────────────────────────────────────────────────
load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

if not ETHERSCAN_API_KEY:
    raise ValueError("❌ ETHERSCAN_API_KEY not found in .env")

# 🔹 Wallets to track (mix of exchanges + whales)
WATCH_WALLETS = [
    "0x28c6c06298d514db089934071355e5743bf21d60",  # Binance
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3",  # Coinbase
    "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",  # Kraken
    "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"   # Whale wallet
]

# 🔹 Known exchange wallets
EXCHANGE_WALLETS = {
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase",
    "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0": "Kraken"
}

ETHERSCAN_URL = "https://api.etherscan.io/v2/api"


def fetch_transactions(wallet: str) -> list:
    """Fetch latest transactions from Etherscan for the watched address."""
    params = {
        "chainid":    "1",
        "module":     "account",
        "action":     "txlist",
        "address":    wallet,
        "startblock": 0,
        "endblock":   99999999,
        "page":       1,
        "offset":     20,
        "sort":       "desc",
        "apikey":     ETHERSCAN_API_KEY
    }
    try:
        response = requests.get(ETHERSCAN_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        status = data.get("status", "0")
        if status != "1":
            message = data.get("message", "Unknown error")
            print(f"  ⚠️ Etherscan API warning for {wallet[:8]}: {message}")
            return []

        return data.get("result", [])

    except Exception as e:
        print(f"  ❌ Etherscan fetch error for {wallet[:8]}: {e}")
        return []


def insert_whale_tx(conn, tx: dict, value_eth: float,
                    direction: str, whale_signal: str):
    """
    Insert a whale transaction into whale_transactions.
    ON CONFLICT (tx_hash) DO NOTHING prevents duplicates.
    """
    sql = """
        INSERT INTO whale_transactions
            (tx_hash, coin, value_eth, from_address, to_address,
             direction, whale_signal, block_number)
        VALUES
            (%s, 'ETH', %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tx_hash) DO NOTHING
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            tx["hash"],
            value_eth,
            tx["from"],
            tx["to"],
            direction,
            whale_signal,
            int(tx.get("blockNumber", 0))
        ))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"  ⚠️ DB insert error for tx {tx['hash'][:12]}...: {e}")


def run():
    print("=" * 60)
    print("🐋 Whale Pipeline  (Etherscan → DB)")
    print("=" * 60)

    while True:
        print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Polling Etherscan for {len(WATCH_WALLETS)} wallets ...")

        try:
            conn = get_connection("crypto_terminal")
        except ConnectionError as e:
            print(f"❌ DB connection failed: {e}")
            print(f"⏳ Retrying in {WHALE_POLL_INTERVAL}s ...")
            time.sleep(WHALE_POLL_INTERVAL)
            continue

        saved_count = 0
        total_signal = 0

        for wallet in WATCH_WALLETS:
            print(f"\n🔍 Checking wallet: {wallet}")
            transactions = fetch_transactions(wallet)
            
            for tx in transactions:
                try:
                    value_eth = int(tx["value"]) / 10**18
                except (KeyError, ValueError, TypeError):
                    continue

                # 🐋 Only whale transactions
                if value_eth > 10:
                    from_addr = tx.get("from", "").lower()
                    to_addr = tx.get("to", "").lower()

                    # 🔴 SELL (to exchange)
                    if to_addr in EXCHANGE_WALLETS:
                        action = "🟥 SELL"
                        signal = -value_eth
                        exchange = EXCHANGE_WALLETS[to_addr]
                        direction = "INFLOW"
                        whale_signal = "DISTRIBUTING"

                    # 🟢 BUY (from exchange)
                    elif from_addr in EXCHANGE_WALLETS:
                        action = "🟩 BUY"
                        signal = value_eth
                        exchange = EXCHANGE_WALLETS[from_addr]
                        direction = "OUTFLOW"
                        whale_signal = "ACCUMULATING"

                    # ⚪ NORMAL TRANSFER
                    else:
                        action = "⚪ TRANSFER"
                        signal = 0
                        exchange = "Unknown"
                        direction = "NEUTRAL"
                        whale_signal = "NEUTRAL"

                    total_signal += signal
                    
                    insert_whale_tx(conn, tx, value_eth, direction, whale_signal)
                    saved_count += 1

                    print(f"  {action} | {value_eth:.2f} ETH | Signal: {signal:.2f}")
                    print(f"  Exchange: {exchange}")
                    print(f"  From: {from_addr}")
                    print(f"  To: {to_addr}")
                    print("  " + "-" * 40)
                    
            # Sleep slightly to respect Etherscan rate limits
            time.sleep(0.3)

        conn.close()

        # 🔥 Final Market Sentiment logs
        print("\n==============================")
        print(f"🔥 TOTAL MARKET SIGNAL: {total_signal:.2f}")

        # ✅ Market Bias + Signal
        if total_signal > 0:
            bias = "📈 BULLISH"
            market_signal = +1
        elif total_signal < 0:
            bias = "📉 BEARISH"
            market_signal = -1
        else:
            bias = "⚖️ NEUTRAL"
            market_signal = 0

        print(f"Market Bias: {bias}")
        print(f"Market Signal: {market_signal}")
        print(f"💾 Processed {saved_count} whale txs this cycle.")
        print(f"⏳ Sleeping {WHALE_POLL_INTERVAL}s ...")
        
        time.sleep(WHALE_POLL_INTERVAL)


if __name__ == "__main__":
    run()
