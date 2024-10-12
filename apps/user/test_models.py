from django.test import TestCase
from datetime import timedelta
from apps.user.models import User
from .enums import Language, Visibility
from django.core.exceptions import ValidationError
from apps.game.models import Statistics

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

    def test_statistics_time_played(self):
        user = User.objects.get(id=1)
        statistics = user.statistics
        self.assertEqual(statistics.time_played, timedelta(0))

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
                    id42="lacasualidad",
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
                    id42="lacasualidad",
                )
                with self.assertRaises(ValidationError):
                    user.full_clean()  # This should raise ValidationError

class StatisticsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user1", email="user1@example.com")
        cls.user2 = User.objects.create(username="user2", email="user2@example.com")
        cls.user3 = User.objects.create(username="user3", email="user3@example.com")
        cls.user4 = User.objects.create(username="user4", email="user4@example.com")
        cls.user5 = User.objects.create(username="user5", email="user5@example.com")

        cls.stats1 = Statistics.objects.get(user=cls.user1)
        cls.stats1.punctuation = 50
        cls.stats1.save()

        cls.stats2 = Statistics.objects.get(user=cls.user2)
        cls.stats2.punctuation = 100
        cls.stats2.save()

        cls.stats3 = Statistics.objects.get(user=cls.user3)
        cls.stats3.punctuation = 75
        cls.stats3.save()

        cls.stats4 = Statistics.objects.get(user=cls.user4)
        cls.stats4.punctuation = 85
        cls.stats4.save()

        cls.stats5 = Statistics.objects.get(user=cls.user5)
        cls.stats5.punctuation = 85
        cls.stats5.save()

    def test_statistics_creation(self):
        """Verificar que se crean las estadísticas para los usuarios."""
        stats1 = Statistics.objects.get(user=self.user1)
        stats2 = Statistics.objects.get(user=self.user2)
        stats3 = Statistics.objects.get(user=self.user3)

        self.assertEqual(stats1.punctuation, 50)
        self.assertEqual(stats2.punctuation, 100)
        self.assertEqual(stats3.punctuation, 75)

    def test_ordering_with_same_punctuation(self):
        """Verificar que las estadísticas se ordenan correctamente por puntuación y nombre de usuario."""
        ordered_stats = Statistics.objects.all().order_by('-punctuation', 'user__username')

        self.assertEqual(ordered_stats[0].user, self.user2)  # user2 tiene la mayor puntuación
        self.assertEqual(ordered_stats[1].user, self.user4)  # user4 y user5 tienen la misma puntuación
        self.assertEqual(ordered_stats[2].user, self.user5)  # user5 debería ir después de user4
        self.assertEqual(ordered_stats[3].user, self.user3)  # user3 tiene la siguiente puntuación
        self.assertEqual(ordered_stats[4].user, self.user1)  # user1 tiene la menor puntuación
