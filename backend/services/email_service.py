import os
import json
import threading
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

# ── SendGrid HTTP API (Bypasses Render SMTP Block) ──
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
# Use the verified sender email from SendGrid. If none set, fallback to Gmail user env.
SENDGRID_SENDER = os.getenv("SENDGRID_SENDER", os.getenv("GMAIL_USER", "onboarding@aurascore.com")).strip()

# ── Local Dev Fallback (Only works off-Render) ──
GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()


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


def _send_via_sendgrid(to_email: str, name: str, otp: str) -> bool:
    """Send email using SendGrid's HTTP API to bypass Render's port blocking."""
    html = _build_otp_html(name, otp)
    
    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": "Your AuraScore Verification Code"
            }
        ],
        "from": {
            "email": SENDGRID_SENDER,
            "name": "AuraScore"
        },
        "content": [
            {
                "type": "text/html",
                "value": html
            }
        ]
    }

    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            # SendGrid returns 202 Accepted on success with no body
            print(f"[EMAIL OK] SendGrid API sent to {to_email}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"[EMAIL FAIL] SendGrid HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"[EMAIL FAIL] SendGrid error: {e}")
        return False


def _send_via_smtp(to_email: str, name: str, otp: str) -> bool:
    """Fallback: send via Gmail SMTP. Will hang or timeout on Render free tier."""
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    html = _build_otp_html(name, otp)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AuraScore Verification Code"
    msg["From"]    = f"AuraScore <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    for method in ("SSL", "STARTTLS"):
        try:
            if method == "SSL":
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=8) as s:
                    s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    s.sendmail(GMAIL_USER, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=8) as s:
                    s.ehlo(); s.starttls(context=ssl.create_default_context()); s.ehlo()
                    s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    s.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"[EMAIL OK] SMTP sent to {to_email} via {method}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH FAIL] {e}")
            return False
        except Exception as e:
            print(f"[EMAIL] SMTP {method} failed: {e}")
    return False


def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Sends email in a background thread and returns immediately.
    Prioritizes SendGrid API, falls back to SMTP for local development.
    """
    # Dev mode: absolutely nothing configured
    if not SENDGRID_API_KEY and not GMAIL_USER:
        print(f"\n{'='*50}\n[DEV] OTP for {to_email}: {otp}\n{'='*50}\n")
        return True

    def _worker():
        try:
            # 1. Try SendGrid HTTP API (Guaranteed to work on Render)
            if SENDGRID_API_KEY:
                if _send_via_sendgrid(to_email, name, otp):
                    return
                print("[EMAIL] SendGrid failed, trying SMTP fallback...")

            # 2. Try Gmail SMTP (Will work locally, but fail on Render due to port block)
            if GMAIL_USER and GMAIL_APP_PASSWORD:
                if _send_via_smtp(to_email, name, otp):
                    return

            print(f"[EMAIL FAIL] Could not deliver OTP to {to_email}")
            print(f"[DEV FALLBACK] OTP code: {otp}")
        except Exception as e:
            print(f"[EMAIL THREAD ERROR] {e}")
            print(f"[DEV FALLBACK] OTP code: {otp}")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    
    return True
