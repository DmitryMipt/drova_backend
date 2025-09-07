import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")

def _get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                email TEXT,
                payment_id TEXT UNIQUE,
                amount TEXT,
                status TEXT,
                timestamp TIMESTAMP
            )
        ''')
        conn.commit()

def save_payment(email, payment_id=None, amount=None, status=None, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow()

    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute('''
            INSERT INTO payments (email, payment_id, amount, status, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (payment_id) DO NOTHING
        ''', (email, payment_id, amount, status, timestamp))
        conn.commit()

def get_all_payments():
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM payments ORDER BY timestamp DESC")
        return cur.fetchall()

def get_by_payment_id(payment_id):
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM payments WHERE payment_id=%s", (payment_id,))
        return cur.fetchone()

def mark_paid(payment_id):
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE payments SET status='paid', timestamp=%s WHERE payment_id=%s",
            (datetime.utcnow(), payment_id)
        )
        conn.commit()
