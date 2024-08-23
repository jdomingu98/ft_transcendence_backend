import datetime
from datetime import timezone

import jwt
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.user.models import RefreshToken
from .read_keys import read_private_key, read_public_key


def generate_access_token(user_id, user_email):
    private_key = read_private_key()
    now = datetime.datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "user_email": user_email,
        "exp": now + datetime.timedelta(minutes=1),
        "iat": now,
    }

    access_token = jwt.encode(payload, private_key, algorithm="RS256")
    return access_token


def generate_refresh_token(user_id, user_email):
    """This function generates a refresh token"""
    private_key = read_private_key()
    now = datetime.datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "user_email": user_email,
        "exp": now + datetime.timedelta(minutes=2),
        "iat": now,
    }

    refresh_token = jwt.encode(payload, private_key, algorithm="RS256")

    return refresh_token


@transaction.atomic
def store_token_at_bd(user_id, refresh_token):
    """This function ensures there is only one token at DB for an user"""
    RefreshToken.objects.filter(user_id=user_id).delete()
    RefreshToken.objects.create(user_id=user_id, token=refresh_token)


def verify_token(token):
    public_key = read_public_key()
    try:
        return jwt.decode(token, public_key, algorithms=["RS256"])
    except jwt.ExpiredSignatureError as e:
        raise ValidationError("Expired token") from e
    except jwt.InvalidTokenError as e:
        raise ValidationError("Invalid token") from e


def generate_new_tokens_from_user(user_id, user_email):
    access_token = generate_access_token(user_id, user_email)
    new_refresh_token = generate_refresh_token(user_id, user_email)
    store_token_at_bd(user_id, new_refresh_token)

    return access_token, new_refresh_token


def generate_new_tokens(refresh_token):
    """
    This function aims to generate a pair of tokens (access and refresh).
    To achieve this, it verifies the refresh token and validates if it is at db.
    After this validations, it generates the new pair and invalidates the old refresh token.
    """
    payload = verify_token(refresh_token)

    user_id = payload["user_id"]
    user_email = payload["user_email"]

    if RefreshToken.objects.filter(token=refresh_token, user_id=user_id).exists():
        access_token, new_refresh_token = generate_new_tokens_from_user(user_id, user_email)
        store_token_at_bd(user_id, new_refresh_token)
        return access_token, new_refresh_token
    raise ValidationError("Invalid token")
