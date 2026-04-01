import os
import sys
from dotenv import load_dotenv
import psycopg2
import psycopg2.extensions
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

# Admin credentials (default PostgreSQL user)
admin_user = "postgres"
admin_password = input("🔐 Enter PostgreSQL admin password (default 'postgres'): ") or "postgres"
admin_host = "localhost"
admin_port = "5432"

# New database credentials
db_name = "binance_data"
db_user = "binance_user"
db_password = "secure_password_123"

logger.info("🚀 PostgreSQL Database Setup")
logger.info("=" * 50)

# Step 1: Connect as admin to create database
try:
    logger.info(f"📌 Connecting as {admin_user}@{admin_host}:{admin_port}")
    admin_conn = psycopg2.connect(
        host=admin_host,
        port=admin_port,
        user=admin_user,
        password=admin_password,
        database="postgres"
    )
    admin_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    admin_cursor = admin_conn.cursor()
    logger.info("✅ Connected to PostgreSQL as admin!")
except Exception as e:
    logger.error(f"❌ Failed to connect as admin: {e}")
    sys.exit(1)

# Step 2: Create user
try:
    logger.info(f"👤 Creating user '{db_user}'...")
    admin_cursor.execute(f"CREATE USER {db_user} WITH PASSWORD %s;", (db_password,))
    logger.info(f"✅ User '{db_user}' created!")
except psycopg2.Error as e:
    if "already exists" in str(e):
        logger.warning(f"⚠️  User '{db_user}' already exists")
    else:
        logger.error(f"❌ Error creating user: {e}")

# Step 3: Create database
try:
    logger.info(f"🗄️  Creating database '{db_name}'...")
    admin_cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user} ENCODING 'UTF8';")
    logger.info(f"✅ Database '{db_name}' created!")
except psycopg2.Error as e:
    if "already exists" in str(e):
        logger.warning(f"⚠️  Database '{db_name}' already exists")
    else:
        logger.error(f"❌ Error creating database: {e}")

# Step 4: Grant privileges
try:
    logger.info(f"🔑 Granting privileges...")
    admin_cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
    logger.info(f"✅ Privileges granted!")
except Exception as e:
    logger.error(f"❌ Error granting privileges: {e}")

admin_cursor.close()
admin_conn.close()

# Step 5: Connect as new user to create tables
try:
    logger.info(f"📌 Connecting as {db_user}@{admin_host}:{admin_port}/{db_name}")
    user_conn = psycopg2.connect(
        host=admin_host,
        port=admin_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    user_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    user_cursor = user_conn.cursor()
    logger.info("✅ Connected to database as new user!")
except Exception as e:
    logger.error(f"❌ Failed to connect as {db_user}: {e}")
    sys.exit(1)

# Step 6: Create tables and indexes
try:
    logger.info("📋 Creating tables...")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS klines (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        interval VARCHAR(10) NOT NULL,
        open_time BIGINT NOT NULL,
        open_price DECIMAL(20, 8) NOT NULL,
        high_price DECIMAL(20, 8) NOT NULL,
        low_price DECIMAL(20, 8) NOT NULL,
        close_price DECIMAL(20, 8) NOT NULL,
        volume DECIMAL(20, 8) NOT NULL,
        close_time BIGINT NOT NULL,
        quote_asset_volume DECIMAL(20, 8),
        number_of_trades INTEGER,
        taker_buy_base_asset_volume DECIMAL(20, 8),
        taker_buy_quote_asset_volume DECIMAL(20, 8),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(symbol, interval, open_time)
    );
    """
    
    user_cursor.execute(create_table_sql)
    logger.info("✅ Table 'klines' created!")
    
    logger.info("📊 Creating indexes...")
    
    user_cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol_interval ON klines(symbol, interval);")
    user_cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_time ON klines(open_time);")
    user_cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON klines(created_at);")
    user_cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON klines(symbol);")
    
    logger.info("✅ Indexes created!")
except Exception as e:
    logger.error(f"❌ Error creating tables: {e}")
    sys.exit(1)

user_cursor.close()
user_conn.close()

# Step 7: Update .env file
logger.info("📝 Updating .env file...")
with open(".env", "r") as f:
    env_content = f.read()

# Add or update database credentials
if "DB_HOST" not in env_content:
    env_content += f"\n# PostgreSQL Configuration\n"
    env_content += f"DB_HOST={admin_host}\n"
    env_content += f"DB_PORT={admin_port}\n"
    env_content += f"DB_USER={db_user}\n"
    env_content += f"DB_PASSWORD={db_password}\n"
    env_content += f"DB_NAME={db_name}\n"
else:
    # Update existing credentials
    env_lines = env_content.split('\n')
    for i, line in enumerate(env_lines):
        if line.startswith('DB_HOST'):
            env_lines[i] = f"DB_HOST={admin_host}"
        elif line.startswith('DB_PORT'):
            env_lines[i] = f"DB_PORT={admin_port}"
        elif line.startswith('DB_USER'):
            env_lines[i] = f"DB_USER={db_user}"
        elif line.startswith('DB_PASSWORD'):
            env_lines[i] = f"DB_PASSWORD={db_password}"
        elif line.startswith('DB_NAME'):
            env_lines[i] = f"DB_NAME={db_name}"
    env_content = '\n'.join(env_lines)

with open(".env", "w") as f:
    f.write(env_content)

logger.info("✅ .env file updated!")

logger.info("\n" + "=" * 50)
logger.info("✨ DATABASE SETUP COMPLETED!")
logger.info("=" * 50)
logger.info("\n📊 Database Details:")
logger.info(f"   Host: {admin_host}")
logger.info(f"   Port: {admin_port}")
logger.info(f"   Database: {db_name}")
logger.info(f"   User: {db_user}")
logger.info(f"   Password: {db_password}")
logger.info("\n✅ Ready to fetch data from Binance!")
logger.info("🚀 Run: python main.py\n")
