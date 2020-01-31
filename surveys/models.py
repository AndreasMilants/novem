from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from organisations.models import Section, SectionUserLink
from django.db.models import Avg
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

LEVEL_CHOICES = (
    (1, _('Power')),
    (2, _('Flexibility')),
    (3, _('Adventure')),
    (4, _('Vision')),
    (5, _('Empathy')),
    (6, _('Trust')),
    (7, _('Rest')),
    (8, _('Authenticity')),
    (9, _('Research')),
)


class SurveyManager(models.Manager):
    def get_personal_survey(self, user):
        surveys = list(self.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id) AS ( '
                                '   SELECT 1 AS depth, s.id, s.parent_section_id '
                                '   FROM organisations_section s INNER JOIN organisations_sectionuserlink l '
                                '   ON (s.id = l.section_id) '
                                '   WHERE l.user_id = %s '
                                'UNION ALL '
                                '   SELECT depth + 1, ss.id, ss.parent_section_id '
                                '   FROM organisations_section ss INNER JOIN section_tree st '
                                '   ON (ss.id = st.parent_section_id)'
                                ') '
                                'SELECT su.id, su.name, su.slug '
                                'FROM section_tree s INNER JOIN surveys_surveysectionlink l ON (s.id = l.section_id) '
                                'INNER JOIN surveys_survey su ON (l.survey_id = su.id) '
                                'ORDER BY depth DESC', [user.id]))
        if len(surveys) > 0:
            return surveys[0]
        return None


class Survey(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('name'))
    slug = models.SlugField()

    objects = SurveyManager()

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Question(models.Model):
    level = models.IntegerField(verbose_name=_('level'), choices=LEVEL_CHOICES)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('survey'))
    question = models.TextField(verbose_name=_('question'))

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return self.question


class SurveyInstance(models.Model):
    """This is only created when the survey is completed! So when ImportantLevelAnswer have been sent as well"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Survey Answers')
        verbose_name_plural = _('Survey Answers')

    def __str__(self):
        return '{} - {}'.format(_('Survey'), str(self.user))


class Answer(models.Model):
    question = models.ForeignKey(Question, verbose_name=_('Question'),
                                 on_delete=models.CASCADE)  # Answers are doubly linked to a survey this way
    answer = models.IntegerField(default=0, verbose_name=_('Answer'),
                                 validators=[
                                     MaxValueValidator(50),
                                     MinValueValidator(-50)
                                 ])
    user = models.ForeignKey(get_user_model(), verbose_name=_('User'),
                             on_delete=models.CASCADE)  # This is used as long as the survey is not completed.
    # A survey instance is only created when the survey is completed!
    survey_instance = models.ForeignKey(SurveyInstance, null=True, blank=True, verbose_name=_('Survey Instance'),
                                        on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        unique_together = ('question', 'user',)

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.question))


class ImportantLevelAnswer(models.Model):
    THREE_CHOICES = ((1, 1), (2, 2), (3, 3))
    survey_instance = models.ForeignKey(SurveyInstance, null=False, verbose_name=_('Survey Instance'),
                                        on_delete=models.CASCADE)
    level = models.IntegerField(verbose_name=_('level'), choices=LEVEL_CHOICES, blank=False, null=False)

    class Meta:
        unique_together = ('survey_instance', 'level')
        verbose_name = _('Important Level Answer')
        verbose_name_plural = _('Important Level Answer')


class SurveySectionLink(models.Model):
    """
    Maybe it is possible that one section has to take multiple surveys in the future. That's why we use this table
    At the moment this is not allowed though, so we set section to unique.
    -> This does not mean that parent- or child-sections aren't allowed to have other surveys
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('survey'))
    section = models.OneToOneField(Section, on_delete=models.CASCADE, verbose_name=_('section'))

    class Meta:
        verbose_name = _('Survey-section-link')
        verbose_name_plural = _('Survey-section-links')

    def __str__(self):
        return '{} - {}'.format(str(self.survey), str(self.section))


