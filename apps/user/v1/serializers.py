from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ..models import User

class RegisterSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(max_length=255)

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