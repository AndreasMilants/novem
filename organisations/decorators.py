from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from .models import OrganisationUserLink, SectionUserLink
from django.core.exceptions import ObjectDoesNotExist


def user_is_linked_to_organisation(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            OrganisationUserLink.objects.get(user=request.user)
        except ObjectDoesNotExist:
            path = request.path
            resolved_url = "".join((resolve_url('authenticate-with-org'), '?next={}'.format(path)))
            messages.error(request, _('You have to link to an organisation before you can access this page'))
            return redirect(resolved_url)
        return func(request, *args, **kwargs)

    return wrapper


def user_is_linked_to_section(func):
    @user_is_linked_to_organisation
    def wrapper(request, *args, **kwargs):
        try:
            SectionUserLink.objects.get(user=request.user)
        except ObjectDoesNotExist:
            path = request.path
            resolved_url = "".join((resolve_url('link-to-section'), '?next={}'.format(path)))
            messages.error(request, _('You have to choose a section before you can access this page'))
            return redirect(resolved_url)
        return func(request, *args, **kwargs)

    return wrapper
