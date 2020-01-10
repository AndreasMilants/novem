from django.urls import path
from .views import homepage, survey_view

urlpatterns = [
    path('', homepage, name='home'),
    path('survey/<page>', survey_view, name='survey'),
]
