from django.shortcuts import redirect
from django.shortcuts import resolve_url


def user_is_linked_to_organisation(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.organisationuserlink_set.all():
            path = request.path
            resolved_url = "".join((resolve_url('authenticate-with-org'), '?next={}'.format(path)))
            return redirect(resolved_url)
        return func(request, *args, **kwargs)

    return wrapper
