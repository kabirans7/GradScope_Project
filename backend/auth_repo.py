from datetime import date
import bcrypt
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from backend.db import get_engine
import secrets, hashlib, smtplib
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
import streamlit as st

engine = get_engine()

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def email_exists(email: str) -> bool:
    email = email.lower().strip()
    with engine.connect() as conn: 
        row = conn.execute(
            text("SELECT 1 FROM credential WHERE email = :email LIMIT 1"),
            {"email": email},
        ).fetchone()
        return row is not None 

def signup_admin(first_name, last_name, university_name, university_occupation, email, password):
    email = email.lower().strip()
    pw_hash = _hash_password(password)

    try:
        with engine.begin() as conn:
            admin_id = conn.execute(
                text("""
                    INSERT INTO admin (first_name, last_name, university_name, university_occupation)
                    VALUES (:fn, :ln, :un, :uo)
                    RETURNING admin_id
                """),
                {
                    "fn": first_name,
                    "ln": last_name,
                    "un": university_name,
                    "uo": university_occupation
                },
            ).scalar_one()

            # Must be inside same connection
            conn.execute(
                text("""
                    INSERT INTO credential (email, password_hash, start_date, end_date, admin_id)
                    VALUES (:email, :ph, :sd, NULL, :aid)
                """),
                {"email": email, "ph": pw_hash, "sd": date.today(), "aid": admin_id},
            )

        return admin_id, None

    except IntegrityError:
        return None, "Email already exists"
    except Exception as e:
        return None, str(e)


def login(email: str, password: str):
    """
    Returns user dict if OK, else None.
    """

    email = email.lower().strip()

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT c.password_hash, a.admin_id, a.first_name, a.last_name
                FROM credential c
                JOIN admin a ON a.admin_id = c.admin_id
                WHERE c.email = :email
                  AND (c.end_date IS NULL OR c.end_date > CURRENT_DATE)
                ORDER BY c.credential_id DESC
                LIMIT 1
            """),
            {"email": email},
        ).fetchone()

    if not row:
        return None
    
    if _verify_password(password, row.password_hash):
        return {
            "admin_id": row.admin_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": email,
        }

    return None

def _token_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _send_reset_email(to_email: str, reset_link: str):
    email_cfg = st.secrets["email"]
    
    host = email_cfg["SMTP_HOST"]
    port = int(email_cfg.get("SMTP_PORT", 587))
    user = email_cfg["SMTP_USER"]
    pw = email_cfg["SMTP_PASS"]
    from_email = email_cfg.get("FROM_EMAIL", user)


    msg = EmailMessage()
    msg["Subject"] = "Reset your GradScope password"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(
        f"""Hi,

Click this link to reset your password (expires in 30 minutes):
{reset_link}

If you didn't request this, ignore this email.
"""
    )

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, pw)
        server.send_message(msg)

def request_password_reset(email: str) -> None:
    """
    Always behaves like success.
    If email exists, create token row and email link.
    """
    email = email.lower().strip()

    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT credential_id FROM credential WHERE email = :email LIMIT 1"),
            {"email": email},
        ).fetchone()

        if not row:
            return

        credential_id = row[0]
        raw_token = secrets.token_urlsafe(32)
        th = _token_hash(raw_token)
        expires = datetime.now(timezone.utc) + timedelta(minutes=30)

        conn.execute(
            text("""
                INSERT INTO password_reset (credential_id, token_hash, expires_at)
                VALUES (:cid, :th, :exp)
            """),
            {"cid": credential_id, "th": th, "exp": expires},
        )

    app_url = st.secrets["email"]["APP_URL"]
    reset_link = f"{app_url}/?page=reset&token={raw_token}"
    _send_reset_email(email, reset_link)

def reset_password_with_token(raw_token: str, new_password: str):
    """
    Validate token, update password_hash, mark token used.
    Returns (ok: bool, message: str)
    """
    th = _token_hash(raw_token)

    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT pr.reset_id, pr.credential_id, pr.expires_at, pr.used_at
                FROM password_reset pr
                WHERE pr.token_hash = :th
                ORDER BY pr.created_at DESC
                LIMIT 1
            """),
            {"th": th},
        ).fetchone()

        if not row:
            return False, "Invalid reset link."

        if row.used_at is not None:
            return False, "This reset link was already used."

        # Check expiry
        if row.expires_at < datetime.now(timezone.utc):
            return False, "This reset link has expired. Request a new one."

        pw_hash = _hash_password(new_password)

        conn.execute(
            text("""
                UPDATE credential
                SET password_hash = :ph
                WHERE credential_id = :cid
            """),
            {"ph": pw_hash, "cid": row.credential_id},
        )

        conn.execute(
            text("""
                UPDATE password_reset
                SET used_at = NOW()
                WHERE reset_id = :rid
            """),
            {"rid": row.reset_id},
        )

    return True, "Password updated."



