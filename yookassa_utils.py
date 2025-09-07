

import uuid
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from yookassa import Payment, Configuration
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

def create_payment(email: str, amount: str):
    payment = Payment.create({
        "amount": {"value": amount, "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://project13852829.tilda.ws/thanks"
        },
        "capture": True,
        "description": f"Курс по колке дров ({email})",
        "receipt": {
            "customer": {"email": email},
            "items": [{
                "description": "Курс по колке дров",
                "quantity": "1.00",
                "amount": {"value": amount, "currency": "RUB"},
                "vat_code": 1, # 1 = без НДС
                "payment_subject": "service",
                "payment_mode": "full_payment"
            }]
        }
    })
    return payment.confirmation.confirmation_url, payment.id
