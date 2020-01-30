from django import forms
from .models import Survey, Answer, Question, ImportantLevelAnswer, SurveyInstance
from django.forms import formset_factory, BaseFormSet, modelformset_factory, BaseModelFormSet
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


class CreateSurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        exclude = ['slug']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer', 'question', ]
        widgets = {'answer': forms.NumberInput(attrs={'type': 'range', 'min': '-50', 'max': '50'}),
                   'question': forms.HiddenInput(), }
        labels = {'answer': ''}

    def __init__(self, *args, user=None, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)
        self.user = user
        self.fields['answer'].label = Question.objects.get(id=initial.get('question'))

    def save(self, commit=True):
        qs = Answer.objects.filter(question=self.cleaned_data.get('question'), user=self.user)
        if not qs:
            self.instance = Answer(question=self.cleaned_data.get('question'),
                                   answer=self.cleaned_data.get('answer'), user=self.user)
        else:
            self.instance = qs[0]
            self.instance.answer = self.cleaned_data.get('answer')
        if not self.instance.survey_instance:
            try:
                survey_instance = SurveyInstance.objects.get(user=self.user)
                self.instance.survey_instance = survey_instance
            except ObjectDoesNotExist:
                pass  # This means this survey is not finished yet, so we don't need to set this.
        if commit:
            self.instance.save()
        return self.instance


class BaseAnswerFormSet(BaseFormSet):
    def __init__(self, *args, data=None, survey, user, page=1, **kwargs):
        answers = [{'question': answer.question_id, 'answer': answer.answer if answer.answer else 0} for answer in
                   Answer.objects.raw('SELECT a.id, q.id as question_id, a.answer '
                                      'FROM surveys_question q left outer join surveys_answer a '
                                      'ON (q.id = a.question_id AND a.user_id = %s) '
                                      'WHERE q.level = %s AND q.survey_id = %s', [user.id, page, survey.id])]
        super().__init__(*args, data=data, initial=answers, **kwargs)

        self.questions = set(answer['question'] for answer in answers)

    def clean(self):
        """
        This is really only so that people won't try and circumvent the formset and just answer some random
        questions from other surveys or don't answer all questions of the formset
        """
        if any(self.errors):
            return
        questions = set(q for q in self.questions)  # copy the set
        for form in self.forms:
            try:
                questions.remove(form.cleaned_data.get('question').id)
            except KeyError:
                raise forms.ValidationError(
                    _('You tried answering a question that does not belong to a survey of yours'), code='invalid', )
            except AttributeError:
                raise forms.ValidationError(
                    _('You have to answer all questions on this level'), code='invalid', )
        if questions:
            raise forms.ValidationError(
                _('You have to answer all questions on this level'), code='invalid', )


AnswerFormSet = formset_factory(AnswerForm, extra=0, formset=BaseAnswerFormSet)


class SurveyInstanceFormAdmin(forms.ModelForm):
    class Meta:
        model = SurveyInstance
        exclude = []


class ImportantLevelAnswerForm(forms.ModelForm):
    class Meta:
        model = ImportantLevelAnswer
        exclude = ['survey_instance']
        # widgets = {'survey_instance': forms.HiddenInput()}

    def __init__(self, *args, user, survey, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.survey = survey

    def save(self, commit=True):
        if self.instance.id is None:
            try:
                survey_instance = SurveyInstance.objects.get(user=self.user)
                self.instance = ImportantLevelAnswer(survey_instance=survey_instance)
            except ObjectDoesNotExist:
                survey_instance = SurveyInstance(user=self.user, survey=self.survey)
                survey_instance.save()
                Answer.objects.filter(user=self.user).update(survey_instance=survey_instance)
                self.instance = ImportantLevelAnswer(survey_instance=survey_instance)
        self.instance.level = self.cleaned_data.get('level')
        if commit:
            self.instance.save()
        return self.instance


class BaseImportantLevelAnswerFormSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        levels = set()
        for form in self.forms:
            levels.add(form.cleaned_data.get('level'))
        if not len(levels) == 3:
            raise forms.ValidationError(_('You have to choose 3 different levels'))
        # TODO Add checks to see whether all questions of the survey were answered
        return self.cleaned_data


ImportantLevelAnswerFormset = modelformset_factory(ImportantLevelAnswer, max_num=3, min_num=3, validate_max=True,
                                                   formset=BaseImportantLevelAnswerFormSet,
                                                   form=ImportantLevelAnswerForm)
