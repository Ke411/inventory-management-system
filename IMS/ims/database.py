"""
IMS - Database Layer
Handles all SQLite operations for the Inventory Management System.
"""
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ims_data.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    """Create all tables and seed default admin user."""
    conn = get_connection()
    c = conn.cursor()

    # ── Users ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname    TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'Staff',
            status      TEXT    NOT NULL DEFAULT 'Active',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Categories ─────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Suppliers ──────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            suppliercode TEXT    NOT NULL UNIQUE,
            fullname     TEXT    NOT NULL,
            location     TEXT,
            phone        TEXT,
            email        TEXT,
            debit        REAL    NOT NULL DEFAULT 0,
            credit       REAL    NOT NULL DEFAULT 0,
            balance      REAL    NOT NULL DEFAULT 0,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Products ───────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            productcode   TEXT    NOT NULL UNIQUE,
            name          TEXT    NOT NULL,
            category_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL,
            description   TEXT,
            quantity      INTEGER NOT NULL DEFAULT 0,
            unit_price    REAL    NOT NULL DEFAULT 0,
            reorder_level INTEGER NOT NULL DEFAULT 5,
            expiry_date   TEXT,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Customers ──────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname   TEXT    NOT NULL,
            phone      TEXT,
            email      TEXT,
            address    TEXT,
            debit      REAL    NOT NULL DEFAULT 0,
            credit     REAL    NOT NULL DEFAULT 0,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Orders (Sales) ─────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT    NOT NULL UNIQUE,
            customer_id  INTEGER REFERENCES customers(id) ON DELETE SET NULL,
            user_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
            total_amount REAL    NOT NULL DEFAULT 0,
            status       TEXT    NOT NULL DEFAULT 'Completed',
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Order Items ────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            quantity   INTEGER NOT NULL,
            unit_price REAL    NOT NULL,
            subtotal   REAL    NOT NULL
        )
    """)

    # ── Purchases (from Suppliers) ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_number TEXT    NOT NULL UNIQUE,
            supplier_id     INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
            user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
            total_amount    REAL    NOT NULL DEFAULT 0,
            status          TEXT    NOT NULL DEFAULT 'Received',
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Purchase Items ─────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL REFERENCES purchases(id) ON DELETE CASCADE,
            product_id  INTEGER REFERENCES products(id) ON DELETE SET NULL,
            quantity    INTEGER NOT NULL,
            unit_cost   REAL    NOT NULL,
            subtotal    REAL    NOT NULL
        )
    """)

    conn.commit()

    # ── Seed default admin ─────────────────────────────────────────────────
    existing = c.execute("SELECT id FROM users WHERE email='admin@ims.com'").fetchone()
    if not existing:
        c.execute("""
            INSERT INTO users (fullname, email, password, role, status)
            VALUES (?, ?, ?, ?, ?)
        """, ('Administrator', 'admin@ims.com', hash_password('admin123'), 'Admin', 'Active'))

    # ── Seed default categories ────────────────────────────────────────────
    default_cats = ['Phones', 'Laptops', 'Accessories', 'Televisions', 'Audio']
    for cat in default_cats:
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  USER OPERATIONS
# ════════════════════════════════════════════════════════════
def authenticate_user(email, password):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=? AND status='Active'",
        (email, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY fullname").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(fullname, email, password, role):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (fullname, email, password, role) VALUES (?,?,?,?)",
            (fullname, email, hash_password(password), role)
        )
        conn.commit()
        return True, "User created successfully."
    except sqlite3.IntegrityError:
        return False, "Email already exists."
    finally:
        conn.close()


def update_user(uid, fullname, email, role, status):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET fullname=?, email=?, role=?, status=? WHERE id=?",
        (fullname, email, role, status, uid)
    )
    conn.commit()
    conn.close()


def delete_user(uid):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  CATEGORY OPERATIONS
# ════════════════════════════════════════════════════════════
def get_all_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_category(name, description=''):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categories (name, description) VALUES (?,?)", (name, description))
        conn.commit()
        return True, "Category created."
    except sqlite3.IntegrityError:
        return False, "Category already exists."
    finally:
        conn.close()


def update_category(cid, name, description):
    conn = get_connection()
    conn.execute("UPDATE categories SET name=?, description=? WHERE id=?", (name, description, cid))
    conn.commit()
    conn.close()


