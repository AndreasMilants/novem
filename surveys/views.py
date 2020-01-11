from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from .models import Question, LEVEL_CHOICES, Survey, Answer
from .forms import AnswerFormSet, get_answer_form_set
from organisations.decorators import user_is_linked_to_organisation


@login_required
@user_is_linked_to_organisation
def homepage(request):
    context = {}
    return render(request, 'surveys/home.html', context)


@login_required
@user_is_linked_to_organisation
def survey_view(request, page):
    # TODO This line should be changed to something that actually gets the correct survey
    survey = Survey.objects.all()[0]
    if request.method == "POST":
        form_set = AnswerFormSet(request.POST)
        if form_set.is_valid():
            for form in form_set:
                if form.is_valid():
                    try:
                        model = Answer.objects.get().filter(question=form.cleaned_data.get('question'),
                                                            user=request.user)
                        model.answer = form.cleaned_data.get('answer')
                    except Answer.DoesNotExist:
                        model = form.save(commit=False)
                        model.user = request.user
                    model.save()
            if request.POST.get('previous', False):
                return redirect("survey", page=str(max(0, int(page) - 1)))
            return redirect("survey", page=str(int(page) + 1))
    else:
        answers = [
            {'question': answer.question, 'user': request.user, 'answer': answer.answer, 'id': answer.id} for answer in
            Answer.objects.filter(user=request.user, question__level=page,
                                  question__survey=survey).select_related('question')
        ]
        if not answers:
            answers = [{'question': question, 'user': request.user} for question in
                       Question.objects.filter(level=page, survey=survey)]
        form_set = get_answer_form_set(answers)

    return render(request, 'surveys/survey.html',
                  {'page': int(page), 'pages': len(LEVEL_CHOICES), 'form_set': form_set,
                   'level': LEVEL_CHOICES[int(page) - 1][1], 'survey': survey})


"""
@login_required
def get_survey_stats(request, survey):
    personal_stats =
"""
