from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from backend.utils.jwt_tokens import generate_new_tokens, generate_new_tokens_from_user, verify_token

from ..models import RefreshToken, User


class RegisterSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "language",
            "visibility",
            "profile_img",
            "banner",
            "repeat_password",
            "access_token",
            "refresh_token",
        )

    def create(self, validated_data):
        validated_data.pop("repeat_password", None)
        validated_data["password"] = make_password(validated_data["password"])
        return User.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        access_token, refresh_token = generate_new_tokens_from_user(instance.id, instance.email)
        representation["access_token"] = access_token
        representation["refresh_token"] = refresh_token
        return representation

    def validate_password(self, value):
        user = User(
            **{
                "username": self.initial_data.get("username"),
                "email": self.initial_data.get("email"),
            }
        )
        password_validation.validate_password(value, user)
        return value

    def validate(self, data):
        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "profile_img",
            "banner",
            "visibility",
            "is_connected",
            "language",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "profile_img",
            "banner",
            "visibility",
            "language",
            "two_factor_enabled",
        )


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_img",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'profile_img',
            'banner',
            'visibility',
            'is_connected',
            'language',
            'id42',
            'two_factor_enabled',
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    two_factor_enabled = serializers.BooleanField(read_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid username/password.")
        self.user = user
        return user

    def to_representation(self, instance):
        access_token, refresh_token = (
            generate_new_tokens_from_user(instance.id, instance.email)
            if not instance.two_factor_enabled else (None, None)
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "two_factor_enabled": instance.two_factor_enabled
        }


class PasswordResetSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        access_token, refresh_token = generate_new_tokens(instance["token"])
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate(self, data):
        token = data["token"]
        try:
            refresh_token = RefreshToken.objects.get(token=token)
            data["user"] = refresh_token.user
        except RefreshToken.DoesNotExist as e:
            raise serializers.ValidationError("Invalid token") from e
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    repeat_new_password = serializers.CharField(write_only=True)
    change_password_token = serializers.CharField(write_only=True)

    def validate(self, data):
        payload = verify_token(data["change_password_token"])
        if not payload.get("change_password"):
            raise serializers.ValidationError("Is not change_password_token")
        new_password = data["new_password"]
        repeat_new_password = data["repeat_new_password"]
        if new_password != repeat_new_password:
            raise serializers.ValidationError("The password doesn´t match")

        return User.objects.get(id=payload.get("user_id"))


class OAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class MeNeedTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class OTPSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid username/password.")
        self.user = user
        return user

    def to_representation(self, instance):
        access_token, refresh_token = generate_new_tokens_from_user(instance.id, instance.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "two_factor_enabled": instance.two_factor_enabled
        }
