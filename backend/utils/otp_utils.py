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
    if(OTPCode.objects.filter(user_id=user.id, expiration_time__gt=timezone.now()).exists()):
        return

    code = generate_code()
    OTPCode.objects.create(
        code=code,
        expiration_time=timezone.now() + timedelta(minutes=5),
        user=user
    )

    EmailSender().send_email_template(
        user.email,
        "Your two-factor sign in code", 
        "oneTimePassword.html", 
        {"code": code}
    )

def verify_otp_code(user: User, code: str):
    otp_expired = OTPCode.objects.filter(
        user_id=user.id,
        code=code,
        expiration_time__lt=timezone.now()
    )

    if otp_expired.exists():
        otp_expired.delete()
        raise Exception("OTP code has expired")
    
    otp_exists = OTPCode.objects.filter(
        user_id=user.id,
        code=code,
        expiration_time__gt=timezone.now()
    )

    if not otp_exists.exists():
        raise Exception("Invalid OTP code")

    OTPCode.objects.filter(user_id=user.id).delete()
    return True