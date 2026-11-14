"""
Smart Poultry Farm Management System - Database Connection & Legacy Helper Layer
Bridges SQLite and MySQL with uniform dictionary-like rows and auto-initialization.
Works alongside models.py (SQLAlchemy ORM) and Flask-Migrate.
"""

import sqlite3
import pymysql
import pymysql.cursors
import os
from datetime import datetime, timezone
from config import Config

DB_PATH = os.path.join(os.path.dirname(__file__), "poultry_farm.db")

class MySQLRowProxy:
    """Wraps PyMySQL dictionary cursor rows to allow both key and index access."""
    def __init__(self, data: dict):
        self._data = data or {}
        self._keys = list(self._data.keys())

    def __getitem__(self, item):
        if isinstance(item, int):
            if 0 <= item < len(self._keys):
                return self._data[self._keys[item]]
            raise IndexError("Row index out of range")
        return self._data.get(item)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, key):
        return key in self._data

class MySQLConnectionWrapper:
    """Wraps PyMySQL connection to provide SQLite-like cursor execution and fetch semantics."""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return self

    def execute(self, sql, params=None):
        # Convert ? placeholders to %s for MySQL
        mysql_sql = sql.replace("?", "%s")
        cursor = self._conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(mysql_sql, params or ())
        self._last_cursor = cursor
        return self

    def fetchone(self):
        if hasattr(self, "_last_cursor"):
            row = self._last_cursor.fetchone()
            return MySQLRowProxy(row) if row else None
        return None

    def fetchall(self):
        if hasattr(self, "_last_cursor"):
            rows = self._last_cursor.fetchall()
            return [MySQLRowProxy(r) for r in rows]
        return []

    @property
    def lastrowid(self):
        return getattr(self._last_cursor, "lastrowid", None)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

