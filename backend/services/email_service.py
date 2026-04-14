import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

def _build_otp_html(name: str, otp: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AuraScore OTP</title></head>
<body style="margin:0;padding:0;background:#080810;font-family:Inter,Segoe UI,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#080810;padding:40px 20px;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;
             background:#0f0f1a;border-radius:20px;overflow:hidden;
             border:1px solid rgba(240,192,64,0.25);box-shadow:0 20px 60px rgba(0,0,0,0.6);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#9b5de5,#f0c040);padding:28px;text-align:center;">
            <div style="font-size:32px;font-weight:900;color:#111;letter-spacing:-1px;">&#10022; AuraScore</div>
            <div style="font-size:13px;color:#333;margin-top:4px;">AI Personal Glow-Up Coach</div>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:36px 32px;">
            <p style="color:#9ca3af;margin:0 0 6px;font-size:15px;">Hi {name},</p>
            <h2 style="color:#f0c040;margin:0 0 20px;font-size:22px;font-weight:800;">Verify your email address</h2>
            <p style="color:#6b7280;line-height:1.7;margin:0 0 28px;font-size:14px;">
              Use the verification code below to complete your AuraScore signup.
              It expires in <strong style="color:#f0c040;">15 minutes</strong>.
            </p>
            <!-- OTP Box -->
            <div style="background:rgba(240,192,64,0.08);border:2px solid rgba(240,192,64,0.35);
                        border-radius:14px;padding:28px;text-align:center;margin-bottom:28px;">
              <div style="font-size:48px;font-weight:900;letter-spacing:14px;
                          color:#f0c040;font-family:monospace;">{otp}</div>
              <div style="font-size:12px;color:#4b5563;margin-top:8px;">One-Time Password — do not share</div>
            </div>
            <p style="color:#4b5563;font-size:12px;line-height:1.6;margin:0;">
              If you didn't create an AuraScore account, you can safely ignore this email.
              No action is required.
            </p>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="padding:18px 32px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
            <p style="color:#374151;font-size:11px;margin:0;">
              AuraScore AI &mdash; Transform. Improve. Glow Up.<br>
              <span style="color:#1f2937;">This is an automated message. Please do not reply.</span>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Sends OTP verification email via Gmail SMTP.
    Falls back to terminal print in dev mode (no credentials configured).
    Returns True on success, False on failure.
    """
    # ── Dev mode: no SMTP configured ──
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("\n" + "=" * 54)
        print(f"[DEV MODE] OTP for {to_email}")
        print(f"  Code : {otp}  (expires in 15 min)")
        print("=" * 54 + "\n")
        return True

    html_body = _build_otp_html(name, otp)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AuraScore Verification Code"
    msg["From"]    = f"AuraScore <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Try SMTP_SSL (port 465) first, fall back to STARTTLS (port 587)
    for attempt, method in enumerate(("SSL", "STARTTLS"), 1):
        try:
            if method == "SSL":
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as srv:
                    srv.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    srv.sendmail(GMAIL_USER, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as srv:
                    srv.ehlo()
                    srv.starttls(context=ssl.create_default_context())
                    srv.ehlo()
                    srv.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                    srv.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"[EMAIL] OTP sent to {to_email} via {method}.")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH ERROR] Gmail rejected credentials. "
                  f"Ensure you're using an App Password (not your main password). "
                  f"Error: {e}")
            return False  # No point retrying with STARTTLS if creds are wrong

        except Exception as e:
            print(f"[EMAIL] Attempt {attempt} ({method}) failed: {e}")
            if attempt == 2:
                print(f"[EMAIL ERROR] All attempts failed for {to_email}.")
                return False
            print("[EMAIL] Retrying with STARTTLS...")

    return False
