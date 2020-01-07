from django.contrib.auth import password_validation
from django.db import models
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string, salted_hmac


class Organisation(models.Model):
    name = models.CharField(unique=True, blank=False, db_index=True, max_length=255)
    password = models.CharField(_('password'), max_length=128)
    is_active = models.BooleanField(default=True, blank=False)

    _password = None

    def check_password(self, raw_password):
        """
        Code copied from official user model django
        """

        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field.
        """
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def __str__(self):
        return self.name
