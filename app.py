
from flask import Flask, request, redirect, jsonify, send_file
from yookassa_utils import create_payment
from mailer import send_email
from db import init_db, save_payment
from yookassa import Payment
import datetime
import os
import logging
from db import init_db, _get_conn

init_db()

app = Flask(__name__)
init_db()

ACCESS_URL = "https://drive.google.com/drive/folders/14_WZemprvf6gO7WLK-Ae_TCnK39gbFQN?usp=sharing"

@app.route("/admin/download-db")
def download_db():
    try:
        return send_file("payments.db", as_attachment=True)
    except Exception as e:
        return str(e), 500

@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'  # можешь указать точный домен Tilda: 'https://project13852829.tilda.ws'
    resp.headers['Vary'] = 'Origin'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return resp

# --- /pay: разрешаем preflight ---
@app.route('/pay', methods=['POST', 'OPTIONS'])
def pay():
    if request.method == 'OPTIONS':
        # preflight ок, тело не требуется
        return ('', 204)

    # дальше твоя логика:
    # if request.form.get("test") == "test": return "Tilda test OK", 200
    email = request.form.get("email")
    amount = request.form.get("amount")
    if not email:
        return jsonify({"error": "Email обязателен"}), 400

    payment_url, payment_id = create_payment(email,amount)
    save_payment(email=email, payment_id=payment_id, status="created")
    return jsonify({"redirect_url": payment_url}), 200

@app.route('/webhook', methods=['POST'])
@app.route('/webhook/', methods=['POST'])
@app.route('/yookassa/webhook', methods=['POST'])
@app.route('/yookassa/webhook/', methods=['POST'])
def yk_webhook():
    data = request.get_json(force=True, silent=True) or {}
    event = data.get('event')
    obj = data.get('object') or {}

    if event == 'payment.succeeded':
        try:
            payment_id = obj.get('id')

            # на всякий случай перепроверим статус у ЮKassa
            p = Payment.find_one(payment_id)
            if p.status != 'succeeded':
                return '', 200

            # e-mail: сначала из metadata/receipt объекта вебхука,
            # либо из p.metadata/p.receipt при необходимости
            email = (
                (obj.get('metadata') or {}).get('email') or
                ((obj.get('receipt') or {}).get('customer') or {}).get('email')
            )
            amount = (obj.get('amount') or {}).get('value')

            # твои функции
            logging.info(f"Вебхук: email={email}")
            send_email(email, ACCESS_URL)
            mark_paid(payment_id)
            

        except Exception as e:
            import traceback; traceback.print_exc()
            # всё равно вернуть 200, чтобы ЮKassa не ретраила бесконечно
            return '', 200

    return '', 200
    
@app.route("/statiti", methods=["GET"])
def stats():    
    if request.args.get("key") != "123":
        return "no", 403
    conn = _get_conn()
    cur = conn.cursor()

    # всего
    cur.execute("SELECT COUNT(*) FROM payments")
    total = cur.fetchone()[0]

    # оплачено
    cur.execute("SELECT COUNT(*) FROM payments WHERE status='paid'")
    paid = cur.fetchone()[0]

    # не оплатили
    cur.execute("SELECT COUNT(*) FROM payments WHERE status='created'")
    not_paid = cur.fetchone()[0]

    # сумма
    cur.execute("""
        SELECT COALESCE(SUM(
            CASE 
                WHEN amount ~ '^[0-9.]+$' THEN amount::numeric 
                ELSE 0 
            END
        ), 0)
        FROM payments WHERE status='paid'
    """)
    total_sum_rub = cur.fetchone()[0]

    print(total, paid, not_paid, total_sum_rub)
    cur.close()
    conn.close()

    return jsonify({
        "opened_payment": total,
        "paid": paid,
        "not_paid": not_paid,
        "conversion": round(paid / total * 100, 2) if total else 0,
        "total_sum_rub": float(total_sum_rub)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
