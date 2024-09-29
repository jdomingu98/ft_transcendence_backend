from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q

from backend.utils.jwt_tokens import verify_token
from backend.utils.oauth_utils import get_access_token, get_user_info, get_or_create_user
from backend.utils.pass_reset_utils import send_reset_email

from ..models import RefreshToken, User
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordResetSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    OAuthCodeSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserSerializer,
    meNeedTokenSerializer,
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("username")

    def get_serializer_class(self):
        serializer = UserSerializer
        if self.action == "create":
            serializer = RegisterSerializer
        elif self.action == "retrieve":
            serializer = UserRetrieveSerializer
        elif self.action == "list":
            serializer = UserListSerializer
        elif self.action in ("update", "partial_update"):
            serializer = UserUpdateSerializer
        elif self.action == "destroy":
            serializer = UserSerializer
        return serializer

    @action(methods=["POST"], detail=False, url_path="login", url_name="login", serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="me", url_name="me", serializer_class=meNeedTokenSerializer)
    def me(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(verify_token(request.data["token"]), status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        url_path="pass-reset",
        url_name="pass-reset",
        serializer_class=PasswordResetSerializer,
    )
    def password_reset(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            username_or_email = serializer.validated_data["username_or_email"]
            user = get_object_or_404(User, Q(email=username_or_email) | Q(username=username_or_email))
            send_reset_email(user)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"error": "ERROR.PASSWORD_RESET"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"], detail=False, url_path="refresh", url_name="refresh", serializer_class=RefreshTokenSerializer
    )
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="logout", url_name="logout", serializer_class=LogoutSerializer)
    def logout(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.is_connected = False
            user.save()
            refresh_token = RefreshToken.objects.get(token=serializer.validated_data["token"])
            refresh_token.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        url_path="change-password",
        url_name="change-password",
        serializer_class=ChangePasswordSerializer,
    )
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = serializer.validated_data
        user.set_password(request.data.get("new_password"))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False, url_path="oauth", url_name="oauth", serializer_class=OAuthCodeSerializer)
    def oauth(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data["code"]
        access_token = get_access_token(code)
        if not access_token:
            return Response({"error": "ERROR.OAUTH.TOKEN"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = get_user_info(access_token)
        if not user_info:
            return Response({"error": "ERROR.OAUTH.USER_INFO"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_or_create_user(user_info)
        login_serializer = LoginSerializer(user)

        return Response(
            login_serializer.data,
            status=status.HTTP_200_OK,
        )
