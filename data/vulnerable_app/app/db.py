"""Data access helpers."""
import sqlite3


def get_conn():
    return sqlite3.connect("shop.db")


def get_user(conn, username):
    cur = conn.cursor()
    cur.execute(f"SELECT id, email FROM users WHERE username = '{username}'")
    return cur.fetchone()


def get_user_safe(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE username = ?", (username,))
    return cur.fetchone()


def search_products(conn, term):
    query = "SELECT * FROM products WHERE name LIKE '%" + term + "%'"
    return conn.execute(query).fetchall()


def count_orders(conn, customer_id):
    return conn.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,)).fetchone()[0]
