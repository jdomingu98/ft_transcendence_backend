import requests
import os
from django.db.utils import IntegrityError
from apps.user.models import User
from rest_framework import serializers


def get_access_token(code):
    token_url = "https://api.intra.42.fr/oauth/token"
    client_id = os.getenv("OAUTH_UID")
    client_secret = os.getenv("OAUTH_SECRET")
    redirect_uri = os.getenv("OAUTH_REDIRECT_URI")

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }

    response = requests.post(token_url, data=payload, timeout=10)
    token_data = response.json()
    return token_data.get("access_token")


def get_user_info(access_token):
    user_info_url = "https://api.intra.42.fr/v2/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def get_or_create_user(user_info):
    id_42 = user_info["id"]
    username = user_info["login"]
    email = user_info["email"]

    if User.objects.filter(username=username).exists():
        username = f"{username}_42"

    user, _ = User.objects.get_or_create(id42=id_42, defaults={"username": username, "email": email})

    return user
