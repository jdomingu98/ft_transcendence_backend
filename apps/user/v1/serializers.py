from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db.models import Q
from backend.utils.jwt_tokens import generate_new_tokens, generate_new_tokens_from_user, verify_token
from ..models import User, FriendShip
from apps.game.models import LocalMatch
from backend.utils.leaderboard import get_leaderboard_cached
from backend.utils.conf_reg_utils import send_conf_reg
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator, EmailValidator
from backend.utils.mixins.custom_error_messages import FtErrorMessagesMixin
from backend.utils.ft_model_serializer import FtModelSerializer
from backend.utils import authentication
from django.core.exceptions import ValidationError
from apps.user.enums import Visibility
import os


class RegisterSerializer(FtErrorMessagesMixin, FtModelSerializer):
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
                "username": self.initial_data.get("username"),  # type: ignore
                "email": self.initial_data.get("email"),  # type: ignore
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


class UserRetrieveSerializer(FtModelSerializer):
    max_streak = serializers.IntegerField(source="statistics.max_streak", read_only=True)
    win_rate = serializers.IntegerField(source="statistics.win_rate", read_only=True)
    num_goals_scored = serializers.IntegerField(source="statistics.num_goals_scored", read_only=True)
    num_goals_against = serializers.IntegerField(source="statistics.num_goals_against", read_only=True)
    num_goals_stopped = serializers.IntegerField(source="statistics.num_goals_stopped", read_only=True)
    punctuation = serializers.IntegerField(source="statistics.punctuation", read_only=True)
    time_played = serializers.SerializerMethodField()
    position = serializers.IntegerField(read_only=True)
    is_friend = serializers.SerializerMethodField()
    has_requested_friendship = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_img",
            "banner",
            "is_connected",
            "max_streak",
            "win_rate",
            "time_played",
            "num_goals_scored",
            "num_goals_against",
            "num_goals_stopped",
            "punctuation",
            "position",
            "is_friend",
            "has_requested_friendship",
        )

    def get_time_played(self, obj):
        duration = obj.statistics.time_played
        total_seconds = duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

    def get_is_friend(self, obj):
        user = self.context["request"].user
        return FriendShip.objects.filter((Q(user=user, friend=obj) | Q(user=obj, friend=user)) & Q(accepted=True)).exists()

    def get_has_requested_friendship(self, obj):
        user = self.context["request"].user
        return FriendShip.objects.filter(user=user, friend=obj, accepted=False).exists()
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request_user = self.context["request"].user

        if request_user and request_user.id == instance.id:
            return representation

        if (
            instance.visibility == Visibility.ANONYMOUS.value or
            (instance.visibility == Visibility.PRIVATE.value and
            (request_user is None or not instance.friends.filter(id=request_user.id).exists()))
        ):
            representation["username"] = "Anonymous"
            representation["profile_img"] = None
            representation["banner"] = None
            representation["is_connected"] = False
            representation["max_streak"] = 0
            representation["win_rate"] = 0
            representation["time_played"] = "0h 0m"
            representation["num_goals_scored"] = 0
            representation["num_goals_against"] = 0
            representation["num_goals_stopped"] = 0
            representation["punctuation"] = 0
            representation["position"] = None

        return representation


class UserUpdateSerializer(FtErrorMessagesMixin, FtModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "profile_img",
            "banner",
            "visibility",
            "language",
            "two_factor_enabled",
        )
        ft_error_messages = {
            'username': {
                UniqueValidator: 'ERROR.USERNAME.ALREADY_EXISTS',
                RegexValidator: 'ERROR.USERNAME.INVALID',
            },
        }
    def update(self, instance, validated_data):
        if 'profile_img' in validated_data:
            old_profile_img = instance.profile_img
            if old_profile_img and os.path.isfile(old_profile_img.path):
                os.remove(old_profile_img.path)
        
        if 'banner' in validated_data:
            old_banner = instance.banner
            if old_banner and os.path.isfile(old_banner.path):
                os.remove(old_banner.path)

        return super().update(instance, validated_data)


class UserListSerializer(FtModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_img",
        )
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request_user = self.context.get('request').user if self.context.get('request') else None
        
        if request_user and request_user.id == instance.id:
            return representation

        if (
            instance.visibility == Visibility.ANONYMOUS.value or
            (instance.visibility == Visibility.PRIVATE.value and
            (request_user is None or not instance.friends.filter(id=request_user.id).exists()))
        ):
            representation["username"] = "Anonymous"
            representation["profile_img"] = None

        return representation


