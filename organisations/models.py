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
    """
    We use an extra table, so that in the future users can be linked to multiple organisations
    -> At this moment we don't want that, so we set user to unique
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, verbose_name=_('organisation'),
                                related_name='organisationuserlink')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                     verbose_name=_('organisation'))

    class Meta:
        verbose_name = _('User-organisation-link')
        verbose_name_plural = _('User-organisation-links')

    def __str__(self):
        return '{user} - {organisation}'.format(user=str(self.user), organisation=str(self.organisation))


class SectionManager(models.Manager):
    def get_sections_admin(self, user):
        return list(self.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id, name, organisation_id) AS ( '
                             '   SELECT 1 AS depth, s.id, s.parent_section_id, s.name, organisation_id '
                             '   FROM organisations_section s INNER JOIN organisations_sectionadministrator a '
                             '   ON (s.id = a.section_id) '
                             '   WHERE a.user_id = %s '
                             'UNION ALL '
                             '   SELECT depth + 1, ss.id, ss.parent_section_id, ss.name, ss.organisation_id '
                             '   FROM organisations_section ss INNER JOIN section_tree st '
                             '   ON (ss.parent_section_id = st.id)'
                             ') '
                             'SELECT id, parent_section_id, name, organisation_id '
                             'FROM section_tree '
                             'ORDER BY depth', [user.id]))

    def get_all_parents_line(self, section_id):
        # Returns a list of parents recursively
        return list(self.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id, name, organisation_id) AS ( '
                             '   SELECT 1 AS depth, s.id, s.parent_section_id, s.name, organisation_id '
                             '   FROM organisations_section s '
                             '   WHERE s.id = %s '
                             'UNION ALL '
                             '   SELECT depth + 1, ss.id, ss.parent_section_id, ss.name, ss.organisation_id '
                             '   FROM organisations_section ss INNER JOIN section_tree st '
                             '   ON (ss.id = st.parent_section_id)'
                             ') '
                             'SELECT id, parent_section_id, name, organisation_id '
                             'FROM section_tree '
                             'ORDER BY depth DESC', [section_id]))

    def get_all_children(self, section_id):
        # Returns a list with the entire tree of children
        return list(
            self.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id, name, organisation_id) AS ('
                     '    SELECT 1 AS depth, s.id, s.parent_section_id, s.name, organisation_id '
                     '    FROM organisations_section s '
                     '    WHERE s.id = %s '
                     'UNION ALL '
                     '    SELECT  depth + 1, ss.id, ss.parent_section_id, ss.name, ss.organisation_id '
                     '    FROM organisations_section ss INNER JOIN section_tree st '
                     '    ON (ss.parent_section_id = st.id)'
                     ') '
                     'SELECT id, parent_section_id, name, organisation_id  '
                     'FROM section_tree '
                     'ORDER BY depth', [section_id]))

    def get_entire_line(self, section_id):
        return self.get_all_parents_line(section_id) + self.get_all_children(section_id)

    def get_entire_tree(self, section_id):
        # Returns a list of all sections in the tree, starting at organisation level
        # Note that these sections are not all linked if there are multiple sections directly linked to an organisation
        return list(self.raw('WITH RECURSIVE section_tree(depth, id, parent_section_section_id, name) AS ('
                             '    SELECT 1 AS depth, s.id, s.parent_section_id, s.name '
                             '    FROM organisations_section s '
                             '    WHERE s.organisation_id = ('
                             '        WITH RECURSIVE section_tree_2(id, parent_section_id, name)'
                             '        AS ('
                             '            SELECT s.id, s.parent_section_id, s.name '
                             '            FROM organisations_section s '
                             '            WHERE s.id = %s '
                             '        UNION ALL '
                             '            SELECT ss.id, ss.parent_section_id, ss.name'
                             '            FROM organisations_section ss INNER JOIN section_tree_2 st2 '
                             '            ON (ss.id = st2.parent_section_id) '
                             ') '
                             'SELECT organisation_id '
                             'FROM section_tree_2 '
                             'WHERE organisation_id IS NOT NULL'
                             ') '
                             'UNION ALL '
                             '    SELECT  depth + 1, ss.id, ss.parent_section_id, ss.name '
                             '    FROM organisations_section ss INNER JOIN section_tree st '
                             '    ON (ss.parent_section_id = st.id)'
                             ') '
                             'SELECT * '
                             'FROM section_tree '
                             'ORDER BY depth', [section_id]))


class Section(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=63, verbose_name=_('Name'))
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.CASCADE,
                                     verbose_name=_('organisation'))
    parent_section = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                       verbose_name=_('parent_section'),
                                       related_name='child_section')

    objects = SectionManager()

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')

    def __str__(self):
        return '{} - {}'.format(str(self.organisation) if self.organisation else str(self.parent_section),
                                str(self.name))


class SectionUserLink(models.Model):
    """
    We use an extra table, so that in the future users can be linked to multiple organisations
    -> so also multiple sections
    At the moment we turned this functionality off though, so we set user to unique
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, verbose_name=_('user'),
                                related_name='sectionuserlink')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_('section'))

    class Meta:
        verbose_name = _('Section-user-link')
        verbose_name_plural = _('Section-user-links')

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.section))


class SectionAdministrator(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('user'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_('section'))

    class Meta:
        verbose_name = _('Section Administrator')
        verbose_name_plural = _('Section Administrators')

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.section))
