import sqlite3

def get_conn(db_path="db.sqlite3"):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("""
      CREATE TABLE IF NOT EXISTS order_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE,
        event_type TEXT,
        order_id TEXT,
        payload_json TEXT,
        published_at TEXT,
        received_at TEXT,
        is_duplicate INTEGER DEFAULT 0
      )
    """)
    conn.execute("""
      CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        requested_by_name TEXT,
        requested_by_email TEXT,
        school TEXT,
        department TEXT,
        status TEXT,
        notes TEXT,
        created_at TEXT,
        last_updated TEXT
      )
    """)
    conn.execute("""
      CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        sku TEXT,
        name TEXT,
        qty INTEGER,
        unit TEXT,
        unit_price REAL,
        total REAL,
        FOREIGN KEY(order_id) REFERENCES orders(order_id)
      )
    """)
    conn.commit()
    return conn
