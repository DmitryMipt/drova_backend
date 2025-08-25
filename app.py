
from flask import Flask, request, redirect
from yookassa_utils import create_payment
from mailer import send_email
from db import init_db, save_payment
import datetime

app = Flask(__name__)
init_db()

ACCESS_URL = "https://your-course-link.com"

@app.route('/pay', methods=['POST'])
def pay():
    email = request.form.get("email")
    if not email:
        return "Email обязателен", 400

    payment_url, payment_id = create_payment(email)
    save_payment(email=email, payment_id=payment_id, status="created", timestamp=datetime.datetime.utcnow())
    return redirect(payment_url)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("event") == "payment.succeeded":
        payment = data.get("object", {})
        metadata = payment.get("metadata", {})
        email = metadata.get("email")
        amount = payment.get("amount", {}).get("value")

        send_email(email, ACCESS_URL)
        save_payment(email=email, amount=amount, status="paid", timestamp=datetime.datetime.utcnow())

    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
