
import smtplib
from email.mime.text import MIMEText
from config import GMAIL_USER, GMAIL_PASSWORD

def send_email(to_email, link):
    msg = MIMEText(f"Привет! Вот твоя ссылка на курс: {link}")
    msg["Subject"] = "Доступ к курсу по колке дров"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
