from .models import Organisation
from django import forms


class OrganisationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Organisation
