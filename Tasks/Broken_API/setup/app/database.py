"""
Database module — SQLite setup and seed data.
"""
import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "/app/store.db")

_connection = None


def get_db() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


def init_db():
    """Create tables and seed data (idempotent)."""
    db = get_db()

    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        sku TEXT UNIQUE NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        status TEXT NOT NULL DEFAULT 'pending',
        total REAL NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES orders(id),
        product_id INTEGER NOT NULL REFERENCES products(id),
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL
    );
    """)

    # Seed only if empty
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        return

    # Users
    db.executemany(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        [
            ("Alice Smith", "alice@example.com"),
            ("Bob Jones", "bob@example.com"),
            ("Carol Davis", "carol@example.com"),
            ("Dave Wilson", "dave@example.com"),
            ("Eve Brown", "eve@example.com"),
        ],
    )

    # Products
    db.executemany(
        "INSERT INTO products (name, price, sku, stock) VALUES (?, ?, ?, ?)",
        [
            ("Widget A", 12.49, "SKU-001", 100),
            ("Widget B", 3.55, "SKU-002", 50),
            ("Gadget C", 2.55, "SKU-003", 200),
            ("Gadget D", 24.99, "SKU-004", 30),
            ("Doohickey E", 7.50, "SKU-005", 75),
            ("Thingamajig F", 15.00, "SKU-006", 45),
            ("Whatsit G", 9.99, "SKU-007", 120),
            ("Gizmo H", 1.99, "SKU-008", 500),
        ],
    )

    # Orders
    db.executemany(
        "INSERT INTO orders (user_id, status, total) VALUES (?, ?, ?)",
        [
            (1, "completed", 24.98),
            (2, "completed", 15.00),
            (2, "pending", 7.50),
            (3, "completed", 9.99),
            (2, "shipped", 49.97),
            (4, "pending", 3.55),
        ],
    )

    # Order items
    db.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        [
            (1, 1, 2, 12.49),
            (2, 6, 1, 15.00),
            (3, 5, 1, 7.50),
            (4, 7, 1, 9.99),
            (5, 4, 1, 24.99),
            (5, 1, 2, 12.49),
            (6, 2, 1, 3.55),
        ],
    )

    db.commit()
