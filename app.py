
from flask import Flask, request, redirect, jsonify
from yookassa_utils import create_payment
from mailer import send_email
from db import init_db, save_payment
from yookassa import Payment
import datetime
import os

app = Flask(__name__)
init_db()

ACCESS_URL = "https://project13852829.tilda.ws"

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
            save_payment(email=email, amount=amount, status='paid',
                         timestamp=datetime.datetime.utcnow())

        except Exception as e:
            import traceback; traceback.print_exc()
            # всё равно вернуть 200, чтобы ЮKassa не ретраила бесконечно
            return '', 200

    return '', 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
