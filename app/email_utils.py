import requests
from app.config import settings

def send_verification_email(to_email: str, code: str):
    if not settings.RESEND_API_KEY:
        print("[WARN] RESEND_API_KEY not set — email skipped")
        return

    url = "https://api.resend.com/emails"

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Your Verification Code",
        "html": f"<p>Your code is: <b>{code}</b></p>",
    }

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()  # hata varsa fırlatır
    print(f"[EMAIL] Resend sent → {to_email}")
