from django.test import TestCase
from .forms import OrganisationCreateForm, OrganisationAuthenticationForm


class OrganisationTests(TestCase):
    def test_create(self):
        name = 'test_org'
        password = 'test123'
        form_data = {'name': name, 'password1': password, 'password2': password}
        form = OrganisationCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        model = form.save(commit=False)
        self.assertEqual(model.name, name)

    def test_check_password_after_creation(self):
        name = 'test_org_2'
        password = 'test123'
        form_data = {'name': name, 'password1': password, 'password2': password}
        form = OrganisationCreateForm(data=form_data)
        model = form.save(commit=False)
        self.assertTrue(model.check_password(password))


class LinkToOrganisationTests(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.org_name = 'test_org'
        self.password = 'test123'

    def setUp(self):
        form_data = {'name': self.org_name, 'password1': self.password, 'password2': self.password}
        form = OrganisationCreateForm(data=form_data)
        org = form.save()
        self.org = org.id

    @staticmethod
    def check_pass(org, password):
        auth_data = {'organisation': org, 'password': password}
        auth = OrganisationAuthenticationForm(data=auth_data)
        return auth.is_valid()

    def test_correct_pass(self):
        self.assertTrue(self.check_pass(self.org, self.password))

    def test_wrong_pass(self):
        self.assertFalse(self.check_pass(self.org, ''))
        self.assertFalse(self.check_pass(self.org, 'wrongpass'))
        self.assertFalse(self.check_pass(self.org, 'Test123'))  # Check case sensitivity

    def test_cannot_link_to_nonexistent_organisation(self):
        self.assertFalse(self.check_pass('nonexistent', self.password))
