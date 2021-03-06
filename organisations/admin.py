from .forms import OrganisationCreateForm, OrganisationChangeForm, AdminPasswordChangeForm
from .models import Organisation, Section, SectionAdministrator
from surveys.models import SurveySectionLink
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import admin, messages
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.http import Http404, HttpResponseRedirect
from django.urls import path, reverse
from django.contrib.admin.options import IS_POPUP_VAR
from django.views.decorators.debug import sensitive_post_parameters
from django.template.response import TemplateResponse
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


"""
I do not know of a way to make recursive inlines. So this is the next best solution. This way you can only make
section trees of 6 levels deep though. If you need a deeper tree. You should use the sectionmodel directly
"""


class SectionInlineUnderSection(NestedTabularInline):
    model = Section
    extra = 0
    exclude = ['organisation']


class SectionInlineLevelFive(SectionInlineUnderSection):
    inlines = [SectionInlineUnderSection, ]


class SectionInlineLevelFour(SectionInlineUnderSection):
    inlines = [SectionInlineLevelFive, ]


class SectionInlineLevelThree(SectionInlineUnderSection):
    inlines = [SectionInlineLevelFour, ]


class SectionInlineLevelTwo(SectionInlineUnderSection):
    inlines = [SectionInlineLevelThree, ]


class SectionInlineLevelOne(NestedTabularInline):
    model = Section
    extra = 0
    exclude = ['parent_section']
    inlines = [SectionInlineLevelTwo, ]


class OrganisationAdmin(NestedModelAdmin):
    add_form = OrganisationCreateForm
    form = OrganisationChangeForm
    change_password_form = AdminPasswordChangeForm
    model = Organisation
    list_filter = ['name', ]
    inlines = [SectionInlineLevelOne, ]

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith('password') and super().lookup_allowed(lookup, value)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during organisation creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
                   path(
                       '<path:object_id>/change/password/',
                       self.admin_site.admin_view(self.org_change_password),
                       name='auth_user_password_change',
                   ),
               ] + super().get_urls()

    @sensitive_post_parameters_m
    def org_change_password(self, request, object_id, form_url=''):
        org = Organisation.objects.get(pk=object_id)
        if not self.has_change_permission(request, org):
            raise PermissionDenied
        if org is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(org, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, org, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            org._meta.app_label,
                            org._meta.model_name,
                        ),
                        args=(org.pk,),
                    )
                )
        else:
            form = self.change_password_form(org)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(org.name),
            'adminForm': admin_form,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': org,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(request, 'organisations/change_password.html', context)


class SectionAdministratorInline(admin.StackedInline):
    model = SectionAdministrator
    extra = 0


class SurveyAdministratorInline(admin.StackedInline):
    model = SurveySectionLink
    extra = 0


class SectionAdmin(admin.ModelAdmin):
    model = Section
    inlines = [SectionAdministratorInline, SurveyAdministratorInline, ]


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Section, SectionAdmin)
