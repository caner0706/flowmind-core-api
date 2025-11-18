import requests
from app.config import settings

RESEND_API_URL = "https://api.resend.com/emails"

def send_verification_email(to_email: str, code: str) -> None:
    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is not set")

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "FlowMind Studio - Email Doğrulama Kodunuz",
        "text": f"Doğrulama kodunuz: {code}",
    }

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
