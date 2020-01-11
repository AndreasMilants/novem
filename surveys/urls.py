from django.urls import path
from .views import homepage, survey_view, get_personal_survey_stats, personal_statistics

urlpatterns = [
    path('', homepage, name='home'),
    path('survey/<page>', survey_view, name='survey'),
    path('statistics', personal_statistics, name='personal-statistics'),
    path('see_statistics/<survey>', get_personal_survey_stats, name='see-personal-statistics'),
]
