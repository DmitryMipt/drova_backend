
import smtplib
from email.mime.text import MIMEText
from config import GMAIL_USER, GMAIL_PASSWORD

def send_email(to_email: str, link: str):
    if not to_email or '@' not in to_email:
        raise ValueError(f"Некорректный email получателя: {to_email!r}")

    msg = MIMEText(f"Привет!\n\nВот твоя ссылка на курс: {link}\n\nУдачи!")
    msg["Subject"] = "Доступ к курсу по колке дров"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, [to_email], msg.as_string())
            print(f"[OK] Письмо отправлено на {to_email}")
    except smtplib.SMTPRecipientsRefused:
        print(f"[ERR] Gmail отказался принимать email: {to_email}")
        raise
    except Exception as e:
        print(f"[ERR] Ошибка при отправке письма: {e}")
        raise
