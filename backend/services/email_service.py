import os
import smtplib
import ssl
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

# ── Aggressive timeout: 8 seconds max per SMTP attempt ──
_SMTP_TIMEOUT = 8


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
            <p style="color:#9ca3af;margin:0 0 6px;font-size:15px;">Hi {name},</p>
            <h2 style="color:#f0c040;margin:0 0 20px;font-size:22px;font-weight:800;">Verify your email</h2>
            <p style="color:#6b7280;line-height:1.7;margin:0 0 28px;font-size:14px;">
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


def _smtp_send(to_email: str, msg: MIMEMultipart) -> bool:
    """Attempt to send email via Gmail SMTP with short timeouts. Returns True on success."""
    # Try SSL (port 465), then STARTTLS (port 587)
    for attempt, method in enumerate(("SSL", "STARTTLS"), 1):
        try:
            if method == "SSL":
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=_SMTP_TIMEOUT) as srv:
                    srv.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    srv.sendmail(GMAIL_USER, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=_SMTP_TIMEOUT) as srv:
                    srv.ehlo()
                    srv.starttls(context=ssl.create_default_context())
                    srv.ehlo()
                    srv.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    srv.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"[EMAIL OK] Sent to {to_email} via {method}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH FAIL] {e}")
            return False  # Wrong creds — don't retry
        except Exception as e:
            print(f"[EMAIL] {method} failed: {e}")
    print(f"[EMAIL FAIL] All attempts failed for {to_email}")
    return False


def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Sends OTP email in a BACKGROUND THREAD so it never blocks the API response.
    Always returns True immediately — the email sends asynchronously.
    """
    # Dev mode: no credentials configured
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print(f"\n{'='*50}\n[DEV] OTP for {to_email}: {otp}\n{'='*50}\n")
        return True

    # Build the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AuraScore Verification Code"
    msg["From"]    = f"AuraScore <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(_build_otp_html(name, otp), "html", "utf-8"))

    # Fire-and-forget: send in a background thread
    def _worker():
        try:
            _smtp_send(to_email, msg)
        except Exception as e:
            print(f"[EMAIL THREAD ERROR] {e}")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

    # Return immediately — never block the API
    return True
