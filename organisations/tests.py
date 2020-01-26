from django.test import TestCase
from .forms import OrganisationCreateForm, OrganisationAuthenticationForm, ChooseSectionForm
from .models import Section, Organisation, OrganisationUserLink
from django.contrib.auth import get_user_model
User = get_user_model()


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


class OrganisationAuthenticationFormTests(TestCase):
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
        self.user = User.objects.create_user('test@novem.be', 'thisisatestpass')
        org = Organisation(name='test', password='test123')
        org.save()
        org2 = Organisation(name='test2', password='test123')
        org2.save()

        link = OrganisationUserLink(user=self.user, organisation=org)
        link.save()

        self.section = Section(name='level0', organisation=org)
        self.section.save()
        for i in range(1, 4):
            self.section = Section(name='level{}'.format(i), parent_section=self.section)
            self.section.save()

        self.other_section = Section(name='other', organisation=org2)
        self.other_section.save()

    def test_gives_only_bottom_most_sections_of_tree(self):
        form = ChooseSectionForm(user=self.user)
        self.assertEquals(1, len(form.fields['section'].choices))
        self.assertEquals('level3', form.fields['section'].choices[0][1])

    def test_can_not_link_to_section_not_in_org(self):
        form = ChooseSectionForm(user=self.user, data={'section': self.other_section.id})
        self.assertFalse(form.is_valid())

    def test_can_link_to_section_in_org(self):
        form = ChooseSectionForm(user=self.user, data={'section': self.section.id})
        self.assertTrue(form.is_valid())

    def test_save(self):
        form = ChooseSectionForm(user=self.user, data={'section': self.section.id})
        if form.is_valid():
            model = form.save()
            self.assertEqual(model.user, self.user)
            self.assertEqual(model.section, self.section)
        else:
            raise Exception('Form should be valid')
