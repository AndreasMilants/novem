from django.shortcuts import render, redirect
from .models import LEVEL_CHOICES, Survey, Statistics, Answer, ImportantLevelAnswer
from organisations.models import Section, SectionAdministrator
from .forms import AnswerFormSet, ImportantLevelAnswerFormset
from organisations.decorators import user_is_linked_to_section, user_is_linked_to_organisation
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .decorators import user_has_finished_survey
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


@user_is_linked_to_section
def homepage_view(request):
    context = {'current': 'survey'}
    return render(request, 'surveys/home.html', context)


@user_is_linked_to_section
def survey_view(request, page):
    if int(page) > len(LEVEL_CHOICES) + 1:
        return redirect('personal-statistics', section='personal')

    survey = Survey.objects.get_personal_survey(request.user)
    if not survey:
        messages.error(request, _('The administrator did not set up a survey for your section.'))
        return redirect('home')

    pages = [{
        'page': level,
        'link': True if level == 1 or Answer.objects.filter(user=request.user, question__level=level - 1) else False
    } for level in range(1, len(LEVEL_CHOICES) + 1)]

    pages.append({'page': 10, 'link': True if Answer.objects.filter(user=request.user, question__level=9) else False})

    if int(page) > 1 and not pages[int(page) - 2]['link']:
        for i in range(int(page) - 1, 0, -1):
            if pages[i]['link']:
                return redirect('survey', page=i + 1)
        return redirect('survey', page=1)

    if int(page) < 10:
        if request.method == 'POST':
            form_set = AnswerFormSet(data=request.POST, survey=survey, user=request.user, page=page,
                                     form_kwargs={'user': request.user})
            if form_set.is_valid():
                for form in form_set:
                    form.save()
                next_page = request.POST.get('next_page', int(page) + 1)
                return redirect("survey", page=next_page)
        else:
            form_set = AnswerFormSet(survey=survey, user=request.user, page=page, form_kwargs={'user': request.user})

        return render(request, 'surveys/survey.html',
                      {'page': int(page), 'pages': pages, 'form_set': form_set,
                       'level': LEVEL_CHOICES[int(page) - 1][1], 'survey': survey, 'current': 'survey'})

    if request.method == 'POST':
        form_set = ImportantLevelAnswerFormset(data=request.POST, form_kwargs={'user': request.user, 'survey': survey})
        if form_set.is_valid():
            for form in form_set:
                form.save()
            next_page = request.POST.get('next_page', int(page) + 1)
            return redirect("survey", page=next_page)
        next_page = request.POST.get('next_page', int(page) + 1)
        if int(next_page) <= 10:
            return redirect("survey", page=next_page)
    else:
        form_set = ImportantLevelAnswerFormset(
            queryset=ImportantLevelAnswer.objects.filter(survey_instance__user=request.user),
            form_kwargs={'user': request.user, 'survey': survey})

    return render(request, 'surveys/finish-survey.html',
                  {'form_set': form_set, 'page': 10, 'pages': pages, 'survey': survey, 'current': 'survey'})


@user_has_finished_survey
def personal_statistics_view(request, section=''):
    surveys = Survey.objects.filter(question__answer__user=request.user).distinct()
    if len(surveys) == 0:
        messages.error(request, _("You have to finish the survey before you can see statistics"))
        return redirect('survey', page='1')
    sections = Section.objects.get_all_parents_line(Section.objects.get(sectionuserlink__user=request.user).id)
    sections.append({'name': _('Personal'), 'id': 'personal'})

    stats = Statistics()
    if section == 'personal' or section == '':
        stats.init_personal(request.user)
        title = _('Personal')
    else:
        stats.init_section_as_in_section(request.user, Section.objects.get(id=section))
        title = Section.objects.get(id=section).name

    return render(request, 'surveys/personal-statistics.html',
                  {'stats': stats, 'min': min([stat['avg'] for stat in stats]),
                   'max': max([stat['avg'] for stat in stats]), 'current': 'stat', 'sections': sections,
                   'title': title})


@user_is_linked_to_organisation
def admin_statistics_view(request):
    if not SectionAdministrator.objects.filter(user=request.user):
        raise PermissionDenied

    return render(request, 'surveys/administrator-statistics-home.html',
                  {'sections': Section.objects.get_sections_admin(request.user), 'current': 'stat-admin'})


@user_is_linked_to_organisation
def admin_statistics_users_view(request, section):
    if not SectionAdministrator.objects.filter(user=request.user):
        raise PermissionDenied
    users = User.objects.filter(sectionuserlink__section__in=Section.objects.get_all_children(section)).select_related(
        'sectionuserlink').select_related('sectionuserlink__section')

    return render(request, 'surveys/administrator-statistics-users.html',
                  {'users': users, 'sections': Section.objects.get_sections_admin(request.user),
                   'current': 'stat-admin',
                   'current_section': Section.objects.get(id=section)})


@user_is_linked_to_organisation
def admin_statistics_section_view(request, section):
    stats = Statistics()
    stats.init_section_as_admin(request.user, Section.objects.get(id=section))
    return render(request, 'surveys/administrator-statistics-section.html',
                  {'stats': stats, 'sections': Section.objects.get_sections_admin(request.user),
                   'current_section': Section.objects.get(id=section), 'current': 'stat-admin'})


@user_is_linked_to_organisation
def admin_statistics_user_view(request, user):
    stats = Statistics()
    other = User.objects.get(email=user)
    section = Section.objects.get(sectionuserlink__user=other)
    try:
        stats.init_other_person(request.user, other)
    except ObjectDoesNotExist:
        if len(stats) == 0:
            messages.info(request, _('This user has not finished his survey'))
    return render(request, 'surveys/administrator-statistics-user.html',
                  {'stats': stats, 'current_section': section, 'user_statistics': other, 'current': 'stat-admin'})
