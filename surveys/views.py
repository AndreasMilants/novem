from django.db.models import Avg
from django.shortcuts import render, redirect
from .models import Question, LEVEL_CHOICES, Survey, Answer, SurveySectionLink
from organisations.models import Section, SectionAdministrator, SectionUserLink
from .forms import AnswerFormSet, get_answer_form_set
from organisations.decorators import user_is_linked_to_section, user_is_linked_to_organisation
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.db import connection
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
import uuid


User = get_user_model()

"""
The following file has a lot of repeated parts in sql-queries. This could be solved by using views, but I'm hesitant
to use these in conjunction with django. The Django ORM has no way to automatically create views with migrations,
so the app could not be automatically deployed on a different platform, using a new database...

The positive part of using views might be that all of these raw queries could be replaced using defined functions
in the ORM.
"""


@user_is_linked_to_section
def homepage_view(request):
    for item in Section.objects.all():
        item.uuid = uuid.uuid4()
        item.save()
    context = {'current': 'survey'}
    return render(request, 'surveys/home.html', context)


@user_is_linked_to_section
def survey_view(request, page):
    surveys = get_surveys(request)
    if not surveys:
        messages.error(request, _('The administrator did not set up a survey for your section.'))
        return redirect('home')
    survey = surveys[0]
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
        return redirect('personal-statistics', section='personal')

    return render(request, 'surveys/survey.html',
                  {'page': int(page), 'pages': range(1, len(LEVEL_CHOICES) + 1), 'form_set': form_set,
                   'level': LEVEL_CHOICES[int(page) - 1][1], 'survey': survey, 'current': 'survey'})


@user_is_linked_to_section
def personal_statistics_view(request, section=''):
    surveys = Survey.objects.filter(question__answer__user=request.user).distinct()
    if len(surveys) == 0:
        messages.error(request, _("You have to finish the survey before you can see statistics"))
        return redirect('survey', page='1')
    survey_slug = surveys[0].slug
    sections = Section.objects.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id, name) AS ( '
                                   '   SELECT 1 AS depth, s.id, s.parent_section_id, s.name '
                                   '   FROM organisations_section s INNER JOIN organisations_sectionuserlink l '
                                   '   ON (s.id = l.section_id) '
                                   '   WHERE l.user_id = %s '
                                   'UNION ALL '
                                   '   SELECT depth + 1, ss.id, ss.parent_section_id, ss.name '
                                   '   FROM organisations_section ss INNER JOIN section_tree st '
                                   '   ON (ss.id = st.parent_section_id)'
                                   ') '
                                   'SELECT * '
                                   'FROM section_tree '
                                   'ORDER BY depth DESC', [request.user.id])

    sections = list(sections)
    sections.append({'name': _('Personal'), 'id': 'personal'})

    if section == 'personal' or section == '':
        stats = [
            {'level': level[1], 'avg': Answer.objects.filter(user=request.user, question__survey__slug=survey_slug,
                                                             question__level=level[0]).aggregate(Avg('answer'))[
                'answer__avg']} for level in LEVEL_CHOICES]
        title = _('Personal')
    else:
        section = int(section)
        with connection.cursor() as cursor:
            # You could ask why we don't just skip the recursion to get the section and immediately get all subsections
            # of the section with this id. This is for safety: to make sure that not just anybody can get statistics
            # about a section he is not a part of. If the request is OK the correct section will be chosen.
            # If the request is not legit, the 'hacker' will not see any statistics
            cursor.execute('SELECT q.level, AVG(answer)::numeric(4,1) '
                           'FROM surveys_answer a INNER JOIN surveys_question q ON (a.question_id = q.id) '
                           'INNER JOIN users_customuser u ON (a.user_id = u.id) INNER JOIN '
                           'organisations_sectionuserlink sl ON (u.id = sl.user_id) '
                           'WHERE sl.section_id IN ('
                           'WITH RECURSIVE section_tree2(id, name, parent_section_id, organisation_id) AS ('
                           '    SELECT id, name, parent_section_id, organisation_id '
                           '    FROM organisations_section '
                           '    WHERE id = ('
                           '        WITH RECURSIVE section_tree(depth, id, parent_section_id, name) AS ( '
                           '            SELECT 1 AS depth, s.id, s.parent_section_id, s.name '
                           '            FROM organisations_section s INNER JOIN organisations_sectionuserlink l '
                           '            ON (s.id = l.section_id) '
                           '            WHERE l.user_id = %s '
                           '        UNION ALL '
                           '            SELECT depth + 1, ss.id, ss.parent_section_id, ss.name '
                           '            FROM organisations_section ss INNER JOIN section_tree st '
                           '            ON (ss.id = st.parent_section_id)'
                           '        )'
                           '        SELECT id'
                           '        FROM section_tree '
                           '        WHERE id = %s '
                           '        )'
                           'UNION ALL '
                           '    SELECT ss.id, ss.name, ss.parent_section_id, ss.organisation_id '
                           '    FROM organisations_section AS ss INNER JOIN section_tree2 AS '
                           '    st ON (ss.parent_section_id = st.id)'
                           ') '
                           'SELECT id '
                           'FROM section_tree2'
                           ') '
                           'GROUP BY q.level '
                           'ORDER BY q.level', [request.user.id, int(section)])
            rows = cursor.fetchall()
            stats = [
                {'level': LEVEL_CHOICES[int(row[0]) - 1][1], 'avg': row[1]} for row in rows]
            title = Section.objects.get(
                id=int(section)).name  # This is not really that big of a problem. At this moment
            # We don't care that people can map section_ids to their names...

    return render(request, 'surveys/personal-statistics.html',
                  {'stats': stats, 'min': min([stat['avg'] for stat in stats]),
                   'max': max([stat['avg'] for stat in stats]), 'current': 'stat', 'sections': sections,
                   'title': title})


