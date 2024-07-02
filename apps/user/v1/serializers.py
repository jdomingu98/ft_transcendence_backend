from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from ..models import User

class RegisterSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)

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
        )

    def create(self, validated_data):
        validated_data.pop('repeat_password', None)
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)

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