"""
AuraScore Email Service
=======================
HTTP-only providers (no SMTP ports — works on Render free tier).

RECOMMENDED → Mailersend (zero setup, pre-verified trial domain, any recipient):
  1. Sign up at https://app.mailersend.com (use GitHub login)
  2. API Tokens → Generate token → copy it
  3. Domains → note your trial domain like "trial-xxx.mlsnd.com"
  4. Set on Render:
       MAILERSEND_API_KEY  = mlsn_xxxxxxxx
       MAILERSEND_DOMAIN   = trial-xxx.mlsnd.com

FALLBACK → Brevo (needs sender verified in Brevo dashboard once):
  Set BREVO_API_KEY + BREVO_SENDER

FALLBACK → Resend (needs verified domain for arbitrary recipients):
  Set RESEND_API_KEY
"""

import os
import requests as _req
from dotenv import load_dotenv

load_dotenv()

# ── Credentials ──────────────────────────────────────────────────────────────
MAILERSEND_API_KEY = os.getenv("MAILERSEND_API_KEY", "").strip()
MAILERSEND_DOMAIN  = os.getenv("MAILERSEND_DOMAIN", "").strip()   # e.g. trial-xxx.mlsnd.com

BREVO_API_KEY      = os.getenv("BREVO_API_KEY", "").strip()
BREVO_SENDER       = os.getenv("BREVO_SENDER", "").strip()

RESEND_API_KEY     = os.getenv("RESEND_API_KEY", "").strip()

SENDGRID_API_KEY   = os.getenv("SENDGRID_API_KEY", "").strip()
SENDGRID_SENDER    = os.getenv("SENDGRID_SENDER", "").strip()

GMAIL_USER         = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

FROM_NAME = "AuraScore"


# ─────────────────────────────────────────────────────────────────────────────
def _otp_html(name: str, otp: str) -> str:
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
      <p style="color:#4b5563;font-size:12px;">If you didn't sign up for AuraScore, ignore this.</p>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
