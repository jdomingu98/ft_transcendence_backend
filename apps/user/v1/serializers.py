from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from backend.utils.jwt_tokens import generate_new_tokens, generate_new_tokens_from_user, verify_token
from ..models import RefreshToken, User
from apps.game.models import LocalMatch
from backend.utils.conf_reg_utils import send_conf_reg
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator, EmailValidator
from backend.utils.mixins.custom_error_messages import FtErrorMessagesMixin
from backend.utils import authentication


class RegisterSerializer(FtErrorMessagesMixin, serializers.ModelSerializer):
    repeat_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)

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
        )
        ft_error_messages = {
            'username': {
                UniqueValidator: 'ERROR.USERNAME.ALREADY_EXISTS',
                RegexValidator: 'ERROR.USERNAME.INVALID',
            },
            'email': {
                UniqueValidator: 'ERROR.EMAIL.ALREADY_EXISTS',
                EmailValidator: 'ERROR.EMAIL.INVALID',
            },
        }

    def create(self, validated_data):
        validated_data.pop("repeat_password", None)
        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)
        send_conf_reg(user)
        return user

    def validate_password(self, value):
        user = User(
            **{
                "username": self.initial_data.get("username"),
                "email": self.initial_data.get("email"),
            }
        )
        authentication.validate_password(value, user)
        return value

    def validate(self, data):
        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError({
                "repeat_password": ["ERROR.PASSWORD.DONT_MATCH"]
            })
        return data


class UserRetrieveSerializer(serializers.ModelSerializer):
    max_streak = serializers.IntegerField(source="statistics.max_streak", read_only=True)
    win_rate = serializers.IntegerField(source="statistics.win_rate", read_only=True)
    num_goals_scored = serializers.IntegerField(source="statistics.num_goals_scored", read_only=True)
    num_goals_against = serializers.IntegerField(source="statistics.num_goals_against", read_only=True)
    num_goals_stopped = serializers.IntegerField(source="statistics.num_goals_stopped", read_only=True)
    punctuation = serializers.IntegerField(source="statistics.punctuation", read_only=True)
    time_played = serializers.SerializerMethodField()
    position = serializers.IntegerField(read_only=True)

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
            "max_streak",
            "win_rate",
            "time_played",
            "num_goals_scored",
            "num_goals_against",
            "num_goals_stopped",
            "punctuation",
            "position",
        )

    def get_time_played(self, obj):
        duration = obj.statistics.time_played
        total_seconds = duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


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
            raise serializers.ValidationError({"error": "ERROR.USER.INVALID_LOGIN"})
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


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    repeat_new_password = serializers.CharField(write_only=True)
    change_password_token = serializers.CharField(write_only=True)

    def validate(self, data):
        payload = verify_token(data["change_password_token"])
        if not payload.get("change_password"):
            raise serializers.ValidationError({"error": "ERROR.INVALID_TOKEN"})
        new_password = data["new_password"]
        repeat_new_password = data["repeat_new_password"]
        if new_password != repeat_new_password:
            raise serializers.ValidationError({"error": "ERROR.PASSWORD.DONT_MATCH"})

        user = User.objects.get(id=payload.get("user_id"))
        authentication.validate_password(new_password, user)
        return user


class OAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class MeNeedTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class LeaderboardSerializer(serializers.ModelSerializer):
    punctuation = serializers.IntegerField(source='statistics.punctuation')

    class Meta:
        model = User
        fields = ['username', 'profile_img', 'id', 'punctuation']


class UserLeaderboardSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    punctuation = serializers.IntegerField(source='statistics.punctuation')
    leaderboard = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['punctuation', 'position', 'leaderboard']

    def get_leaderboard(self, obj):
        top_users = User.objects.with_ranking()[:10]
        return LeaderboardSerializer(top_users, many=True).data


class OTPSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, data):
        user = get_object_or_404(User, username=data["username"])
        self.user = user
        return user

    def to_representation(self, instance):
        access_token, refresh_token = generate_new_tokens_from_user(instance.id, instance.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "two_factor_enabled": instance.two_factor_enabled
        }


class LocalMatchSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    earned = serializers.SerializerMethodField()
    against = serializers.CharField(source='user_b', read_only=True)

    class Meta:
        model = LocalMatch
        fields = (
            'id',
            'time_played',
            'against',
            'result',
            'earned',
        )

    def get_result(self, obj):
        if obj.num_goals_scored > obj.num_goals_against:
            return 'victory'
        elif obj.num_goals_scored < obj.num_goals_against:
            return 'defeat'
        else:
            return 'draw'

    def get_earned(self, obj):
        if obj.num_goals_scored > obj.num_goals_against:
            return 10
        elif obj.num_goals_scored < obj.num_goals_against:
            return -5
        else:
            return 0
