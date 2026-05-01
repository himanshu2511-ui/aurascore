"""
AuraScore Email Service
=======================
Uses HTTP APIs only (no SMTP) — works on Render free tier.

Priority chain:
  1. Brevo HTTP API    — free 300/day, no domain needed, just API key
  2. Resend HTTP API   — free 3000/mo, needs verified domain for arbitrary recipients
  3. Gmail SMTP        — local dev only (Render blocks SMTP ports 465/587)
  4. Console fallback  — always prints OTP to logs

Required env vars (set ONE on Render):
  BREVO_API_KEY   — from https://app.brevo.com → Settings → API Keys
  BREVO_SENDER    — a verified sender email in your Brevo account
  RESEND_API_KEY  — from https://resend.com
"""

import os
import threading
import requests as _requests
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY      = os.getenv("BREVO_API_KEY", "").strip()
BREVO_SENDER       = os.getenv("BREVO_SENDER", "").strip()
RESEND_API_KEY     = os.getenv("RESEND_API_KEY", "").strip()
SENDGRID_API_KEY   = os.getenv("SENDGRID_API_KEY", "").strip()
SENDGRID_SENDER    = os.getenv("SENDGRID_SENDER", "").strip()
GMAIL_USER         = os.getenv("GMAIL_USER", "").strip()
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
            <p style="color:#4b5563;font-size:12px;">If you didn't sign up for AuraScore, ignore this email.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_brevo(to_email: str, name: str, otp: str) -> bool:
    """
    Brevo Transactional Email HTTP API.
    Pure HTTPS — not affected by Render's SMTP port block.
    """
    if not BREVO_API_KEY:
        print("[EMAIL] Brevo: BREVO_API_KEY not set, skipping.")
        return False

    sender_email = BREVO_SENDER or GMAIL_USER
    if not sender_email:
        print("[EMAIL] Brevo: BREVO_SENDER not set. "
              "Set BREVO_SENDER to a verified sender email in your Brevo account.")
        return False

    payload = {
        "sender":      {"name": FROM_NAME, "email": sender_email},
        "to":          [{"email": to_email, "name": name}],
        "subject":     "Your AuraScore Verification Code",
        "htmlContent": _build_otp_html(name, otp),
    }

    try:
        resp = _requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={"api-key": BREVO_API_KEY, "accept": "application/json"},
            timeout=15,
        )
        if resp.status_code in (200, 201, 202):
            print(f"[EMAIL OK] Brevo → {to_email} (status {resp.status_code})")
            return True
        else:
            print(f"[EMAIL FAIL] Brevo {resp.status_code}: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"[EMAIL FAIL] Brevo exception: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_resend(to_email: str, name: str, otp: str) -> bool:
    """
    Resend HTTP API.
    NOTE: Without a verified domain, onboarding@resend.dev only sends to
    your OWN Resend account email. To send to anyone, verify a domain at resend.com/domains
    """
    if not RESEND_API_KEY:
        print("[EMAIL] Resend: RESEND_API_KEY not set, skipping.")
        return False

    payload = {
        "from":    f"{FROM_NAME} <onboarding@resend.dev>",
        "to":      [to_email],
        "subject": "Your AuraScore Verification Code",
        "html":    _build_otp_html(name, otp),
    }

    try:
        resp = _requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            timeout=15,
        )
        if resp.status_code in (200, 201, 202):
            print(f"[EMAIL OK] Resend → {to_email} (status {resp.status_code})")
            return True
        else:
            print(f"[EMAIL FAIL] Resend {resp.status_code}: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"[EMAIL FAIL] Resend exception: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_sendgrid(to_email: str, name: str, otp: str) -> bool:
    if not SENDGRID_API_KEY:
        return False
    sender = SENDGRID_SENDER or GMAIL_USER
    if not sender:
        return False
    try:
        resp = _requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            json={
                "personalizations": [{"to": [{"email": to_email}],
                                       "subject": "Your AuraScore Verification Code"}],
                "from": {"email": sender, "name": FROM_NAME},
                "content": [{"type": "text/html", "value": _build_otp_html(name, otp)}],
            },
            headers={"Authorization": f"Bearer {SENDGRID_API_KEY}"},
            timeout=15,
        )
        if resp.status_code in (200, 201, 202):
            print(f"[EMAIL OK] SendGrid → {to_email}")
            return True
        print(f"[EMAIL FAIL] SendGrid {resp.status_code}: {resp.text[:500]}")
        return False
    except Exception as e:
        print(f"[EMAIL FAIL] SendGrid exception: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
def _send_via_smtp(to_email: str, name: str, otp: str) -> bool:
    """Gmail SMTP — local dev only. Render free tier blocks SMTP ports 465/587."""
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
                    s.login(GMAIL_USER, GMAIL_APP_PASSWORD); s.sendmail(GMAIL_USER, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=10) as s:
                    s.ehlo(); s.starttls(context=ctx); s.ehlo()
                    s.login(GMAIL_USER, GMAIL_APP_PASSWORD); s.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"[EMAIL OK] SMTP {method} → {to_email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH FAIL] {e}"); return False
        except Exception as e:
            print(f"[EMAIL] SMTP {method} port {port} failed: {type(e).__name__}: {e}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Try all email providers synchronously. Returns True if any succeeded.
    The caller should surface fallback_otp to the user when this returns False.
    """
    print(f"[EMAIL] Starting delivery attempt to {to_email}")
    print(f"[EMAIL] Config — BREVO_KEY={'set' if BREVO_API_KEY else 'NOT SET'} | "
          f"BREVO_SENDER={BREVO_SENDER or 'NOT SET'} | "
          f"RESEND_KEY={'set' if RESEND_API_KEY else 'NOT SET'} | "
          f"SENDGRID_KEY={'set' if SENDGRID_API_KEY else 'NOT SET'}")

    if _send_via_brevo(to_email, name, otp):
        return True
    if _send_via_resend(to_email, name, otp):
        return True
    if _send_via_sendgrid(to_email, name, otp):
        return True
    if _send_via_smtp(to_email, name, otp):
        return True

    print(f"\n{'='*60}")
    print(f"[OTP FALLBACK] to={to_email}  otp={otp}")
    print(f"  All email providers failed. Set BREVO_API_KEY on Render.")
    print(f"{'='*60}\n")
    return False


# ─────────────────────────────────────────────────────────────────────────────
def test_email_config(to_email: str) -> dict:
    """
    Synchronous email test that returns verbose results.
    Called by /api/test-email endpoint for debugging.
    """
    import time

    results = {
        "config": {
            "brevo_key_set":     bool(BREVO_API_KEY),
            "brevo_sender":      BREVO_SENDER or "(not set)",
            "resend_key_set":    bool(RESEND_API_KEY),
            "sendgrid_key_set":  bool(SENDGRID_API_KEY),
            "gmail_user":        GMAIL_USER or "(not set)",
        },
        "results": {},
    }

    test_otp = "123456"
    test_name = "Test"

    # Test Brevo
    if BREVO_API_KEY and (BREVO_SENDER or GMAIL_USER):
        sender = BREVO_SENDER or GMAIL_USER
        try:
            t = time.time()
            resp = _requests.post(
                "https://api.brevo.com/v3/smtp/email",
                json={
                    "sender":      {"name": FROM_NAME, "email": sender},
                    "to":          [{"email": to_email, "name": test_name}],
                    "subject":     "AuraScore Email Test",
                    "htmlContent": f"<p>Test OTP: <b>{test_otp}</b></p>",
                },
                headers={"api-key": BREVO_API_KEY, "accept": "application/json"},
                timeout=15,
            )
            results["results"]["brevo"] = {
                "status_code": resp.status_code,
                "ok": resp.status_code in (200, 201, 202),
                "response": resp.text[:300],
                "elapsed_ms": int((time.time() - t) * 1000),
            }
        except Exception as e:
            results["results"]["brevo"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    else:
        results["results"]["brevo"] = {"ok": False, "error": "BREVO_API_KEY or BREVO_SENDER not configured"}

    # Test Resend
    if RESEND_API_KEY:
        try:
            t = time.time()
            resp = _requests.post(
                "https://api.resend.com/emails",
                json={"from": f"{FROM_NAME} <onboarding@resend.dev>",
                      "to": [to_email], "subject": "AuraScore Email Test",
                      "html": f"<p>Test OTP: <b>{test_otp}</b></p>"},
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                timeout=15,
            )
            results["results"]["resend"] = {
                "status_code": resp.status_code,
                "ok": resp.status_code in (200, 201, 202),
                "response": resp.text[:300],
                "elapsed_ms": int((time.time() - t) * 1000),
            }
        except Exception as e:
            results["results"]["resend"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    else:
        results["results"]["resend"] = {"ok": False, "error": "RESEND_API_KEY not configured"}

    results["overall_success"] = any(v.get("ok") for v in results["results"].values())
    return results
