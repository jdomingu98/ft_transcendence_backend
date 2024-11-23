from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q
from backend.utils.oauth_utils import get_access_token, get_user_info, get_or_create_user
from backend.utils.pass_reset_utils import send_reset_email
from backend.utils.pagination import paginate_matches
from ..models import RefreshToken, User, FriendShip
from apps.game.models import LocalMatch
from backend.utils.authentication import Authentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from apps.user.v1.filters import UserFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
import os
from backend.utils.pagination import paginate
from .permissions import UserPermissions
from backend.utils.otp_utils import send_otp_code, verify_otp_code
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    MeNeedTokenSerializer,
    PasswordResetSerializer,
    OAuthCodeSerializer,
    OTPSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserSerializer,
    FriendSerializer,
    AcceptFriendSerializer,
    UserLeaderboardSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    MyRequestsFriendsSerializer,
    CancelFriendRequestSerializer,
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    authentication_classes = [Authentication]
    permission_classes = [UserPermissions]
    filterset_class = UserFilter

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    def list(self, request, *args, **kwargs):
        users = self.filter_queryset(self.get_queryset())
        if request.query_params.get("paginate"):
            return paginate(users, request, self.get_serializer_class(), 12)
        return Response(self.get_serializer(users[:50], many=True).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            user = self.get_object()
        except Http404:
            return Response({"error": ["ERROR.USER.NOT_FOUND"]}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({"error": ["ERROR.USER.NOT_VERIFIED"]}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({"error": ["ERROR.OTP_CODE"]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="me", url_name="me", serializer_class=MeNeedTokenSerializer)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(methods=["POST"], detail=False, url_path="logout", url_name="logout")
    def logout(self, request):
        user = request.user
        request.user.is_connected = False
        request.user.save()
        RefreshToken.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        access_token = get_access_token(code)
        if not access_token:
            return Response({"error": ["ERROR.OAUTH.TOKEN"]}, status=status.HTTP_400_BAD_REQUEST)
        user_info = get_user_info(access_token)
        if not user_info:
            return Response({"error": ["ERROR.OAUTH.USER_INFO"]}, status=status.HTTP_400_BAD_REQUEST)
        user = get_or_create_user(user_info)
        if not user:
            return Response({"error": ["ERROR.OAUTH.EMAIL_EXISTS"]}, status=status.HTTP_400_BAD_REQUEST)
        login_serializer = LoginSerializer(user)

        return Response(login_serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="leaderboard", url_name="leaderboard", serializer_class=UserLeaderboardSerializer)
    def leaderboard(self, request):
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

    @action(methods=["GET"], detail=True, url_path="match", url_name="match")
    def match(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        matches = LocalMatch.objects.filter(Q(user_a=user)).order_by('-start_date')

        return paginate_matches(matches, request)


class FriendsViewSet(ModelViewSet):
    serializer_class = FriendSerializer
    authentication_classes = [Authentication]
    permission_classes = [IsAuthenticated]
    queryset = FriendShip.objects.all()
    http_method_names = ["get", "post", "delete"]

    @action(methods=["POST"], detail=False, url_path="accept", url_name="accept", serializer_class=AcceptFriendSerializer)
    def accept(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friendship: FriendShip = serializer.validated_data

        friendship.accepted = True
        with transaction.atomic():
            friendship.save()
            FriendShip.objects.create(user_id=request.user.id, friend_id=friendship.user_id, accepted=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=False, url_path="cancel", url_name="cancel", serializer_class=CancelFriendRequestSerializer)
    def cancel(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False, url_path="requests", url_name="requests", serializer_class=MyRequestsFriendsSerializer)
    def requests(self, request, *args, **kwargs):
        user = self.request.user
        friends = FriendShip.objects.filter(friend=user, accepted=False)
        return Response(self.get_serializer(friends, many=True).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        friend = get_object_or_404(User, id=kwargs["pk"])
        user = self.request.user
        FriendShip.objects.filter(Q(user=user, friend=friend) | Q(user=friend, friend=user)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
