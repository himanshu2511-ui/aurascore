"""
Email service for AuraScore.

Priority chain:
  1. Brevo (formerly Sendinblue) HTTP API — free, no domain needed, 300/day
  2. Resend HTTP API                       — free 3000/mo (needs domain for arbitrary recipients)
  3. SendGrid HTTP API                     — free 100/day
  4. Gmail SMTP                            — local dev only (Render blocks SMTP ports)
  5. Console fallback                      — prints OTP to server logs

Set ONE of these on Render env vars:
  BREVO_API_KEY    → get free key at https://app.brevo.com  (recommended, no domain needed)
  RESEND_API_KEY   → get free key at https://resend.com
  SENDGRID_API_KEY → get free key at https://sendgrid.com
"""

import os
import json
import threading
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY     = os.getenv("BREVO_API_KEY", "").strip()
BREVO_SENDER      = os.getenv("BREVO_SENDER", os.getenv("GMAIL_USER", "")).strip()
RESEND_API_KEY    = os.getenv("RESEND_API_KEY", "").strip()
SENDGRID_API_KEY  = os.getenv("SENDGRID_API_KEY", "").strip()
SENDGRID_SENDER   = os.getenv("SENDGRID_SENDER", "").strip()
GMAIL_USER        = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

FROM_NAME = "AuraScore"


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
    try:
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            url, data=data,
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[EMAIL OK] {label} status={resp.status}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace") if e.fp else ""
        print(f"[EMAIL FAIL] {label} HTTP {e.code}: {body[:400]}")
        return False
    except Exception as e:
        print(f"[EMAIL FAIL] {label}: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_brevo(to_email: str, name: str, otp: str) -> bool:
    """
    Brevo (Sendinblue) HTTP API.
    FREE: 300 emails/day, NO domain verification needed.
    Just verify sender email in Brevo dashboard once.
    Sign up: https://app.brevo.com → API Keys → Create key.
    """
    if not BREVO_API_KEY:
        return False

    sender_email = BREVO_SENDER or GMAIL_USER or "noreply@aurascore.app"
    return _http_post(
        url="https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_API_KEY},
        payload={
            "sender": {"name": FROM_NAME, "email": sender_email},
            "to": [{"email": to_email, "name": name}],
            "subject": "Your AuraScore Verification Code",
            "htmlContent": _build_otp_html(name, otp),
        },
        label=f"Brevo→{to_email}",
    )


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_resend(to_email: str, name: str, otp: str) -> bool:
    """
    Resend HTTP API. FREE 3000/month.
    NOTE: Without a verified domain, only sends to your own Resend account email.
    Add domain at https://resend.com/domains for full functionality.
    """
    if not RESEND_API_KEY:
        return False

    return _http_post(
        url="https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        payload={
            "from": f"{FROM_NAME} <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "Your AuraScore Verification Code",
            "html": _build_otp_html(name, otp),
        },
        label=f"Resend→{to_email}",
    )


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_sendgrid(to_email: str, name: str, otp: str) -> bool:
    if not SENDGRID_API_KEY:
        return False
    sender = SENDGRID_SENDER or GMAIL_USER or "noreply@aurascore.app"
    return _http_post(
        url="https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {SENDGRID_API_KEY}"},
        payload={
            "personalizations": [{"to": [{"email": to_email}],
                                   "subject": "Your AuraScore Verification Code"}],
            "from": {"email": sender, "name": FROM_NAME},
            "content": [{"type": "text/html", "value": _build_otp_html(name, otp)}],
        },
        label=f"SendGrid→{to_email}",
    )


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_smtp(to_email: str, name: str, otp: str) -> bool:
    """Gmail SMTP — LOCAL DEV ONLY. Render free tier blocks all SMTP ports."""
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
    def _ctx():
        try:
            import certifi; return ssl.create_default_context(cafile=certifi.where())
        except Exception: pass
        try: return ssl.create_default_context()
        except Exception: return ssl._create_unverified_context()
    ctx = _ctx()
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
            print(f"[EMAIL OK] SMTP {method}→{to_email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH FAIL] {e}"); return False
        except Exception as e:
            print(f"[EMAIL] SMTP {method} failed: {type(e).__name__}: {e}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Try all email providers synchronously.
    Returns True if any provider succeeded, False if all failed.
    Caller should surface OTP to the user when this returns False.
    """
    print(f"[EMAIL] Attempting delivery to {to_email}...")

    if _send_via_brevo(to_email, name, otp):
        return True
    if _send_via_resend(to_email, name, otp):
        return True
    if _send_via_sendgrid(to_email, name, otp):
        return True
    if _send_via_smtp(to_email, name, otp):
        return True

    # All providers failed — log OTP so it's never lost
    print(f"\n{'='*55}")
    print(f"[OTP FALLBACK] email={to_email}  otp={otp}")
    print(f"  All email providers failed or unconfigured.")
    print(f"  Set BREVO_API_KEY on Render to enable emails.")
    print(f"{'='*55}\n")
    return False
