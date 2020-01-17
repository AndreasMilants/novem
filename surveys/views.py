from django.db.models import Avg, Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from .models import Question, LEVEL_CHOICES, Survey, Answer
from .forms import AnswerFormSet, get_answer_form_set
from organisations.decorators import user_is_linked_to_organisation, user_is_linked_to_section


@login_required
@user_is_linked_to_organisation
@user_is_linked_to_section
def homepage(request):
    context = {}
    return render(request, 'surveys/home.html', context)


@login_required
@user_is_linked_to_organisation
@user_is_linked_to_section
def survey_view(request, page):
    # TODO This line should be changed to something that actually gets the correct survey
    survey = Survey.objects.all()[0]
    if request.method == "POST":
        form_set = AnswerFormSet(request.POST)
        if form_set.is_valid():
            for form in form_set:
                if form.is_valid():
                    try:
                        model = Answer.objects.get(question=form.cleaned_data.get('question'), user=request.user)
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

    if int(page) > len(LEVEL_CHOICES):
        return redirect('personal-statistics')

    return render(request, 'surveys/survey.html',
                  {'page': int(page), 'pages': len(LEVEL_CHOICES), 'form_set': form_set,
                   'level': LEVEL_CHOICES[int(page) - 1][1], 'survey': survey})


@login_required
@user_is_linked_to_organisation
@user_is_linked_to_section
def get_personal_survey_stats(request, survey):
    personal_stats = [
        {'level': level[1], 'avg': Answer.objects.filter(user=request.user, question__survey__slug=survey,
                                                         question__level=level[0]).aggregate(Avg('answer'))[
            'answer__avg']} for level in LEVEL_CHOICES]
    return render(request, 'surveys/see-personal-statistics-survey.html',
                  {'stats': personal_stats, 'min': -50, 'max': 50, 'survey': Survey.objects.get(slug=survey)})


@login_required
@user_is_linked_to_organisation
@user_is_linked_to_section
def personal_statistics(request):
    surveys = Survey.objects.filter(question__answer__user=request.user).distinct()
    return render(request, 'surveys/personal-statistics.html', {'surveys': surveys})
