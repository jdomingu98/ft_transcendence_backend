from typing import Any

from rest_framework import status
from rest_framework.test import APITestCase

from apps.user.models import User
from .utils import generate_user_mock


class RegisterViewTest(APITestCase):
    REGISTER_ENDPOINT = "/api/v1/user/"
    response: Any

    def test_register_user(self):
        data = generate_user_mock("testuser", "testuser@example.com", "testpassword123", "testpassword123")
        self.when_user_is_registered(data)
        self.should_return_202()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")

    def test_register_user_passwords_do_not_match(self):
        data = generate_user_mock("testuser", "testuser@example.com", "testpassword123", "wrongpassword")
        self.when_user_is_registered(data)
        self.should_return_400()
        self.assertIn("ERROR.PASSWORD.DONT_MATCH", str(self.response.data))

    def test_register_user_missing_field(self):
        data = {
            "username": "testuser",
        }
        self.when_user_is_registered(data)
        self.should_return_400()
        self.assertIn("email", self.response.data)
        self.assertIn("password", self.response.data)
        self.assertIn("repeat_password", self.response.data)

    def test_register_user_invalid_email(self):
        data = generate_user_mock("testuser", "invalid-email", "my'secure'password", "my'secure'password")
        self.when_user_is_registered(data)
        self.should_return_400()
        self.should_contain_field_error("email", "ERROR.EMAIL.INVALID")

    def test_unique_username(self):
        data = generate_user_mock("testuser", "email1@test.com", "my'secure'password", "my'secure'password")
        self.when_user_is_registered(data)
        data2 = generate_user_mock("testuser", "email2@test.com", "my'secure'password", "my'secure'password")
        self.when_user_is_registered(data2)
        self.should_return_400()
        self.should_contain_field_error("username", "ERROR.USERNAME.ALREADY_EXISTS")

    def test_unique_email(self):
        data = generate_user_mock("testuser", "sameemail@test.com", "my'secure'password", "my'secure'password")
        self.when_user_is_registered(data)
        data2 = generate_user_mock("testuser2", "sameemail@test.com", "my'secure'password", "my'secure'password")
        self.when_user_is_registered(data2)
        self.should_return_400()
        self.should_contain_field_error("email", "ERROR.EMAIL.ALREADY_EXISTS")

    def when_user_is_registered(self, data):
        self.response = self.client.post(self.REGISTER_ENDPOINT, data, format="json")

    def should_return_400(self):
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def should_return_202(self):
        self.assertEqual(self.response.status_code, status.HTTP_202_ACCEPTED)

    def should_contain_field_error(self, field, error):
        self.assertIn(field, self.response.data)
        self.assertIn(error, self.response.data[field])
