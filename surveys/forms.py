from django import forms
from .models import Survey, Answer
from django.forms import formset_factory


class CreateSurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        exclude = ['slug']


class AnswerForm(forms.ModelForm):
    def __init__(self, *args, user=None, page=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.page = page

    class Meta:
        model = Answer
        fields = ['answer', 'question', ]
        widgets = {'answer': forms.NumberInput(attrs={'type': 'range', 'min': '-50', 'max': '50'}),
                   'question': forms.HiddenInput(), }
        labels = {'answer': ''}


AnswerFormSet = formset_factory(AnswerForm, extra=0)


def get_answer_form_set(initial):
    form_set = AnswerFormSet(initial=initial)
    for model, form in zip(initial, form_set.forms):
        form.fields['answer'].label = model['question']
    return form_set
