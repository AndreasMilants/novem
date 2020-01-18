from django.test import TestCase
from .forms import OrganisationCreateForm, OrganisationAuthenticationForm


class OrganisationTests(TestCase):
    @staticmethod
    def save_form_throws_value_error(form):
        try:
            form.save()
        except ValueError:
            return True
        return False

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

    def test_empty_name_gives_error(self):
        passw = 'test123'
        form = OrganisationCreateForm(data={'name': '', 'password1': passw, 'password2': passw})
        self.assertTrue(self.save_form_throws_value_error(form))

    def test_non_matching_passwords_give_error(self):
        form = OrganisationCreateForm(
            data={'name': 'test', 'password1': 'this_is_a_pass', 'password2': 'this_is_another_one'})
        self.assertTrue(self.save_form_throws_value_error(form))


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


class OrganisationAuthenticationTests(TestCase):
    def setUp(self):
        self.passw = 'pass'
        self.org = OrganisationCreateForm(
            data={'name': 'test', 'password1': self.passw, 'password2': self.passw}).save()

    def test_login_correct(self):
        form = OrganisationAuthenticationForm(data={'organisation': self.org.id, 'password': self.passw})
        self.assertTrue(form.is_valid())

    def test_login_with_wrong_credentials_fails(self):
        form = OrganisationAuthenticationForm(data={'organisation': self.org.id, 'password': 'wrong'})
        self.assertFalse(form.is_valid())

    def test_login_with_inactive_organisation_fails(self):
        self.org.is_active = False
        self.org.save()
        form = OrganisationAuthenticationForm(data={'organisation': self.org.id, 'password': self.passw})
        self.assertFalse(form.is_valid())
        self.org.is_active = True
        self.org.save()


# TODO choosesectionform (important: gives correct options)
