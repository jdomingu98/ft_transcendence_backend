import os
from datetime import datetime, timedelta, timezone

import pynliner
import jwt
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from backend.utils.email_sender import EmailSender
from backend.utils.jwt_tokens import verify_token
from backend.utils.read_keys import read_private_key
from backend.utils.oauth_utils import get_access_token, get_user_info, get_or_create_user

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
        if self.action == "create":
            return RegisterSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        elif self.action == "list":
            return UserListSerializer
        elif self.action == "update":
            return UserUpdateSerializer
        elif self.action == "partial_update":
            return UserUpdateSerializer
        elif self.action == "destroy":
            return UserSerializer
        return super().get_serializer_class()
        
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
    
    @action(methods=["POST"], detail=False, url_path="pass-reset", url_name="pass-reset", serializer_class=PasswordResetSerializer)
    def password_reset(self, request):
        emails = EmailSender()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_or_email = serializer.validated_data["username_or_email"]
        user = get_object_or_404(User, Q(email=username_or_email) | Q(username=username_or_email))

        private_key = read_private_key()

        payload = {
            "user_id": user.id,
            "change_password": True,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }

        token = jwt.encode(payload, private_key, algorithm="RS256")

        frontend_url = os.getenv("FRONTEND_URL")

        reset_link = f"{frontend_url}/reset-password/?k={token}"

        email_content = render_to_string("changePassword.html", {"username": user.username, "reset_link": reset_link})

        inliner = pynliner.Pynliner()
        email_content_inline = inliner.from_string(email_content).run()

        emails.send_email_html(user.email, "Recover Password Request", email_content_inline)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False, url_path="refresh", url_name="refresh", serializer_class=RefreshTokenSerializer)
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
    
    @action(methods=["POST"], detail=False, url_path="change-password", url_name="change-password", serializer_class=ChangePasswordSerializer)
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
