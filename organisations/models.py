from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import ugettext_lazy as _


class OrganisationManager(models.Manager):
    def create(self, name, password):
        org = self.model(name=name, password=make_password(password))
        org.save()
        return org


class Organisation(models.Model):
    name = models.CharField(unique=True, blank=False, db_index=True, max_length=255)
    password = models.CharField(_('password'), max_length=128)
    objects = OrganisationManager()

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)
