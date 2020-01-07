from django.test import TestCase
from django.contrib.auth import get_user_model


# Create your tests here.

class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        email_address = 'test@gmail.com'
        password = 'test123'
        user = User.objects.create_user(
            email=email_address,
            password=password,
        )
        self.assertEqual(user.email, email_address)
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        email_address = 'super@gmail.com'
        password = 'test123'
        admin_user = User.objects.create_superuser(
            email=email_address,
            password=password,
        )
        self.assertEqual(admin_user.email, email_address)
        self.assertNotEqual(admin_user.password, password)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
