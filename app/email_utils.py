# app/email_utils.py
import smtplib
from email.mime.text import MIMEText
from app.config import settings

def send_verification_email(to_email: str, code: str):
    # Eğer SMTP env'leri yoksa hiç deneme, sadece logla
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("[WARN] SMTP not configured; skipping verification email.")
        return

    msg = MIMEText(f"FlowMind doğrulama kodun: {code}")
    msg["Subject"] = "FlowMind - E-posta Doğrulama"
    msg["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
