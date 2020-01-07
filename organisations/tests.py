from django.test import TestCase
from .models import Organisation
from .forms import OrganisationCreateForm


class OrganisationTests(TestCase):
    def test_create(self):
        name = 'test_org'
        password = 'test123'
        form_data = {'name': name, 'password1': password, 'password2': password}
        form = OrganisationCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_check_password_after_creation(self):
        name = 'test_org_2'
        password = 'test123'
        form_data = {'name': name, 'password1': password, 'password2': password}
        form = OrganisationCreateForm(data=form_data)
        model = form.save(commit=False)
        self.assertTrue(model.check_password(password))
