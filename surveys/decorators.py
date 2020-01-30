from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from organisations.decorators import user_is_linked_to_section
from .models import SurveyInstance
from django.core.exceptions import ObjectDoesNotExist


def user_has_finished_survey(func):
    @user_is_linked_to_section
    def wrapper(request, *args, **kwargs):
        try:
            survey_instance = SurveyInstance.objects.get(user=request.user)
            return func(request, *args, **kwargs)
        except ObjectDoesNotExist:
            path = request.path
            resolved_url = "".join((reverse('survey', args=['1']), '?next={}'.format(path)))
            messages.error(request, _('You have to finish your survey before you can access this page'))
            return redirect(resolved_url)

    return wrapper
