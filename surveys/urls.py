from django.urls import path
from .views import homepage, survey_view, get_personal_statistics

urlpatterns = [
    path('', homepage, name='home'),
    path('survey/<page>', survey_view, name='survey'),
    path('statistics', get_personal_statistics, name='personal-statistics'),
]
