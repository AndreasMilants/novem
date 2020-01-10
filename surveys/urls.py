from django.urls import path
from .views import homepage, add_organisation, survey_view

urlpatterns = [
    path('', homepage, name='home'),
    path('link-to-org', add_organisation, name='authenticate-with-org'),
    path('survey/<page>', survey_view, name='survey'),
]
