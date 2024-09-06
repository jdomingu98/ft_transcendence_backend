from django.test import TestCase

from apps.user.models import User

from .enums import Language, Visibility

from django.core.exceptions import ValidationError


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User(
            id=1,
            username="testuser",
            email="testuser@example.com",
        )
        user.set_password("testpassword123")
        user.save()

    def test_create_user(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("testpassword123"))

    def test_default_visibility(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.visibility, Visibility.PUBLIC.value)

    def test_default_language(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.language, Language.SPANISH.value)

    def test_default_is_connected(self):
        user = User.objects.get(id=1)
        self.assertTrue(user.is_connected)


class UserModelEmailTest(TestCase):

    def setUp(self):
        self.valid_emails = [
            "user@example.com",
            "user@mail.example.com",
            "user@gmail.com",
            "user@outlook.com",
            "user@hotmail.com",
            "user@42.fr",
        ]
        self.invalid_emails = [
            "userexample.com",  # Missing @
            "user@examplecom",  # Missing .xxx
            "user@.com",  # Missing domain name
            "@example.com",  # Missing local part
            "user@com",  # Missing domain part
            "user@.com",  # Missing domain name
            "user@com.",  # Trailing dot
            "user@-example.com",  # Invalid domain name
        ]

    def test_valid_emails(self):
        for email in self.valid_emails:
            with self.subTest(email=email):
                user = User(
                    username="testuser",
                    email=email,
                    password="testpassword123",
                    profile_img="default.jpg",
                    banner="default_banner.jpg",
                )
                try:
                    user.full_clean()  # This will call the validators
                except ValidationError:
                    self.fail(f"Valid email '{email}' raised ValidationError")

    def test_invalid_emails(self):
        for email in self.invalid_emails:
            with self.subTest(email=email):
                user = User(
                    username="testuser",
                    email=email,
                    password="testpassword123",
                    profile_img="default.jpg",
                    banner="default_banner.jpg",
                )
                with self.assertRaises(ValidationError):
                    user.full_clean()  # This should raise ValidationError
