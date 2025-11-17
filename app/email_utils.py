# app/email_utils.py
import os
import smtplib
import ssl
from email.message import EmailMessage


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Gmail adresin
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # App Password
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Basit SMTP mail gönderici.
    HF Spaces'te env olarak:
      - SMTP_USERNAME
      - SMTP_PASSWORD
      - SMTP_FROM_EMAIL
    tanımlı olmalı.
    """
    if not (SMTP_USERNAME and SMTP_PASSWORD and SMTP_FROM_EMAIL):
        # Log için raise edebiliriz; şimdilik sessiz geçmek yerine hata atalım
        raise RuntimeError("SMTP credentials are not configured in environment.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


def send_verification_email(to_email: str, code: str) -> None:
    """
    Kullanıcı kayıt olduğunda doğrulama kodu göndermek için helper.
    """
    subject = "FlowMind Studio - E-posta Doğrulama Kodu"
    body = (
        "Merhaba,\n\n"
        f"FlowMind Studio hesabını doğrulamak için aşağıdaki kodu kullan:\n\n"
        f"    {code}\n\n"
        "Bu kod 15 dakika boyunca geçerlidir.\n\n"
        "Eğer bu isteği sen göndermediysen bu maili yok sayabilirsin.\n\n"
        "Sevgiler,\n"
        "FlowMind Studio"
    )
    send_email(to_email, subject, body)
