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
)


class Register(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    def post(self, request):
        return Response(verify_token(request.data["token"]), status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    def post(self, request):
        emails = EmailSender()
        serializer = PasswordResetSerializer(data=request.data)
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


class RefreshTokenView(APIView):
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.is_connected = False
            user.save()
            refresh_token = RefreshToken.objects.get(token=serializer.validated_data["token"])
            refresh_token.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = serializer.validated_data
        user.set_password(request.data.get("new_password"))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OAuthView(APIView):
    def post(self, request):
        serializer = OAuthCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            access_token = get_access_token(code)
            if access_token:
                user_info = get_user_info(access_token)
                if user_info:
                    user = get_or_create_user(user_info)
                    login_serializer = LoginSerializer(user)
                    tokens = login_serializer.to_representation(user)
                    return Response(
                        {"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]},
                        status=status.HTTP_200_OK,
                    )
                return Response({"error": "Failed to retrieve user info"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "No access token found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
