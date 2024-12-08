import string
import random
from datetime import timedelta
from django.utils import timezone
from apps.user.models import User, OTPCode
from .email_sender import EmailSender


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choices(characters, k=length))
    return code


def send_otp_code(user: User):
    if OTPCode.objects.filter(user_id=user.id, expiration_time__gt=timezone.now()).exists():
        return
    
    OTPCode.objects.filter(user_id=user.id).delete()
    
    code = generate_code()
    OTPCode.objects.create(
        code=code,
        expiration_time=timezone.now() + timedelta(minutes=1),
        user=user
    )

    template_name = f"oneTimePassword/{user.language}.html"

    EmailSender().send_email_template(
        user.email,
        "Your two-factor sign in code",
        template_name,
        {"code": code}
    )


def verify_otp_code(user: User, code: str):
    otp_exists = OTPCode.objects.filter(
        user_id=user.id,
        code=code,
        expiration_time__gt=timezone.now()
    ).exists()

    if otp_exists:
        OTPCode.objects.filter(user_id=user.id).delete()

    return otp_exists
