from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from organisations.forms import OrganisationAuthenticationForm
from organisations.models import OrganisationUserLink, Organisation
from django.utils.translation import ugettext_lazy as _


@login_required
def homepage(request):
    if not request.user.organisationuserlink_set.all():
        return redirect('authenticate-with-org')
    return render(request, 'home.html', {})


@login_required
def add_organisation(request):
    if request.method == "POST":
        form = OrganisationAuthenticationForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            org_user_link = OrganisationUserLink(organisation=Organisation.objects.get(name=model.organisation), user=request.user)
            org_user_link.save()
            messages.success(request, _('You are now a member of %(organisation)s.') % {
                'organisation': model.organisation,
            })
            return redirect('home')
    else:
        form = OrganisationAuthenticationForm()
    return render(request, "organisations/authenticate_organisation.html", {"form": form})

