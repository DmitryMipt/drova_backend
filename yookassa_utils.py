

import uuid
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from yookassa import Payment, Configuration
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

PRICE = "786.50"  # строкой, 2 знака после запятой

def create_payment(email: str):
    payment = Payment.create({
        "amount": {"value": PRICE, "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://project13852829.tilda.ws/thanks"  # твоя страница "спасибо"
        },
        "capture": True,
        "description": f"Курс по колке дров ({email})",
        # ⬇⬇⬇ ОБЯЗАТЕЛЬНАЯ ЧАСТЬ — ЧЕК
        "receipt": {
            "customer": {"email": email},
            # если у тебя УСН/самозанятый — налог обычно "без НДС"
            "items": [{
                "description": "Курс по колке дров",
                "quantity": "1.00",                       # строкой!
                "amount": {"value": PRICE, "currency": "RUB"},
                "vat_code": 1,                            # 1 = без НДС
                "payment_subject": "service",             # услуга
                "payment_mode": "full_payment"            # полная оплата
            }],
            # если в договоре указан НПД/УСН — tax_system_code можно не передавать;
            # если ЮKassa требует — раскомментируй и поставь нужный код (1..6)
            # "tax_system_code": 6
        }
    })
    return payment.confirmation.confirmation_url, payment.id
