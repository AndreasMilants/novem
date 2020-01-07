from django.test import TestCase
from .models import Organisation


class OrganisationTests(TestCase):
    def test_create_organisation(self):
        name = 'test_org'
        password = 'test123'
        org = Organisation.objects.create(
            name=name,
            password=password,
        )
        self.assertEqual(org.name, name)
        self.assertNotEqual(org.password, password)

    def test_check_password(self):
        name = 'test_org_2'
        password = 'test123'
        org = Organisation.objects.create(
            name=name,
            password=password,
        )
        self.assertTrue(org.check_password(password))
        self.assertFalse(org.check_password('test12'))