class UserSerializer(FtModelSerializer):
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
        user.is_connected = True
        user.save()
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
    # This refers to the refresh token
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
        if self.context["request"].user.is_authenticated:
            user_id = self.context["request"].user.id
        else:
            payload = verify_token(data["change_password_token"])
            if not payload.get("change_password"):
                raise serializers.ValidationError({"error": "ERROR.INVALID_TOKEN"})
            user_id = payload.get("user_id")
        new_password = data["new_password"]
        repeat_new_password = data["repeat_new_password"]
        if new_password != repeat_new_password:
            raise serializers.ValidationError({"error": "ERROR.PASSWORD.DONT_MATCH"})

        user = User.objects.get(id=user_id)
        try:
            authentication.validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"error": e.messages})
        return user


class OAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class MeNeedTokenSerializer(FtModelSerializer):
    is42 = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'profile_img',
            'two_factor_enabled',
            'banner',
            'visibility',
            'is_connected',
            'language',
            'is42',
        ]

    def get_is42(self, obj):
        return obj.id42 is not None


class FriendSerializer(serializers.ModelSerializer):
    friend_id = serializers.IntegerField(source='friend.id', write_only=True)

    class Meta:
        model = FriendShip
        fields = ['friend_id']

    def validate_friend_id(self, value):
        if self.context["request"].user.id == value:
            raise serializers.ValidationError({"error": "ERROR.FRIENDS.YOURSELF"})
        get_object_or_404(User, id=value)
        return value

    def validate(self, attrs):
        if FriendShip.objects.filter(user=self.context["request"].user, friend_id=attrs["friend"]["id"]).exists():
            raise serializers.ValidationError({"error": "ERROR.FRIENDS.FRIENDSHIP_EXISTS"})
        return {"friend_id": attrs["friend"]["id"]}

    def create(self, validated_data):
        friend = User.objects.get(id=validated_data["friend_id"])
        user = self.context["request"].user
        FriendShip.objects.get_or_create(user=user, friend=friend)
        return validated_data


class AcceptFriendSerializer(serializers.ModelSerializer):
    friend_id = serializers.IntegerField(source='friend.id', write_only=True)

    class Meta:
        model = FriendShip
        fields = ['friend_id']

    def validate(self, attrs):
        friend = attrs["friend"]["id"]
        user = self.context["request"].user

        friendship = FriendShip.objects.filter(user_id=friend, friend=user).first()
        if not friendship:
            raise serializers.ValidationError({"error": "ERROR.FRIENDS.FRIENDSHIP_NOT_FOUND"})
        if friendship.accepted:
            raise serializers.ValidationError({"error": "ERROR.FRIENDS.WAS_ACCEPTED"})
        return friendship


class MyRequestsFriendsSerializer(serializers.ModelSerializer):
    profile_img = serializers.FileField(source='user.profile_img', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = FriendShip
        fields = ['id', 'username', 'profile_img']


class CancelFriendRequestSerializer(serializers.ModelSerializer):
    friend_id = serializers.IntegerField(source='friend.id', write_only=True)

    class Meta:
        model = FriendShip
        fields = ['friend_id']

    def validate(self, attrs):
        friend = attrs["friend"]["id"]
        user = self.context["request"].user

        friendship = FriendShip.objects.filter(user=user, friend_id=friend, accepted=False).first()
        if not friendship:
            raise serializers.ValidationError({"error": "ERROR.FRIENDS.FRIENDSHIP_NOT_FOUND"})
        return friendship

    def delete(self):
        self.validated_data.delete()
        return self.validated_data


class LeaderboardSerializer(FtModelSerializer):
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
        top_users = get_leaderboard_cached()
        return LeaderboardSerializer(top_users, many=True, context=self.context).data


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
    user_b = serializers.CharField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    num_goals_scored = serializers.IntegerField(read_only=True)
    num_goals_against = serializers.IntegerField(read_only=True)
    num_goals_stopped_a = serializers.IntegerField(read_only=True)
    num_goals_stopped_b = serializers.IntegerField(read_only=True)
    time_played = serializers.SerializerMethodField()

    class Meta:
        model = LocalMatch
        fields = (
            'user_b',
            'start_date',
            'num_goals_scored',
            'num_goals_against',
            'num_goals_stopped_a',
            'num_goals_stopped_b',
            'time_played',
        )

    def get_time_played(self, obj):
        total_seconds = int(obj.time_played.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02}:{seconds:02}"
