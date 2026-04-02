# db.py — Database connection helper (dual-DB support)

import psycopg2
from config import BINANCE_DB, CRYPTO_DB


def get_connection(db: str = "crypto_terminal"):
    """
    Returns a psycopg2 connection.

    Parameters
    ----------
    db : str
        'crypto_terminal'  → new DB (read + write)
        'binance_data'     → existing Binance DB (read-only)

    Usage
    -----
        conn = get_connection('binance_data')
        cur  = conn.cursor()
        cur.execute("SELECT ...")
        rows = cur.fetchall()
        conn.close()
    """
    if db == "binance_data":
        cfg = BINANCE_DB
    elif db == "crypto_terminal":
        cfg = CRYPTO_DB
    else:
        raise ValueError(f"Unknown database alias '{db}'. Use 'crypto_terminal' or 'binance_data'.")

    try:
        conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            dbname=cfg["dbname"]
        )
        return conn
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"[db.py] Could not connect to '{db}': {e}")
