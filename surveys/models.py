from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from organisations.models import Section


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


class Survey(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('name'))
    slug = models.SlugField()

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


class Answer(models.Model):
    question = models.ForeignKey(Question, verbose_name=_('Question'), on_delete=models.CASCADE)
    answer = models.IntegerField(default=0, verbose_name=_('Answer'),
                                 validators=[
                                     MaxValueValidator(50),
                                     MinValueValidator(-50)
                                 ])
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=0)

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        unique_together = ('question', 'user',)

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.question))


class SurveySectionLink(models.Model):
    """Maybe it is possible that one section has to take multiple surveys. That's why we use this table"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('survey'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name=_('section'))
    """section_uuid = models.ForeignKey(Section, null=True, blank=True, related_name='d', to_field='uuid', on_delete=models.PROTECT)"""

    class Meta:
        verbose_name = _('Survey-section-link')
        verbose_name_plural = _('Survey-section-links')

    def __str__(self):
        return '{} - {}'.format(str(self.survey), str(self.section))