@user_is_linked_to_organisation
def admin_statistics_view(request):
    if not SectionAdministrator.objects.filter(user=request.user):
        raise PermissionDenied

    return render(request, 'surveys/administrator-statistics-home.html',
                  {'sections': get_sections_admin(request), 'current': 'stat-admin'})


@user_is_linked_to_organisation
def admin_statistics_users_view(request, section):
    if not SectionAdministrator.objects.filter(user=request.user):
        raise PermissionDenied
    with connection.cursor() as cursor:
        cursor.execute('SELECT u.id, u.email, s.id as section_id, s.name as section_name '
                       'FROM users_customuser u INNER JOIN '
                       'organisations_sectionuserlink sl ON (u.id = sl.user_id) '
                       'INNER JOIN organisations_section s ON (sl.section_id = s.id) '
                       'WHERE s.id IN ('
                       'WITH RECURSIVE section_tree2(id, name, parent_section_id, organisation_id) AS ('
                       '    SELECT id, name, parent_section_id, organisation_id '
                       '    FROM organisations_section '
                       '    WHERE id = ('
                       '        WITH RECURSIVE section_tree(depth, id, parent_section_id, name) AS ( '
                       '            SELECT 1 AS depth, s.id, s.parent_section_id, s.name '
                       '            FROM organisations_section s INNER JOIN organisations_sectionadministrator a '
                       '            ON (s.id = a.section_id) '
                       '            WHERE a.user_id = %s '
                       '        UNION ALL '
                       '            SELECT depth + 1, ss.id, ss.parent_section_id, ss.name '
                       '            FROM organisations_section ss INNER JOIN section_tree st '
                       '            ON (ss.parent_section_id = st.id)'
                       '        )'
                       '        SELECT id'
                       '        FROM section_tree '
                       '        WHERE id = %s '
                       '        )'
                       'UNION ALL '
                       '    SELECT ss.id, ss.name, ss.parent_section_id, ss.organisation_id '
                       '    FROM organisations_section AS ss INNER JOIN section_tree2 AS '
                       '    st ON (ss.parent_section_id = st.id)'
                       ') '
                       'SELECT id '
                       'FROM section_tree2'
                       ') '
                       'ORDER BY s.name', [request.user.id, section])
        rows = cursor.fetchall()
        users = [{'id': row[0], 'email': row[1], 'section_id': row[2], 'section_name': row[3]} for row in rows]

    return render(request, 'surveys/administrator-statistics-users.html',
                  {'users': users, 'sections': get_sections_admin(request), 'current': 'stat-admin',
                   'current_section': Section.objects.get(id=section)})


