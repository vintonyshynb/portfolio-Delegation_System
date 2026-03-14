import sqlite3

DB = "delegacje.db"


def db():
    return sqlite3.connect(DB)


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols


def init():
    conn = db()
    c = conn.cursor()

    # оригінальний SQL, працює у SQLite
    c.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        distance INTEGER,
        currency TEXT,
        fuel_cost_PLN TEXT DEFAULT '0.00',
        accommodation_cost_PLN TEXT DEFAULT '0.00',
        diet_cost_PLN TEXT DEFAULT '0.00',
        fuel_cost TEXT DEFAULT '0.00',
        accommodation_cost TEXT DEFAULT '0.00',
        diet_cost TEXT DEFAULT '0.00',
        deleted INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
