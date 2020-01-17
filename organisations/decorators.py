from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


def user_is_linked_to_organisation(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.organisationuserlink_set.all():
            path = request.path
            resolved_url = "".join((resolve_url('authenticate-with-org'), '?next={}'.format(path)))
            messages.error(request, _('You have to link to an organisation before you can access this page'))
            return redirect(resolved_url)
        return func(request, *args, **kwargs)

    return wrapper


def user_is_linked_to_section(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.sectionuserlink_set.all():
            path = request.path
            resolved_url = "".join((resolve_url('link-to-section'), '?next={}'.format(path)))
            messages.error(request, _('You have to choose a section before you can access this page'))
            return redirect(resolved_url)
        return func(request, *args, **kwargs)

    return wrapper
