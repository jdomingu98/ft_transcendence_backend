from django.test import TestCase
from typing import cast
from apps.user.models import User
from apps.user.enums import Visibility, Language
from apps.user.v1.serializers import RegisterSerializer

class RegisterSerializerTest(TestCase):

    def test_valid_registration(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'repeat_password': 'testpassword123',
            'language': Language.SPANISH.value,
            'visibility': Visibility.PUBLIC.value
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_passwords_do_not_match(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'repeat_password': 'wrongpassword',
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Passwords do not match', str(serializer.errors))

    def test_create_user(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'repeat_password': 'testpassword123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = cast(User, serializer.save())
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpassword123'))
