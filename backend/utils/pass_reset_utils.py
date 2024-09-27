from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import datetime, timedelta, timezone
import jwt
import os
import pynliner
from apps.user.models import User
from .email_sender import EmailSender

def get_user_by_username_or_email(username_or_email):
    return get_object_or_404(User, Q(email=username_or_email) | Q(username=username_or_email))

def generate_reset_token(user_id, private_key):
    payload = {
        "user_id": user_id,
        "change_password": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def create_reset_link(token):
    frontend_url = os.getenv("FRONTEND_URL")
    return f"{frontend_url}/reset-password/?k={token}"

def render_email_content(username, reset_link):
    email_content = render_to_string("changePassword.html", {"username": username, "reset_link": reset_link})
    inliner = pynliner.Pynliner()
    return inliner.from_string(email_content).run()

def send_reset_email(email, email_content):
    emails = EmailSender()
    emails.send_email_html(email, "Recover Password Request", email_content)