from rest_framework.authentication import BaseAuthentication
from backend.utils.jwt_tokens import verify_token
from apps.user.models import User


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get("Authorization")

        if not authorization_header:
            return None

        token = authorization_header.split(" ")[1]
        user_dict = verify_token(token)
        user = User.objects.get(id=user_dict["user_id"])

        return (user, token)