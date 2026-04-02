# services/db_service.py — Async PostgreSQL connection pool via asyncpg
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# crypto_terminal DB credentials (separate from binance_data)
CT_DSN = "postgresql://crypto_user:crypto_pass_123@localhost:5432/crypto_terminal"

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=CT_DSN,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