@user_is_linked_to_organisation
def admin_statistics_section_view(request, section):
    if not SectionAdministrator.objects.filter(user=request.user):
        raise PermissionDenied
    with connection.cursor() as cursor:
        # You could ask why we don't just skip the recursion to get the section and immediately get all subsections
        # of the section with this id. This is for safety: to make sure that not just anybody can get statistics
        # about a section he is not an administrator of. If the request is OK the correct section will be chosen.
        # If the request is not legit, the 'hacker' will not see any statistics
        cursor.execute('SELECT q.level, AVG(answer)::numeric(4,1) '
                       'FROM surveys_answer a INNER JOIN surveys_question q ON (a.question_id = q.id) '
                       'INNER JOIN users_customuser u ON (a.user_id = u.id) INNER JOIN '
                       'organisations_sectionuserlink sl ON (u.id = sl.user_id) '
                       'WHERE sl.section_id IN ('
                       'WITH RECURSIVE section_tree2(id, name, parent_section_id, organisation_id) AS ('
                       '    SELECT id, name, parent_section_id, organisation_id '
                       '    FROM organisations_section '
                       '    WHERE id = ('
                       '        WITH RECURSIVE section_tree(id, parent_section_id, name) AS ( '
                       '            SELECT s.id, s.parent_section_id, s.name '
                       '            FROM organisations_section s INNER JOIN organisations_sectionadministrator a '
                       '            ON (s.id = a.section_id) '
                       '            WHERE a.user_id = %s '
                       '        UNION ALL '
                       '            SELECT ss.id, ss.parent_section_id, ss.name '
                       '            FROM organisations_section ss INNER JOIN section_tree st '
                       '            ON (ss.parent_section_id = st.id)'
                       '        )'
                       '        SELECT id'
                       '        FROM section_tree '
                       '        WHERE id = %s '
                       '        )'
                       'UNION ALL '
                       '    SELECT ss.id, ss.name, ss.parent_section_id, ss.organisation_id '
                       '    FROM organisations_section AS ss INNER JOIN section_tree2 AS '
                       '    st ON (ss.parent_section_id = st.id)'
                       ') '
                       'SELECT id '
                       'FROM section_tree2'
                       ') '
                       'GROUP BY q.level '
                       'ORDER BY q.level', [request.user.id, int(section)])
        rows = cursor.fetchall()
        stats = [
            {'level': LEVEL_CHOICES[int(row[0]) - 1][1], 'avg': row[1]} for row in rows]

    return render(request, 'surveys/administrator-statistics-section.html',
                  {'stats': stats, 'sections': get_sections_admin(request),
                   'current_section': Section.objects.get(id=section), 'current': 'stat-admin'})


@user_is_linked_to_organisation
def admin_statistics_user_view(request, user):
    if not SectionAdministrator.objects.filter(user=request.user):
        raise PermissionDenied
    # messages.info(request, _('This user has not finished his survey'))
    messages.error(request, 'Not implemented yet')
    return redirect('admin-statistics')


def get_surveys(request):
    """This is only a helper method. It does not return a view"""
    surveys = Survey.objects.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id) AS ( '
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
                                 'ORDER BY depth DESC', [request.user.id])
    return surveys


def get_sections_admin(request):
    return Section.objects.raw('WITH RECURSIVE section_tree(depth, id, parent_section_id, name) AS ( '
                               '   SELECT 1 AS depth, s.id, s.parent_section_id, s.name '
                               '   FROM organisations_section s INNER JOIN organisations_sectionadministrator a '
                               '   ON (s.id = a.section_id) '
                               '   WHERE a.user_id = %s '
                               'UNION ALL '
                               '   SELECT depth + 1, ss.id, ss.parent_section_id, ss.name '
                               '   FROM organisations_section ss INNER JOIN section_tree st '
                               '   ON (ss.parent_section_id = st.id)'
                               ') '
                               'SELECT * '
                               'FROM section_tree '
                               'ORDER BY depth', [request.user.id])
