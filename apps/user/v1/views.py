from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from .serializers import RegisterSerializer, LoginSerializer, PasswordResetSerializer, RefreshTokenSerializer
from ..models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from backend.utils.email_sender import EmailSender
import jwt
from datetime import datetime, timedelta
import os
from datetime import timezone
from backend.utils.read_keys import read_private_key
from django.template.loader import render_to_string
from backend.utils.read_keys import read_private_key, read_public_key
from backend.utils.jwt_tokens import generate_new_tokens, generate_new_tokens_from_user, verify_token
from ..models import RefreshToken

class Register(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            access_token, new_refresh_token = generate_new_tokens_from_user(user.id, user.email)
            return Response({"access_token": access_token, "refresh_token": new_refresh_token}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)