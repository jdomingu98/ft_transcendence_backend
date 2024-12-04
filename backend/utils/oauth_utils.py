import requests
import os
from apps.user.models import User


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

    filterUser = User.objects.filter(email=email).first()
    if filterUser and not filterUser.id42:
        return None
    
    if filterUser:
        return filterUser

    if User.objects.filter(username=username).exists():
        username = f"{username}_42"

    user = User.objects.create(id42=id_42, username=username, email=email, is_verified=True)

    return user