def get_db():
    """
    Returns an active database connection.
    Attempts MySQL if DB_ENGINE == 'mysql'; falls back gracefully to SQLite if MySQL is offline.
    """
    if Config.DB_ENGINE == "mysql":
        try:
            raw_conn = pymysql.connect(
                host=Config.DB_HOST,
                port=int(Config.DB_PORT),
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset="utf8mb4",
                autocommit=False
            )
            return MySQLConnectionWrapper(raw_conn)
        except Exception:
            # Fall back to SQLite for local execution
            pass

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(clean=False):
    """
    Ensures all tables (Users, OTP, Farms, Sheds, Flocks, Daily Logs, etc.) exist.
    """
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'farmer',
        mobile_verified INTEGER NOT NULL DEFAULT 0,
        account_status TEXT NOT NULL DEFAULT 'pending',
        language TEXT DEFAULT 'en',
        specialization TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. OTP Verifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        otp_hash TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        is_used INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 3. Farms Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        owner_id INTEGER,
        farm_name TEXT NOT NULL,
        location TEXT,
        address TEXT,
        total_capacity INTEGER DEFAULT 5000,
        farm_type TEXT DEFAULT 'Broiler',
        farm_size TEXT DEFAULT '2 Acres',
        established_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Try adding columns if table was created earlier without them
    for col_def in [
        ("farm_size", "TEXT DEFAULT '2 Acres'"),
        ("established_date", "DATE"),
        ("owner_id", "INTEGER")
    ]:
        try:
            cursor.execute(f"ALTER TABLE farms ADD COLUMN {col_def[0]} {col_def[1]};")
        except Exception:
            pass

    # 4. Sheds Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sheds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        shed_name TEXT NOT NULL,
        capacity INTEGER DEFAULT 1000,
        ventilation_type TEXT DEFAULT 'Tunnel',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
    );
    """)

    # 5. Flocks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        shed_id INTEGER,
        batch_code TEXT NOT NULL,
        batch_number TEXT,
        bird_type TEXT DEFAULT 'Broiler',
        breed TEXT NOT NULL,
        initial_birds INTEGER NOT NULL,
        current_birds INTEGER NOT NULL,
        initial_bird_count INTEGER,
        current_bird_count INTEGER,
        arrival_date DATE NOT NULL,
        expected_sale_date DATE,
        target_weight_kg REAL DEFAULT 2.0,
        status TEXT DEFAULT 'active',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (shed_id) REFERENCES sheds(id) ON DELETE SET NULL
    );
    """)

    # 6. Daily Operations Logs / Daily Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flock_id INTEGER NOT NULL,
        log_date DATE NOT NULL,
        opening_birds INTEGER DEFAULT 0,
        mortality INTEGER DEFAULT 0,
        culls INTEGER DEFAULT 0,
        closing_birds INTEGER DEFAULT 0,
        feed_consumed_kg REAL DEFAULT 0.0,
        water_liters REAL DEFAULT 0.0,
        egg_good INTEGER DEFAULT 0,
        egg_broken INTEGER DEFAULT 0,
        avg_weight_grams REAL DEFAULT 0.0,
        notes TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(flock_id, log_date),
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
    );
    """)

    # 7. Daily Records (Formal Table matching schema requirements)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flock_id INTEGER NOT NULL,
        record_date DATE NOT NULL,
        opening_birds INTEGER NOT NULL,
        mortality INTEGER DEFAULT 0,
        culls INTEGER DEFAULT 0,
        closing_birds INTEGER NOT NULL,
        average_weight_kg REAL DEFAULT 0.0,
        feed_consumed_kg REAL DEFAULT 0.0,
        water_consumed_liters REAL DEFAULT 0.0,
        eggs_produced INTEGER DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(flock_id, record_date),
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
    );
    """)

    # 8. Feed Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feed_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flock_id INTEGER NOT NULL,
        record_date DATE NOT NULL,
        feed_type TEXT NOT NULL,
        quantity_kg REAL NOT NULL,
        unit_cost REAL DEFAULT 0.0,
        total_cost REAL DEFAULT 0.0,
        supplier TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
    );
    """)

    # 9. Egg Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS egg_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flock_id INTEGER NOT NULL,
        record_date DATE NOT NULL,
        eggs_produced INTEGER DEFAULT 0,
        eggs_sold INTEGER DEFAULT 0,
        damaged_eggs INTEGER DEFAULT 0,
        selling_price_per_egg REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
    );
    """)

    # 10. Environment Records / Sensor Readings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS environment_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        flock_id INTEGER,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        temperature_celsius REAL NOT NULL,
        humidity_percentage REAL NOT NULL,
        ammonia_ppm REAL DEFAULT 0.0,
        water_level_pct REAL DEFAULT 100.0,
        feed_level_pct REAL DEFAULT 100.0,
        source TEXT DEFAULT 'IoT_Sensor',
        notes TEXT,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    for col_def in [
        ("water_level_pct", "REAL DEFAULT 100.0"),
        ("feed_level_pct", "REAL DEFAULT 100.0"),
        ("source", "TEXT DEFAULT 'IoT_Sensor'")
    ]:
        try:
            cursor.execute(f"ALTER TABLE environment_records ADD COLUMN {col_def[0]} {col_def[1]};")
        except Exception:
            pass

    # 11. Sensor Readings (IoT Legacy)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shed_id INTEGER NOT NULL,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL,
        ammonia_ppm REAL DEFAULT 10.0,
        water_level_pct REAL DEFAULT 80.0,
        feed_level_pct REAL DEFAULT 75.0,
        light_lux REAL DEFAULT 20.0,
        device_id TEXT DEFAULT 'ESP32-NODE-01',
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (shed_id) REFERENCES sheds(id) ON DELETE CASCADE
    );
    """)

    # 12. Expenses & Finances
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        flock_id INTEGER,
        expense_date DATE NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'Cash',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        flock_id INTEGER,
        transaction_type TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        quantity REAL DEFAULT 0,
        unit_price REAL DEFAULT 0,
        buyer_or_seller TEXT,
        transaction_date DATE NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    # 13. Sales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        flock_id INTEGER,
        sale_date DATE NOT NULL,
        product_type TEXT DEFAULT 'birds',
        quantity REAL NOT NULL,
        unit_price REAL DEFAULT 0.0,
        total_amount REAL NOT NULL,
        buyer_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    # 14. Tasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        flock_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        due_date DATE NOT NULL,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    # 15. Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        shed_id INTEGER,
        flock_id INTEGER,
        alert_type TEXT NOT NULL,
        severity TEXT DEFAULT 'warning',
        message TEXT,
        message_en TEXT,
        message_te TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (shed_id) REFERENCES sheds(id) ON DELETE SET NULL,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    # 16. Feed Inventory (Legacy)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feed_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        feed_name TEXT NOT NULL,
        feed_type TEXT DEFAULT 'Pre-Starter',
        bags_purchased INTEGER NOT NULL,
        bag_weight_kg REAL DEFAULT 50.0,
        cost_per_bag REAL NOT NULL,
        total_quantity_kg REAL NOT NULL,
        stock_remaining_kg REAL NOT NULL,
        purchase_date DATE NOT NULL,
        supplier_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
    );
    """)

    # 17. Vaccinations (Legacy)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vaccinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flock_id INTEGER NOT NULL,
        vaccine_name TEXT NOT NULL,
        scheduled_date DATE NOT NULL,
        administered_date DATE,
        dose_type TEXT DEFAULT 'Eye Drop',
        status TEXT DEFAULT 'scheduled',
        administered_by TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
    );
    """)

    # 18. Weight Logs (Legacy)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weight_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flock_id INTEGER NOT NULL,
        log_date DATE NOT NULL,
        age_days INTEGER NOT NULL,
        sample_weight_grams REAL NOT NULL,
        sample_size INTEGER DEFAULT 10,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
    );
    """)

    # 19. Vet Consultations (Legacy)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vet_consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        vet_id INTEGER,
        flock_id INTEGER,
        subject TEXT NOT NULL,
        symptoms TEXT NOT NULL,
        vet_diagnosis TEXT,
        prescription TEXT,
        recommendation TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
        FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (vet_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema successfully synchronized.")
