from rest_framework.authentication import BaseAuthentication
from backend.utils.jwt_tokens import verify_token
from apps.user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import get_default_password_validators


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get("Authorization")

        if not authorization_header:
            return None

        [key, token] = authorization_header.split(" ")
        if key != "Bearer":
            return None
        user_dict = verify_token(token)
        user = User.objects.get(id=user_dict["user_id"])

        return (user, token)


def validate_password(password, user=None, password_validators=None):
    """
    Validate that the password meets all validator requirements.

    If the password is valid, return ``None``.
    If the password is invalid, raise ValidationError with all error messages.
    """
    errors = []
    if password_validators is None:
        password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            if error.code == "password_too_similar":
                error.message = "ERROR.PASSWORD.TOO_SIMILAR"
            elif error.code == "password_too_short":
                error.message = "ERROR.PASSWORD.TOO_SHORT"
            elif error.code == "password_too_common":
                error.message = "ERROR.PASSWORD.TOO_COMMON"
            elif error.code == "password_entirely_numeric":
                error.message = "ERROR.PASSWORD.ENTIRELY_NUMERIC"
            errors.append(error)
    if errors:
        raise ValidationError(errors)
