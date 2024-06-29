from rest_framework.test import APITestCase
from rest_framework import status
from apps.user.models import User
from typing import Any


class RegisterViewTest(APITestCase):
    REGISTER_ENDPOINT = '/api/v1/user/register/'
    response: Any

    def test_register_user(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'repeat_password': 'testpassword123',
        }
        self.when_user_is_registered(data)
        self.should_return_201()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_register_user_passwords_do_not_match(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'repeat_password': 'wrongpassword',
        }
        self.when_user_is_registered(data)
        self.should_return_400()
        self.assertIn('Passwords do not match', str(self.response.data))

    def test_register_user_missing_field(self):
        data = {
            'username': 'testuser',
        }
        self.when_user_is_registered(data)
        self.should_return_400()
        self.assertIn('email', self.response.data)
        self.assertIn('password', self.response.data)
        self.assertIn('repeat_password', self.response.data)

    def test_register_user_invalid_email(self):
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'testpassword',
            'repeat_password': 'testpassword',
        }
        self.when_user_is_registered(data)
        self.should_return_400()
        self.should_contain_field_error('email', 'Enter a valid email address.')

    def test_unique_username(self):
        data = {
            'username': 'testuser',
            'email': 'email1@test.com',
            'password': 'testpassword',
            'repeat_password': 'testpassword',
        }
        self.when_user_is_registered(data)
        data2 = {
            'username': 'testuser',
            'email': 'email2@test.com',
            'password': 'testpassword',
            'repeat_password': 'testpassword',
        }
        self.when_user_is_registered(data2)
        self.should_return_400()
        self.should_contain_field_error('username', 'user with this username already exists.')
    
    def test_unique_email(self):
        data = {
            'username': 'testuser',
            'email': 'sameemail@test.com',
            'password': 'testpassword',
            'repeat_password': 'testpassword',
        }
        self.when_user_is_registered(data)
        data2 = {
            'username': 'testuser2',
            'email': 'sameemail@test.com',
            'password': 'testpassword',
            'repeat_password': 'testpassword',
        }
        self.when_user_is_registered(data2)
        self.should_return_400()
        self.should_contain_field_error('email', 'user with this email already exists.')
        
    def when_user_is_registered(self, data):
        self.response = self.client.post(self.REGISTER_ENDPOINT, data, format='json')

    def should_return_400(self):
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def should_return_201(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def should_contain_field_error(self, field, error):
        self.assertIn(field, self.response.data)
        self.assertIn(error, self.response.data[field])
        