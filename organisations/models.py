from django.contrib.auth import password_validation
from django.db import models
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import salted_hmac
from django.contrib.auth import get_user_model
import uuid


class Organisation(models.Model):
    name = models.CharField(_('name'), unique=True, blank=False, db_index=True, max_length=255)
    password = models.CharField(_('password'), max_length=128)
    is_active = models.BooleanField(_('is active'), default=True, blank=False,
                                    help_text=_('Users can register with this organisation'))

    _password = None

    class Meta:
        verbose_name = _('Organisation')
        verbose_name_plural = _('Organisations')

    def check_password(self, raw_password):
        """
        Only checks the password. Does not check whether the organisation is active
        """

        def setter(password):
            self.set_password(password)
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


class OrganisationUserLink(models.Model):
    """We use an extra table, so that in the future users can be linked to multiple organisations"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('organisation'))
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                     verbose_name=_('organisation'))

    class Meta:
        verbose_name = _('User-organisation-link')
        verbose_name_plural = _('User-organisation-links')

    def __str__(self):
        return '{user} - {organisation}'.format(user=str(self.user), organisation=str(self.organisation))


class Section(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4(), unique=True)
    name = models.CharField(max_length=63)
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.CASCADE,
                                     verbose_name=_('organisation'))
    parent_section = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                       verbose_name=_('parent_section'),
                                       related_name='child_section')
    parent_section_uuid = models.ForeignKey('self', on_delete=models.CASCADE, related_name='cbase_uuid',
                                            to_field='uuid', blank=True, null=True)

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')

    def __str__(self):
        return '{} - {}'.format(str(self.organisation) if self.organisation else str(self.parent_section),
                                str(self.name))


class SectionUserLink(models.Model):
    """We use an extra table, so that in the future users can be linked to multiple organisations"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('user'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_('section'))
    section_uuid = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='bbase_uuid', to_field='uuid',
                                     blank=True, null=True)

    class Meta:
        verbose_name = _('Section-user-link')
        verbose_name_plural = _('Section-user-links')

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.section))


class SectionAdministrator(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('user'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_('section'))
    section_uuid = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='nbase_uuid', to_field='uuid',
                                     blank=True, null=True)

    class Meta:
        verbose_name = _('Section Administrator')
        verbose_name_plural = _('Section Administrators')

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.section))
