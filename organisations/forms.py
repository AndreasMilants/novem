from .models import Organisation, OrganisationUserLink, SectionUserLink, Section
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import lazy
from django.forms.models import ModelChoiceIterator


class OrganisationCreateForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = Organisation
        fields = ('name', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        org = super(OrganisationCreateForm, self).save(commit=False)
        org.set_password(self.cleaned_data["password1"])
        if commit:
            org.save()
        return org


class OrganisationChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = Organisation
        fields = ['name', 'password', 'is_active']

    def __init__(self, *args, **kwargs):
        super(OrganisationChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class OrganisationAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Organisation.objects.filter(is_active=True)
        iterator = ModelChoiceIterator(field=self.fields['organisation'])
        iterator.queryset = queryset
        self.fields['organisation'].choices = iterator

    class Meta:
        model = OrganisationUserLink
        fields = ['organisation', 'password']

    error_messages = {
        'invalid_login': _("Please enter a correct organisation and password. "
                           "Note that both fields are case-sensitive."),
        'inactive': _("This account is inactive."),
    }

    def clean(self):
        organisation = self.cleaned_data.get('organisation')
        password = self.cleaned_data.get('password')
        if not organisation:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'organisation': 'organisation'},
            )
        try:
            if organisation and password:
                organisation_cache = Organisation.objects.get(name=organisation)
                if not organisation_cache or not organisation_cache.check_password(password):
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        # params={'organisation': 'organisation'},
                    )
                else:
                    self.confirm_registration_with_organisation_allowed(organisation_cache)
            if not organisation.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='invalid_login',
                    params={'organisation': 'organisation'},
                )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'organisation': 'organisation'},
            )

        return self.cleaned_data

    def is_valid(self):
        return super().is_valid()

    def confirm_registration_with_organisation_allowed(self, organisation):
        """
        Controls whether the organisation accepts new registrations. This is a policy setting,
        independent of authentication.
        """
        if not organisation.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class ChooseSectionForm(forms.Form):
    class Meta:
        model = SectionUserLink
        fields = ['section']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        organisation = Organisation.objects.get(organisationuserlink__user=user)

        # This query selects all sections without children that are linked to this organisation
        choices = [(section.id, section.name) for section in
                   Section.objects.raw('WITH RECURSIVE section_tree(id, name, parent_section_id, organisation_id) AS ('
                                       '    SELECT id, name, parent_section_id, organisation_id '
                                       '    FROM organisations_section '
                                       '    WHERE organisation_id = %s '
                                       'UNION ALL '
                                       '    SELECT ss.id, ss.name, ss.parent_section_id, ss.organisation_id '
                                       '    FROM organisations_section AS ss INNER JOIN section_tree AS '
                                       '    st ON (ss.parent_section_id = st.id)'
                                       ') '
                                       'SELECT st.id, st.name, st.organisation_id, st.parent_section_id '
                                       'FROM section_tree as st LEFT OUTER JOIN '
                                       'organisations_section s ON(st.id = s.parent_section_id) '
                                       'WHERE s.id is null', [organisation.id])]

        self.fields['section'] = forms.ChoiceField(choices=choices)

    def save(self, commit=True):
        model = SectionUserLink(section_id=self.cleaned_data['section'], user=self.user)
        if commit:
            model.save()
        return model


class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    required_css_class = 'required'
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user

    def _get_changed_data(self):
        data = super(AdminPasswordChangeForm, self).changed_data
        for name in self.fields.keys():
            if name not in data:
                return []
        return ['password']

    changed_data = property(_get_changed_data)