def delete_category(cid):
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id=?", (cid,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  SUPPLIER OPERATIONS
# ════════════════════════════════════════════════════════════
def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY fullname").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_supplier(suppliercode, fullname, location, phone, email):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO suppliers (suppliercode, fullname, location, phone, email) VALUES (?,?,?,?,?)",
            (suppliercode, fullname, location, phone, email)
        )
        conn.commit()
        return True, "Supplier created."
    except sqlite3.IntegrityError:
        return False, "Supplier code already exists."
    finally:
        conn.close()


def update_supplier(sid, suppliercode, fullname, location, phone, email):
    conn = get_connection()
    conn.execute(
        "UPDATE suppliers SET suppliercode=?, fullname=?, location=?, phone=?, email=? WHERE id=?",
        (suppliercode, fullname, location, phone, email, sid)
    )
    conn.commit()
    conn.close()


def delete_supplier(sid):
    conn = get_connection()
    conn.execute("DELETE FROM suppliers WHERE id=?", (sid,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  PRODUCT OPERATIONS
# ════════════════════════════════════════════════════════════
def get_all_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_low_stock_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.quantity <= p.reorder_level
        ORDER BY p.quantity ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_product(productcode, name, category_id, description, quantity, unit_price, reorder_level, expiry_date):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO products (productcode, name, category_id, description, quantity, unit_price, reorder_level, expiry_date)
            VALUES (?,?,?,?,?,?,?,?)
        """, (productcode, name, category_id, description, quantity, unit_price, reorder_level, expiry_date or None))
        conn.commit()
        return True, "Product created."
    except sqlite3.IntegrityError:
        return False, "Product code already exists."
    finally:
        conn.close()


def update_product(pid, productcode, name, category_id, description, quantity, unit_price, reorder_level, expiry_date):
    conn = get_connection()
    conn.execute("""
        UPDATE products SET productcode=?, name=?, category_id=?, description=?,
        quantity=?, unit_price=?, reorder_level=?, expiry_date=? WHERE id=?
    """, (productcode, name, category_id, description, quantity, unit_price, reorder_level, expiry_date or None, pid))
    conn.commit()
    conn.close()


def delete_product(pid):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  CUSTOMER OPERATIONS
# ════════════════════════════════════════════════════════════
def get_all_customers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM customers ORDER BY fullname").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_customer(fullname, phone, email, address):
    conn = get_connection()
    conn.execute(
        "INSERT INTO customers (fullname, phone, email, address) VALUES (?,?,?,?)",
        (fullname, phone, email, address)
    )
    conn.commit()
    conn.close()


def update_customer(cid, fullname, phone, email, address):
    conn = get_connection()
    conn.execute(
        "UPDATE customers SET fullname=?, phone=?, email=?, address=? WHERE id=?",
        (fullname, phone, email, address, cid)
    )
    conn.commit()
    conn.close()


def delete_customer(cid):
    conn = get_connection()
    conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
#  ORDER (SALES) OPERATIONS
# ════════════════════════════════════════════════════════════
def generate_order_number():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{count+1:04d}"


def create_order(customer_id, user_id, items):
    """
    items = list of {'product_id': int, 'quantity': int, 'unit_price': float}
    """
    conn = get_connection()
    try:
        order_number = generate_order_number()
        total = sum(i['quantity'] * i['unit_price'] for i in items)

        conn.execute("""
            INSERT INTO orders (order_number, customer_id, user_id, total_amount)
            VALUES (?,?,?,?)
        """, (order_number, customer_id, user_id, total))
        order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in items:
            subtotal = item['quantity'] * item['unit_price']
            conn.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (?,?,?,?,?)
            """, (order_id, item['product_id'], item['quantity'], item['unit_price'], subtotal))
            # Deduct stock
            conn.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id=?",
                (item['quantity'], item['product_id'])
            )
            # Update customer credit
            conn.execute(
                "UPDATE customers SET credit = credit + ? WHERE id=?",
                (subtotal, customer_id)
            )

        conn.commit()
        return True, order_number
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_orders():
    conn = get_connection()
    rows = conn.execute("""
        SELECT o.*, c.fullname as customer_name, u.fullname as staff_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order_items(order_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT oi.*, p.name as product_name, p.productcode
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════
#  PURCHASE OPERATIONS
# ════════════════════════════════════════════════════════════
def generate_purchase_number():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM purchases").fetchone()[0]
    conn.close()
    return f"PUR-{datetime.now().strftime('%Y%m%d')}-{count+1:04d}"


def create_purchase(supplier_id, user_id, items):
    conn = get_connection()
    try:
        purchase_number = generate_purchase_number()
        total = sum(i['quantity'] * i['unit_cost'] for i in items)

        conn.execute("""
            INSERT INTO purchases (purchase_number, supplier_id, user_id, total_amount)
            VALUES (?,?,?,?)
        """, (purchase_number, supplier_id, user_id, total))
        purchase_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in items:
            subtotal = item['quantity'] * item['unit_cost']
            conn.execute("""
                INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost, subtotal)
                VALUES (?,?,?,?,?)
            """, (purchase_id, item['product_id'], item['quantity'], item['unit_cost'], subtotal))
            conn.execute(
                "UPDATE products SET quantity = quantity + ? WHERE id=?",
                (item['quantity'], item['product_id'])
            )
            conn.execute(
                "UPDATE suppliers SET debit = debit + ? WHERE id=?",
                (subtotal, supplier_id)
            )

        conn.commit()
        return True, purchase_number
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_purchases():
    conn = get_connection()
    rows = conn.execute("""
        SELECT pu.*, s.fullname as supplier_name, u.fullname as staff_name
        FROM purchases pu
        LEFT JOIN suppliers s ON pu.supplier_id = s.id
        LEFT JOIN users u ON pu.user_id = u.id
        ORDER BY pu.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_purchase_items(purchase_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT pi.*, p.name as product_name, p.productcode
        FROM purchase_items pi
        LEFT JOIN products p ON pi.product_id = p.id
        WHERE pi.purchase_id = ?
    """, (purchase_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════
#  DASHBOARD STATS
# ════════════════════════════════════════════════════════════
def get_dashboard_stats():
    conn = get_connection()
    stats = {}
    stats['total_products']  = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    stats['total_customers'] = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    stats['total_suppliers'] = conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
    stats['total_orders']    = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    stats['total_sales']     = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders").fetchone()[0]
    stats['total_purchases'] = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM purchases").fetchone()[0]
    stats['low_stock']       = conn.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= reorder_level"
    ).fetchone()[0]
    stats['monthly_sales']   = conn.execute("""
        SELECT COALESCE(SUM(total_amount),0) FROM orders
        WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
    """).fetchone()[0]
    conn.close()
    return stats


# ════════════════════════════════════════════════════════════
#  REPORT QUERIES
# ════════════════════════════════════════════════════════════
def report_sales_by_period(start_date, end_date):
    conn = get_connection()
    rows = conn.execute("""
        SELECT o.order_number, o.created_at, c.fullname as customer,
               u.fullname as staff, o.total_amount, o.status
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN users u ON o.user_id = u.id
        WHERE date(o.created_at) BETWEEN ? AND ?
        ORDER BY o.created_at DESC
    """, (start_date, end_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def report_inventory_status():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.productcode, p.name, c.name as category,
               p.quantity, p.reorder_level, p.unit_price,
               (p.quantity * p.unit_price) as stock_value,
               CASE WHEN p.quantity <= 0 THEN 'Out of Stock'
                    WHEN p.quantity <= p.reorder_level THEN 'Low Stock'
                    ELSE 'In Stock' END as stock_status,
               p.expiry_date
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.quantity ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def report_top_selling_products(limit=10):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, p.productcode, c.name as category,
               SUM(oi.quantity) as total_sold,
               SUM(oi.subtotal) as total_revenue
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        LEFT JOIN categories c ON p.category_id = c.id
        GROUP BY oi.product_id
        ORDER BY total_sold DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def report_customer_purchases():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.fullname, c.phone, c.email,
               COUNT(o.id) as total_orders,
               COALESCE(SUM(o.total_amount),0) as total_spent
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.id
        GROUP BY c.id
        ORDER BY total_spent DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def report_purchase_by_period(start_date, end_date):
    conn = get_connection()
    rows = conn.execute("""
        SELECT pu.purchase_number, pu.created_at, s.fullname as supplier,
               u.fullname as staff, pu.total_amount, pu.status
        FROM purchases pu
        LEFT JOIN suppliers s ON pu.supplier_id = s.id
        LEFT JOIN users u ON pu.user_id = u.id
        WHERE date(pu.created_at) BETWEEN ? AND ?
        ORDER BY pu.created_at DESC
    """, (start_date, end_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
