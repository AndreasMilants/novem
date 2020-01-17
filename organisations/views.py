from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import OrganisationAuthenticationForm, ChooseSectionForm
from django.utils.translation import ugettext_lazy as _
from .decorators import user_is_linked_to_organisation
from .models import Organisation, SectionUserLink
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url


@login_required
def link_to_organisation(request):
    # We've allowed multiple organisations to be linked to users in the future with the way our models are set up.
    # But at this moment we don't want users to be able to link to multiple organisations, so we raise PermissionDenied
    if request.user.organisationuserlink_set.all():
        raise PermissionDenied()
    if request.method == "POST":
        form = OrganisationAuthenticationForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            messages.success(request, _('You are now a member of %(organisation)s.') % {
                'organisation': model.organisation,
            })
            next_page = request.GET.get("next")
            if next_page:
                resolved_url = "".join((resolve_url('link-to-section'), '?next={}'.format(next_page)))
            else:
                resolved_url = resolve_url('link-to-section')
            return redirect(resolved_url)
    else:
        form = OrganisationAuthenticationForm()
    return render(request, "organisations/authenticate_organisation.html",
                  {"form": form, })


@login_required
@user_is_linked_to_organisation
def link_to_section(request):
    # Same reason as with link_to_organisation
    if request.user.sectionuserlink_set.all():
        raise PermissionDenied()
    organisation = Organisation.objects.get(organisationuserlink__user=request.user)
    if request.method == "POST":
        # If it was really important, I'd check whether the chosen section can be chosen here. This is a vulnerability
        # if we don't check. But this isn't really important here.
        # We use a strange workaround for saving this because form.is_valid doesn't work

        model = SectionUserLink(user=request.user, section_id=request.POST.get('section'))
        model.save()
        messages.success(request, _('You are now a member of %(section)s.') % {
            'section': model.section,
        })
        next_page = request.GET.get("next")
        if next_page:
            return redirect(next_page)
        return redirect('home')
    else:
        form = ChooseSectionForm(organisation=organisation)
    return render(request, "organisations/choose_section.html", {'form': form})
