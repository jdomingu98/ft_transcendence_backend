
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from backend.utils.jwt_tokens import verify_token
from backend.utils.read_keys import read_private_key
from backend.utils.oauth_utils import get_access_token, get_user_info, get_or_create_user
from backend.utils.pass_reset_utils import (
    get_user_by_username_or_email,
    generate_reset_token,
    create_reset_link,
    render_email_content,
    send_reset_email,
)

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
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            username_or_email = serializer.validated_data["username_or_email"]
            user = get_user_by_username_or_email(username_or_email)

            private_key = read_private_key()

            token = generate_reset_token(user.id, private_key)
            reset_link = create_reset_link(token)
            email_content = render_email_content(user.username, reset_link)
            send_reset_email(user.email, email_content)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
