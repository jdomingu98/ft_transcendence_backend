from .email_sender import EmailSender
from apps.user.models import User
import os
from django.conf import settings


def create_verify_link(user: User) -> str:
    return f"{settings.BASE_URL}/api/v1/user/{user.id}/verify_account/" 

def send_conf_reg(user: User):

   EmailSender().send_email_template(
        user.email,
        "Almost There! Confirm Your Account",
        "confirmRegistration.html",
        {"username": user.username, "verify_link": create_verify_link(user)},
    )