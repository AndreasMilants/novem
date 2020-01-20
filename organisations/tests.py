from django.test import TestCase
from .forms import OrganisationCreateForm, OrganisationAuthenticationForm, ChooseSectionForm
from .models import Section, SectionUserLink, Organisation


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

    def test_cannot_link_to_nonexistent_organisation(self):
        self.assertFalse(
            OrganisationAuthenticationForm(data={'organisation': 'nonexistent', 'password': 'pass'}).is_valid())


class ChooseSectionFormTests(TestCase):
    def setUp(self):
        self.org = Organisation(name='test', password='test123')
        self.org.save()
        section = Section(name='level0', organisation=self.org)
        section.save()
        for i in range(1, 4):
            section = Section(name='level{}'.format(i), parent_section=section)
            section.save()

    def test_gives_only_bottom_most_sections_of_tree(self):
        form = ChooseSectionForm(organisation=self.org)
        self.assertEquals(1, len(form.fields['section'].choices))
        self.assertEquals('level3', form.fields['section'].choices[0][1])

    # Cannot check creation because this uses a raw query

# TODO should check the linktosection view because this does not use the default form behaviour