class Statistics:
    """
    This model can be seen as a view in a database. I've decided not to use a view though, because django doesn't
    support apps that are portable with views (views can't be automatically created by the orm)
    """

    def __init__(self):
        self.statistics = []

    def __iter__(self):
        return self.statistics.__iter__()

    def __getitem__(self, item):
        return self.statistics.__getitem__(item)

    def __len__(self):
        return len(self.statistics)

    def init_personal(self, user):
        #  This will throw an error if the survey was not finished yet, but you should never call this method
        #  outside of a function without the decorator @user_has_finished_survey
        self.statistics = [
            {
                'level': level[1],
                'avg': Answer.objects.filter(survey_instance=SurveyInstance.objects.get(user=user),
                                             question__level=level[0]).aggregate(Avg('answer'))['answer__avg']
            } for level in LEVEL_CHOICES]
        important = ImportantLevelAnswer.objects.filter(survey_instance=SurveyInstance.objects.get(user=user))
        for imp in important:
            self.statistics[imp.level - 1]['avg'] *= 2

    def _init_section(self, section):
        # We ask the user as well because we also check access-rights at this level
        with connection.cursor() as cursor:
            cursor.execute('SELECT q.level, AVG('
                           'CASE WHEN NOT EXISTS('
                           '    SELECT * '
                           '    FROM surveys_importantlevelanswer la'
                           '    WHERE la.level = q.level AND la.survey_instance_id = a.survey_instance_id) THEN answer '
                           'ELSE answer * 2 END )::numeric(4,1) '
                           'FROM surveys_answer a INNER JOIN surveys_question q ON (a.question_id = q.id) '
                           'INNER JOIN users_customuser u ON (a.user_id = u.id) INNER JOIN '
                           'organisations_sectionuserlink sl ON (u.id = sl.user_id) '
                           'WHERE a.survey_instance_id IS NOT NULL AND sl.section_id IN ('
                           'WITH RECURSIVE section_tree2(id, name, parent_section_id, organisation_id) AS ('
                           '    SELECT id, name, parent_section_id, organisation_id '
                           '    FROM organisations_section '
                           '    WHERE id = %s '
                           'UNION ALL '
                           '    SELECT ss.id, ss.name, ss.parent_section_id, ss.organisation_id '
                           '    FROM organisations_section AS ss INNER JOIN section_tree2 AS '
                           '    st ON (ss.parent_section_id = st.id)'
                           ') '
                           'SELECT id '
                           'FROM section_tree2'
                           ') '
                           'GROUP BY q.level '
                           'ORDER BY q.level', [section.id])
            rows = cursor.fetchall()
            self.statistics = [{'level': LEVEL_CHOICES[int(row[0]) - 1][1], 'avg': row[1]} for row in rows]

    def init_section_as_in_section(self, user, section):
        def has_access():
            # This is not a fast function at all, since it does lots of queries. If this becomes a problem, this
            # is the first place to start improving
            if user.is_superuser:
                return True
            user_section = Section.objects.get(sectionuserlink__user=user)
            parent_line = Section.objects.get_all_parents_line(user_section.id)
            if section in parent_line:
                return True
            return False

        if not has_access():
            raise PermissionDenied
        self._init_section(section)

    def init_section_as_admin(self, user, section):
        def has_access():
            # This is not a fast function at all, since it does lots of queries. If this becomes a problem, this
            # is the first place to start improving
            if user.is_superuser:
                return True
            admin_sections = Section.objects.filter(sectionadministrator__user=user)
            for admin_section in admin_sections:
                children = Section.objects.get_all_children(admin_section.id)
                if section in children:
                    return True
            return False

        if not has_access():
            raise PermissionDenied
        self._init_section(section)

    def init_other_person(self, user, other):
        def has_access():
            # This is not a fast function at all, since it does lots of queries. If this becomes a problem, this
            # is the first place to start improving
            admin_sections = Section.objects.filter(sectionadministrator__user=user)
            for admin_section in admin_sections:
                children = Section.objects.get_all_children(admin_section.id)
                try:
                    SectionUserLink.objects.get(user=other, section__in=children)
                    return True
                except ObjectDoesNotExist:
                    pass
            return False

        if not has_access():
            raise PermissionDenied

        self.init_personal(other)
