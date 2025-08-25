
import sqlite3

def init_db():
    with sqlite3.connect("payments.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            payment_id TEXT,
            amount TEXT,
            status TEXT,
            timestamp TEXT
        )''')

def save_payment(email, payment_id=None, amount=None, status=None, timestamp=None):
    with sqlite3.connect("payments.db") as conn:
        conn.execute('''INSERT INTO payments (email, payment_id, amount, status, timestamp)
                        VALUES (?, ?, ?, ?, ?)''',
                     (email, payment_id, amount, status, timestamp))
