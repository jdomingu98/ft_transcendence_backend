from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q
from backend.utils.authentication import Authentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.http import Http404
import os
from backend.utils.jwt_tokens import verify_token
from backend.utils.oauth_utils import get_access_token, get_user_info, get_or_create_user
from backend.utils.pass_reset_utils import send_reset_email
from backend.utils.otp_utils import send_otp_code, verify_otp_code
from ..models import RefreshToken, User
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    MeNeedTokenSerializer,
    PasswordResetSerializer,
    OAuthCodeSerializer,
    OTPSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserSerializer,
    UserLeaderboardSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = User.objects.with_ranking()
        return queryset

    def get_serializer_class(self):
        serializer = super().get_serializer_class()
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

    def retrieve(self, request, pk=None):
        try:
            user = self.get_object()
        except Http404:
            return Response({"error": "ERROR.USER.NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        
        user_list = User.objects.with_ranking()

        user_position = next((i for i, u in enumerate(user_list, 1) if u.id == user.id), None)
        
        serializer = self.get_serializer(user)
        data = serializer.data
        data['position'] = user_position
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="login", url_name="login", serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.user
        if not user.is_verified:
            return Response({"error": "ERROR.USER.NOT_VERIFIED"}, status=status.HTTP_400_BAD_REQUEST)
        if user.two_factor_enabled:
            send_otp_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="otp", url_name="otp", serializer_class=OTPSerializer)
    def otp(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if verify_otp_code(user, request.data["code"]):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "ERROR.OTP_CODE"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="me", url_name="me", serializer_class=MeNeedTokenSerializer)
    def me(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(verify_token(request.data["token"]), status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="pass-reset", url_name="pass-reset", serializer_class=PasswordResetSerializer)
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username_or_email = serializer.validated_data["username_or_email"]
        user = get_object_or_404(User, Q(email=username_or_email) | Q(username=username_or_email))
        send_reset_email(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False, url_path="refresh", url_name="refresh", serializer_class=RefreshTokenSerializer)
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="logout", url_name="logout", serializer_class=LogoutSerializer)
    def logout(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.is_connected = False
        user.save()
        refresh_token = RefreshToken.objects.get(token=serializer.validated_data["token"])
        refresh_token.delete()
        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="change-password", url_name="change-password",serializer_class=ChangePasswordSerializer)
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
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        access_token = get_access_token(code)
        if not access_token:
            return Response({"error": "ERROR.OAUTH.TOKEN"}, status=status.HTTP_400_BAD_REQUEST)
        user_info = get_user_info(access_token)
        if not user_info:
            return Response({"error": "ERROR.OAUTH.USER_INFO"}, status=status.HTTP_400_BAD_REQUEST)
        user = get_or_create_user(user_info)
        if not user:
            return Response({"error": "ERROR.OAUTH.EMAIL_EXISTS"}, status=status.HTTP_400_BAD_REQUEST)
        login_serializer = LoginSerializer(user)

        return Response(login_serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=["GET"], detail=False, url_path="leaderboard", url_name="leaderboard", serializer_class=UserLeaderboardSerializer,
        authentication_classes=[Authentication], permission_classes=[IsAuthenticated])
    def leaderboard(self,request):
        user_list = User.objects.with_ranking()
        user = next((i for i in user_list if i.id == request.user.id), None)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, url_path="verify_account", url_name="verify_account")
    def verify_account(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_verified = True
        user.save()
        return redirect(os.getenv("FRONTEND_URL"))
