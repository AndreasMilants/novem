from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model

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

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')

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

    def __str__(self):
        return '{} - {}'.format(str(self.user), str(self.question))
