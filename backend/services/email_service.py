import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Sends OTP verification email. Falls back to terminal print in dev mode.
    Returns True on success, False on failure.
    """
    html_body = f"""
    <div style="font-family:Inter,sans-serif;background:#080810;color:#f0f0f5;
                max-width:520px;margin:0 auto;border-radius:16px;overflow:hidden;
                border:1px solid rgba(240,192,64,0.3)">
      <div style="background:linear-gradient(135deg,#9b5de5,#f0c040);padding:24px;text-align:center">
        <h1 style="margin:0;font-size:28px;color:#111">✦ AuraScore</h1>
        <p style="margin:4px 0 0;color:#333;font-size:13px">AI Personal Glow-Up Coach</p>
      </div>
      <div style="padding:32px 28px">
        <p style="color:#a1a1aa;margin-bottom:8px">Hi {name},</p>
        <h2 style="color:#f0c040;margin:0 0 24px">Verify your email</h2>
        <p style="color:#a1a1aa;line-height:1.6">
          Use the code below to verify your AuraScore account. It expires in <strong>15 minutes</strong>.
        </p>
        <div style="background:rgba(240,192,64,0.12);border:1px solid rgba(240,192,64,0.4);
                    border-radius:12px;padding:24px;text-align:center;margin:24px 0">
          <span style="font-size:42px;font-weight:900;letter-spacing:12px;color:#f0c040">{otp}</span>
        </div>
        <p style="color:#6b7280;font-size:12px;margin-top:24px">
          If you didn't sign up for AuraScore, you can safely ignore this email.
        </p>
      </div>
      <div style="padding:16px;text-align:center;border-top:1px solid rgba(255,255,255,0.06)">
        <p style="color:#4b4b60;font-size:11px;margin:0">AuraScore AI — Transform. Improve. Glow Up.</p>
      </div>
    </div>
    """

    # ── Dev mode: no SMTP configured ──
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("\n" + "="*50)
        print(f"[DEV MODE] Email verification OTP for {to_email}")
        print(f"  OTP: {otp}")
        print("="*50 + "\n")
        return True

    # ── Production: send via Gmail SMTP ──
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✦ Your AuraScore Verification Code"
        msg["From"]    = f"AuraScore <{GMAIL_USER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        return False
