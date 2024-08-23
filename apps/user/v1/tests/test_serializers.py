from typing import cast

from django.test import TestCase

from apps.user.enums import Language, Visibility
from apps.user.models import User
from apps.user.v1.serializers import RegisterSerializer

from .utils import generate_user_mock


class RegisterSerializerTest(TestCase):

    def test_valid_registration(self):
        user = generate_user_mock("testuser", "testuser@example.com", "testpassword123", "testpassword123")
        data = {
            **user,
            "language": Language.SPANISH.value,
            "visibility": Visibility.PUBLIC.value,
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_passwords_do_not_match(self):
        data = generate_user_mock("testuser", "testuser@example.com", "testpassword123", "wrongpassword")
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Passwords do not match", str(serializer.errors))

    def test_create_user(self):
        data = generate_user_mock("testuser", "testuser@example.com", "testpassword123", "testpassword123")
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = cast(User, serializer.save())
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testpassword123"))
