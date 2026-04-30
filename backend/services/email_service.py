"""
Email service for AuraScore.

Priority chain:
  1. Resend HTTP API  — works on ALL hosts (no port block), free 3000/mo
  2. SendGrid HTTP API — HTTP, works if key is set
  3. Gmail SMTP       — local dev only (Render blocks SMTP ports)
  4. Console fallback — prints OTP to server logs in dev

To enable email in production set ONE of these on Render:
  RESEND_API_KEY   →  get free key at https://resend.com (recommended)
  SENDGRID_API_KEY →  get free key at https://sendgrid.com
"""

import os
import json
import threading
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY    = os.getenv("RESEND_API_KEY", "").strip()
SENDGRID_API_KEY  = os.getenv("SENDGRID_API_KEY", "").strip()
SENDGRID_SENDER   = os.getenv("SENDGRID_SENDER", "").strip()
GMAIL_USER        = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

FROM_NAME  = "AuraScore"
FROM_EMAIL = "onboarding@resend.dev"   # Works with Resend free tier; swap to your domain once verified


# ─────────────────────────────────────────────────────────────────────────────
def _build_otp_html(name: str, otp: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#080810;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#080810;padding:40px 20px;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;
             background:#0f0f1a;border-radius:20px;overflow:hidden;
             border:1px solid rgba(240,192,64,0.25);">
        <tr>
          <td style="background:linear-gradient(135deg,#9b5de5,#f0c040);padding:28px;text-align:center;">
            <div style="font-size:32px;font-weight:900;color:#111;">AuraScore</div>
            <div style="font-size:13px;color:#333;margin-top:4px;">AI Personal Glow-Up Coach</div>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 32px;">
            <p style="color:#9ca3af;margin:0 0 6px;">Hi {name},</p>
            <h2 style="color:#f0c040;margin:0 0 20px;font-weight:800;">Verify your email</h2>
            <p style="color:#6b7280;line-height:1.7;margin:0 0 28px;">
              Your verification code expires in <strong style="color:#f0c040;">15 minutes</strong>.
            </p>
            <div style="background:rgba(240,192,64,0.08);border:2px solid rgba(240,192,64,0.35);
                        border-radius:14px;padding:28px;text-align:center;margin-bottom:28px;">
              <div style="font-size:48px;font-weight:900;letter-spacing:14px;
                          color:#f0c040;font-family:monospace;">{otp}</div>
            </div>
            <p style="color:#4b5563;font-size:12px;">If you didn't sign up, ignore this email.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
def _http_post(url: str, headers: dict, payload: dict, label: str) -> bool:
    """Generic JSON HTTP POST helper using only stdlib."""
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            print(f"[EMAIL OK] {label} → {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace") if e.fp else ""
        print(f"[EMAIL FAIL] {label} HTTP {e.code}: {body[:300]}")
        return False
    except Exception as e:
        print(f"[EMAIL FAIL] {label}: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_resend(to_email: str, name: str, otp: str) -> bool:
    """
    Resend HTTP API — pure HTTPS, not affected by SMTP port blocks.
    Free tier: 3000 emails/month.  Get key at https://resend.com
    """
    if not RESEND_API_KEY:
        return False

    return _http_post(
        url="https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        payload={
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Your AuraScore Verification Code",
            "html": _build_otp_html(name, otp),
        },
        label=f"Resend → {to_email}",
    )


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_sendgrid(to_email: str, name: str, otp: str) -> bool:
    """SendGrid HTTP API fallback."""
    if not SENDGRID_API_KEY:
        return False

    sender = SENDGRID_SENDER or GMAIL_USER or "noreply@aurascore.com"
    return _http_post(
        url="https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {SENDGRID_API_KEY}"},
        payload={
            "personalizations": [{"to": [{"email": to_email}],
                                   "subject": "Your AuraScore Verification Code"}],
            "from": {"email": sender, "name": FROM_NAME},
            "content": [{"type": "text/html", "value": _build_otp_html(name, otp)}],
        },
        label=f"SendGrid → {to_email}",
    )


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_smtp(to_email: str, name: str, otp: str) -> bool:
    """
    Gmail SMTP — LOCAL DEV ONLY.
    Render free tier blocks ports 465 & 587 — this will always fail there.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False

    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AuraScore Verification Code"
    msg["From"]    = f"{FROM_NAME} <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(_build_otp_html(name, otp), "html", "utf-8"))

    def _make_ctx():
        try:
            import certifi
            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            pass
        try:
            return ssl.create_default_context()
        except Exception:
            return ssl._create_unverified_context()

    ctx = _make_ctx()
    for method, port in (("SSL", 465), ("STARTTLS", 587)):
        try:
            if method == "SSL":
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=ctx, timeout=10) as s:
                    s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    s.sendmail(GMAIL_USER, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=10) as s:
                    s.ehlo(); s.starttls(context=ctx); s.ehlo()
                    s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    s.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"[EMAIL OK] SMTP {method} → {to_email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH FAIL] {e}")
            return False   # Wrong credentials — no point retrying
        except Exception as e:
            print(f"[EMAIL] SMTP {method} failed: {type(e).__name__}: {e}")

    return False


# ─────────────────────────────────────────────────────────────────────────────
def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Dispatch OTP email in a background thread (non-blocking).
    Returns True immediately; actual delivery is async.
    """
    def _worker():
        print(f"[EMAIL] Sending OTP to {to_email}...")

        # 1. Resend (HTTP — works on Render free tier)
        if _send_via_resend(to_email, name, otp):
            return

        # 2. SendGrid (HTTP — works on Render free tier)
        if _send_via_sendgrid(to_email, name, otp):
            return

        # 3. Gmail SMTP (local dev only)
        if _send_via_smtp(to_email, name, otp):
            return

        # 4. Console fallback — always print so OTP is never lost
        print(f"\n{'='*55}")
        print(f"[OTP FALLBACK]  to={to_email}  code={otp}")
        print(f"  → No email provider configured or all failed.")
        print(f"  → Set RESEND_API_KEY on Render to enable emails.")
        print(f"{'='*55}\n")

    threading.Thread(target=_worker, daemon=True).start()
    return True
