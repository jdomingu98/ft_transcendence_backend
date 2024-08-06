from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

from backend.utils.jwt_tokens import generate_new_tokens_from_user
from ..models import User

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
        user = User.objects.create(**validated_data)

        access_token, refresh_token = generate_new_tokens_from_user(user.id, user.email)
        self.context['access_token'] = access_token
        self.context['refresh_token'] = refresh_token

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['access_token'] = self.context.get('access_token')
        representation['refresh_token'] = self.context.get('refresh_token')
        return representation

    def validate(self, data):
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid username/password.")
        return user

class PasswordResetSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()

class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField()