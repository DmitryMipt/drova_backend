

import uuid
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from yookassa import Payment, Configuration
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

def create_payment(email):
    payment = Payment.create({
        "amount": {
            "value": "990.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://your-site.com/thankyou"
        },
        "capture": True,
        "metadata": {
            "email": email
        },
        "description": "Курс по колке дров"
    }, uuid.uuid4())

    return payment.confirmation.confirmation_url, payment.id
