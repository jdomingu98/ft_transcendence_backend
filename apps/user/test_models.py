from django.test import TestCase
from apps.user.models import User
from .enums import Visibility, Language


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User(
            id=1,
            username='testuser',
            email='testuser@example.com',
        )
        user.set_password('testpassword123')
        user.save()

    def test_create_user(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpassword123'))

    def test_default_visibility(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.visibility, Visibility.PUBLIC.value)

    def test_default_language(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.language, Language.SPANISH.value)

    def test_default_is_connected(self):
        user = User.objects.get(id=1)
        self.assertTrue(user.is_connected)
