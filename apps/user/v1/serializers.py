from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

from backend.utils.jwt_tokens import generate_new_tokens_from_user, generate_new_tokens
from ..models import User, RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'language',
            'visibility',
            'profile_img',
            'banner',
            'repeat_password',
            'access_token',
            'refresh_token',
        )

    def create(self, validated_data):
        validated_data.pop('repeat_password', None)
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        access_token, refresh_token = generate_new_tokens_from_user(instance.id, instance.email)
        representation['access_token'] = access_token
        representation['refresh_token'] = refresh_token
        return representation

    def validate(self, data):
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid username/password.")
        return user

    def to_representation(self, instance):
        access_token, refresh_token = generate_new_tokens_from_user(instance.id,instance.email)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

class PasswordResetSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()

class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        access_token, refresh_token = generate_new_tokens(instance['token'])
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

class logoutSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate(self, data):
        token = data['token']
        try:
            refresh_token = RefreshToken.objects.get(token=token)
            data['user'] = refresh_token.user
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")
        return data