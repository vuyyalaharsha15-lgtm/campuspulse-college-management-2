from flask import Flask, render_template, request, redirect, url_for, session, send_file
import psycopg
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from psycopg.rows import dict_row
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import qrcode
import os
from dotenv import load_dotenv

load_dotenv()

from datetime import date, datetime, timedelta, timezone
import random
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing. Set a strong random value in .env.")

# ==========================================
# EMAIL CONFIGURATION (Google Apps Script HTTPS API)
# ==========================================

def send_email(subject, recipient, text_body):
    """Send email through a secured Google Apps Script HTTPS endpoint.

    Configure EMAIL_API_URL and EMAIL_API_SECRET in Render Environment.
    The Apps Script web app must be deployed to execute as its owner.
    """
    endpoint = os.getenv("EMAIL_API_URL", "").strip()
    secret = os.getenv("EMAIL_API_SECRET", "")

    if not endpoint or not secret:
        raise RuntimeError(
            "EMAIL_API_URL or EMAIL_API_SECRET is missing. "
            "Set both in Render Environment."
        )

    payload = {
        "secret": secret,
        "to": recipient,
        "subject": subject,
        "text": text_body,
    }

    req = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CampusPulse/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8", "replace")
            status = getattr(response, "status", 200)
    except HTTPError as exc:
        details = exc.read().decode("utf-8", "replace")
        # Do not log request payloads because they contain the OTP and secret.
        raise RuntimeError(
            f"Email HTTPS API error ({exc.code}): {details[:1000]}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            f"Could not reach email HTTPS API: {type(exc).__name__}: {exc}"
        ) from exc

    if status < 200 or status >= 300:
        raise RuntimeError(f"Email HTTPS API returned HTTP {status}: {raw[:1000]}")

    try:
        result = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError("Email API returned an invalid response.") from exc

    if result.get("ok") is not True:
        # Apps Script may return HTTP 200 with an application-level error.
        raise RuntimeError(
            "Email API rejected the request: " + str(result.get("error", "unknown error"))[:500]
        )

# ==========================================
# SUPABASE POSTGRESQL CONNECTION
# ==========================================

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url: