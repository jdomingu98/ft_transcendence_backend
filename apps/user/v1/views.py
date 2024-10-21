from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q,F

from backend.utils.jwt_tokens import verify_token
from backend.utils.oauth_utils import get_access_token, get_user_info, get_or_create_user
from backend.utils.pass_reset_utils import send_reset_email
from django.core.exceptions import ValidationError

from ..models import RefreshToken, User, FriendShip
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
    MeNeedTokenSerializer, 
    FriendSerializer,
    FriendsListSerializer
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("username")

    serializer_class = UserSerializer
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

    @action(methods=["POST"], detail=False, url_path="login", url_name="login", serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="me", url_name="me", serializer_class=MeNeedTokenSerializer)
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
        if not user:
            return Response({"error": "ERROR.OAUTH.EMAIL_EXISTS"}, status=status.HTTP_400_BAD_REQUEST)
        login_serializer = LoginSerializer(user)

        return Response(
            login_serializer.data,
            status=status.HTTP_200_OK,
        )

class FriendsViewSet(ModelViewSet):
    serializer_class = FriendSerializer
    queryset = FriendShip.objects.all()
    
    def list(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs.get("user_pk"))
        friendships = FriendShip.objects.filter(
            Q(user_id=user.id) | Q(friend_id=user.id),
            accepted=True
        )
        friend_ids = {
            i.friend_id if i.user_id == user.id else i.user_id
            for i in friendships
        }
        data = {'friends_ids': friend_ids}
        serializer = FriendsListSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs.get("user_pk"))
        user_id = user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        friend_id = serializer.validated_data.get("friend_id")

        if user_id == friend_id:
            return Response({"error": "ERROR.FRIENDS.YOURSELF"}, status=status.HTTP_400_BAD_REQUEST)

        if FriendShip.objects.filter(
                Q(user_id=user_id, friend_id=friend_id) | Q(user_id=friend_id, friend_id=user_id)
            ).exists():
            return Response({"error": "ERROR.FRIENDS.FRIENDSHIP_EXISTS"}, status=status.HTTP_400_BAD_REQUEST)

        FriendShip.objects.create(user_id=user_id, friend_id=friend_id, accepted=False)
        return Response(status=status.HTTP_201_CREATED)
    
    @action(methods=["POST"], detail=False, url_path="accept", url_name="accept")
    def accept(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs.get("user_pk"))
        user_id = user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        friend_id = serializer.validated_data.get("friend_id")
        friendShip = FriendShip.objects.get(
            Q(user_id=friend_id, friend_id=user_id) 
        )
        if not friendShip:
            raise ValidationError({"error": "ERROR.FRIEND.YOU_ARE_NOT_MY_FRIEND:("})

        if friendShip.accepted:
            return Response({"error": 'ERROR.FRIEND.WAS_ACCEPTED'}, status=status.HTTP_400_BAD_REQUEST)
        
        friendShip.accepted = True
        friendShip.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    
    def delete(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs.get("user_pk"))
        user_id = user.id

        friend_id = request.data.get("friend_id")

        friendship = FriendShip.objects.filter(
            Q(user_id=user_id, friend_id=friend_id) | 
            Q(user_id=friend_id, friend_id=user_id)
        ).first()

        if not friendship:
            return Response({"error": "ERROR.FRIEND.FRIENDSHIP_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
