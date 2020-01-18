from django.db.models import Avg
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
    survey = get_surveys(request)
    print(survey)
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
    if len(surveys) == 1:
        return redirect('see-personal-statistics', surveys[0].slug)
    return render(request, 'surveys/personal-statistics.html', {'surveys': surveys})


def get_surveys(request):
    """This is only a helper method. It does not return a view"""
    surveys = Survey.objects.raw('WITH RECURSIVE section_tree(id, parent_section_id) AS ( '
                                 '   SELECT s.id, s.parent_section_id '
                                 '   FROM organisations_section s INNER JOIN organisations_sectionuserlink l '
                                 '   ON (s.id = l.section_id) '
                                 '   WHERE l.user_id = %s '
                                 'UNION ALL '
                                 '   SELECT ss.id, ss.parent_section_id '
                                 '   FROM organisations_section ss INNER JOIN section_tree st '
                                 '   ON (ss.id = st.parent_section_id)'
                                 ') '
                                 'SELECT su.id, su.name, su.slug '
                                 'FROM section_tree s INNER JOIN surveys_surveysectionlink l ON (s.id = l.section_id) '
                                 'INNER JOIN surveys_survey su ON (l.survey_id = su.id) '
                                 'ORDER BY s.id DESC', [request.user.id])
    # This ORDER BY goes by the presumption that a higher id means the section is lower in the tree.
    # If this presumption is correct, we should always get the first section above us that is linked to a survey
    return surveys[0]  # Maybe in the future this can return multiple surveys...
