from datetime import datetime, timedelta, timezone
import jwt
import os
from apps.user.models import User
from .email_sender import EmailSender
from .read_keys import read_private_key


def generate_reset_token(user_id: int) -> str:
    private_key = read_private_key()
    payload = {
        "user_id": user_id,
        "change_password": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def create_reset_link(user_id: int) -> str:
    token = generate_reset_token(user_id)
    frontend_url = os.getenv("FRONTEND_URL")
    return f"{frontend_url}/reset-password/?k={token}"


def send_reset_email(user: User):
    reset_link = create_reset_link(user.id)
    emails = EmailSender()
    emails.send_email_template(
        user.email,
        "Recover Password Request",
        "changePassword.html",
        {"username": user.username, "reset_dlink": reset_link},
    )
