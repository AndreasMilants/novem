from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from organisations.forms import OrganisationAuthenticationForm
from organisations.models import OrganisationUserLink, Organisation
from django.utils.translation import ugettext_lazy as _
from .models import Question, LEVEL_CHOICES, Survey, Answer
from .forms import AnswerFormSet, AnswerForm, get_answer_form_set


@login_required
def homepage(request):
    if not request.user.organisationuserlink_set.all():
        return redirect('authenticate-with-org')
    context = {}
    return render(request, 'surveys/home.html', context)


@login_required
def add_organisation(request):
    if request.method == "POST":
        form = OrganisationAuthenticationForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            org_user_link = OrganisationUserLink(organisation=Organisation.objects.get(name=model.organisation),
                                                 user=request.user)
            org_user_link.save()
            messages.success(request, _('You are now a member of %(organisation)s.') % {
                'organisation': model.organisation,
            })
            return redirect('home')
    else:
        form = OrganisationAuthenticationForm()
    return render(request, "organisations/authenticate_organisation.html",
                  {"form": form, })


@login_required
def survey_view(request, page):
    if request.method == "POST":
        form_set = AnswerFormSet(request.POST)
        if form_set.is_valid():
            for form in form_set:
                if form.is_valid():
                    models = Answer.objects.all().filter(question=form.cleaned_data.get('question'), user=request.user)
                    if not models:
                        model = form.save(commit=False)
                        model.user = request.user
                    else:
                        model = models[0]
                        model.answer = form.cleaned_data.get('answer')
                    model.save()
            return redirect("survey", page=str(int(page) + 1))
    else:
        # TODO This line should be changed to something that actually gets the correct survey
        survey = Survey.objects.all()[0]
        answers = [{'question': answer.question, 'user': request.user, 'answer': answer.answer, 'id': answer.id} for answer in
                   Answer.objects.all().filter(user=request.user, question__level=page, question__survey=survey)]
        if not answers:
            answers = [{'question': question, 'user': request.user} for question in
                       Question.objects.all().filter(level=page, survey=survey)]
        form_set = get_answer_form_set(answers)

    return render(request, 'surveys/survey.html',
                  {'page': page, 'pages': len(LEVEL_CHOICES), 'form_set': form_set,
                   'level': LEVEL_CHOICES[int(page) - 1][1]})