def _post(label, url, headers, payload):
    """HTTP POST with full error logging."""
    try:
        r = _req.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code in (200, 201, 202):
            print(f"[EMAIL OK] {label} status={r.status_code}")
            return True
        print(f"[EMAIL FAIL] {label} HTTP {r.status_code}: {r.text[:600]}")
        return False
    except Exception as e:
        print(f"[EMAIL FAIL] {label} exception: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
def _via_mailersend(to_email, name, otp):
    """
    Mailersend — RECOMMENDED for Render free tier.
    Pre-verified trial domain, sends to ANY email, zero domain setup needed.
    """
    if not MAILERSEND_API_KEY or not MAILERSEND_DOMAIN:
        print("[EMAIL] Mailersend: MAILERSEND_API_KEY or MAILERSEND_DOMAIN not set.")
        return False
    from_email = f"noreply@{MAILERSEND_DOMAIN}"
    return _post(
        f"Mailersend→{to_email}",
        "https://api.mailersend.com/v1/email",
        {"Authorization": f"Bearer {MAILERSEND_API_KEY}", "Content-Type": "application/json"},
        {
            "from":    {"email": from_email, "name": FROM_NAME},
            "to":      [{"email": to_email,  "name": name}],
            "subject": "Your AuraScore Verification Code",
            "html":    _otp_html(name, otp),
        },
    )


def _via_brevo(to_email, name, otp):
    """Brevo HTTP API — needs sender verified once in Brevo dashboard."""
    if not BREVO_API_KEY:
        print("[EMAIL] Brevo: BREVO_API_KEY not set.")
        return False
    sender = BREVO_SENDER or GMAIL_USER
    if not sender:
        print("[EMAIL] Brevo: BREVO_SENDER not set.")
        return False
    return _post(
        f"Brevo→{to_email}",
        "https://api.brevo.com/v3/smtp/email",
        {"api-key": BREVO_API_KEY, "accept": "application/json", "content-type": "application/json"},
        {
            "sender":      {"name": FROM_NAME, "email": sender},
            "to":          [{"email": to_email, "name": name}],
            "subject":     "Your AuraScore Verification Code",
            "htmlContent": _otp_html(name, otp),
        },
    )


def _via_resend(to_email, name, otp):
    """Resend — needs verified domain to send to arbitrary recipients."""
    if not RESEND_API_KEY:
        print("[EMAIL] Resend: RESEND_API_KEY not set.")
        return False
    return _post(
        f"Resend→{to_email}",
        "https://api.resend.com/emails",
        {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        {
            "from":    f"{FROM_NAME} <onboarding@resend.dev>",
            "to":      [to_email],
            "subject": "Your AuraScore Verification Code",
            "html":    _otp_html(name, otp),
        },
    )


def _via_sendgrid(to_email, name, otp):
    if not SENDGRID_API_KEY:
        return False
    sender = SENDGRID_SENDER or GMAIL_USER
    if not sender:
        return False
    return _post(
        f"SendGrid→{to_email}",
        "https://api.sendgrid.com/v3/mail/send",
        {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"},
        {
            "personalizations": [{"to": [{"email": to_email}],
                                   "subject": "Your AuraScore Verification Code"}],
            "from":    {"email": sender, "name": FROM_NAME},
            "content": [{"type": "text/html", "value": _otp_html(name, otp)}],
        },
    )


def _via_smtp(to_email, name, otp):
    """Gmail SMTP — local dev only. Render free tier blocks ports 465 & 587."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AuraScore Verification Code"
    msg["From"]    = f"{FROM_NAME} <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(_otp_html(name, otp), "html", "utf-8"))
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
            print(f"[EMAIL] SMTP {method}/{port} failed: {type(e).__name__}: {e}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Try all providers. Returns True if any succeeded.
    Caller includes fallback_otp in response when this returns False.
    """
    print(f"[EMAIL] Sending to {to_email} | "
          f"Mailersend={'✓' if MAILERSEND_API_KEY else '✗'} "
          f"Brevo={'✓' if BREVO_API_KEY else '✗'} "
          f"Resend={'✓' if RESEND_API_KEY else '✗'} "
          f"Gmail={'✓' if GMAIL_USER else '✗'}")

    if _via_mailersend(to_email, name, otp): return True
    if _via_brevo(to_email, name, otp):      return True
    if _via_resend(to_email, name, otp):     return True
    if _via_sendgrid(to_email, name, otp):   return True
    if _via_smtp(to_email, name, otp):       return True

    print(f"\n{'='*60}\n[OTP FALLBACK] to={to_email}  otp={otp}\n{'='*60}\n")
    return False


# ─────────────────────────────────────────────────────────────────────────────
def test_email_config(to_email: str) -> dict:
    """Called by /api/test-email — synchronous test returning verbose results."""
    import time

    cfg = {
        "mailersend_key_set": bool(MAILERSEND_API_KEY),
        "mailersend_domain":  MAILERSEND_DOMAIN or "(not set)",
        "brevo_key_set":      bool(BREVO_API_KEY),
        "brevo_sender":       BREVO_SENDER or GMAIL_USER or "(not set)",
        "resend_key_set":     bool(RESEND_API_KEY),
        "sendgrid_key_set":   bool(SENDGRID_API_KEY),
        "gmail_user":         GMAIL_USER or "(not set)",
    }

    results = {}

    # Test Mailersend
    if MAILERSEND_API_KEY and MAILERSEND_DOMAIN:
        try:
            t = time.time()
            r = _req.post(
                "https://api.mailersend.com/v1/email",
                json={
                    "from":    {"email": f"noreply@{MAILERSEND_DOMAIN}", "name": FROM_NAME},
                    "to":      [{"email": to_email, "name": "Test"}],
                    "subject": "AuraScore Email Test",
                    "html":    "<p>Email test from AuraScore. OTP: <b>123456</b></p>",
                },
                headers={"Authorization": f"Bearer {MAILERSEND_API_KEY}"},
                timeout=15,
            )
            results["mailersend"] = {
                "ok": r.status_code in (200, 201, 202),
                "status": r.status_code,
                "response": r.text[:400],
                "ms": int((time.time()-t)*1000),
            }
        except Exception as e:
            results["mailersend"] = {"ok": False, "error": str(e)}
    else:
        results["mailersend"] = {"ok": False, "reason": "MAILERSEND_API_KEY or MAILERSEND_DOMAIN not set"}

    # Test Brevo
    sender = BREVO_SENDER or GMAIL_USER
    if BREVO_API_KEY and sender:
        try:
            t = time.time()
            r = _req.post(
                "https://api.brevo.com/v3/smtp/email",
                json={
                    "sender":      {"name": FROM_NAME, "email": sender},
                    "to":          [{"email": to_email, "name": "Test"}],
                    "subject":     "AuraScore Email Test",
                    "htmlContent": "<p>Email test. OTP: <b>123456</b></p>",
                },
                headers={"api-key": BREVO_API_KEY, "accept": "application/json"},
                timeout=15,
            )
            results["brevo"] = {
                "ok": r.status_code in (200, 201, 202),
                "status": r.status_code,
                "response": r.text[:400],
                "ms": int((time.time()-t)*1000),
            }
        except Exception as e:
            results["brevo"] = {"ok": False, "error": str(e)}
    else:
        results["brevo"] = {"ok": False, "reason": "BREVO_API_KEY or sender not configured"}

    # Test Resend
    if RESEND_API_KEY:
        try:
            t = time.time()
            r = _req.post(
                "https://api.resend.com/emails",
                json={"from": f"{FROM_NAME} <onboarding@resend.dev>",
                      "to": [to_email], "subject": "AuraScore Email Test",
                      "html": "<p>Email test. OTP: <b>123456</b></p>"},
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                timeout=15,
            )
            results["resend"] = {
                "ok": r.status_code in (200, 201, 202),
                "status": r.status_code,
                "response": r.text[:400],
                "ms": int((time.time()-t)*1000),
            }
        except Exception as e:
            results["resend"] = {"ok": False, "error": str(e)}
    else:
        results["resend"] = {"ok": False, "reason": "RESEND_API_KEY not set"}

    return {
        "config": cfg,
        "results": results,
        "any_success": any(v.get("ok") for v in results.values()),
        "recommendation": (
            "Set MAILERSEND_API_KEY + MAILERSEND_DOMAIN from https://app.mailersend.com"
            if not cfg["mailersend_key_set"] else
            "Check 'results' above for exact error from each provider"
        ),
    }
