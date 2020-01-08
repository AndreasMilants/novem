from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OrganisationsConfig(AppConfig):
    name = 'organisations'
    verbose_name = _('Organisations')
