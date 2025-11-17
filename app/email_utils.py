# app/email_utils.py
import smtplib
import ssl
from email.message import EmailMessage

from app.config import settings


def send_verification_email(to_email: str, code: str):
    """
    Kayıt sonrası kullanıcıya doğrulama kodu gönderen basit SMTP fonksiyonu.
    HF Spaces içinde SMTP_HOST / SMTP_USERNAME / SMTP_PASSWORD
    environment variable olarak ayarlı olmalı.
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        # Config yoksa log gibi davran, prod öncesi uyarı
        print("[WARN] SMTP bilgileri tanımlı değil, mail gönderilemedi.")
        print(f"[INFO] Doğrulama kodu: {code} (to: {to_email})")
        return

    subject = "FlowMind - E-posta Doğrulama Kodunuz"
    body = (
        f"Merhaba,\n\n"
        f"FlowMind hesabınızı doğrulamak için aşağıdaki kodu kullanın:\n\n"
        f"    {code}\n\n"
        f"Bu kod {settings.EMAIL_VERIFICATION_EXPIRE_MINUTES} dakika boyunca geçerlidir.\n\n"
        f"FlowMind ekibi"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    msg["To"] = to_email
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)

    print(f"[OK] Verification email sent to {to_email}")
