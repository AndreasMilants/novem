from django.urls import path
from .views import homepage_view, survey_view, personal_statistics_view, admin_statistics_view, \
    admin_statistics_section_view, admin_statistics_users_view, admin_statistics_user_view

urlpatterns = [
    path('', homepage_view, name='home'),
    path('survey/<page>', survey_view, name='survey'),
    path('statistics/<section>', personal_statistics_view, name='personal-statistics'),
    path('admin-statistics', admin_statistics_view, name='admin-statistics'),
    path('admin-statistics-section/<section>', admin_statistics_section_view, name='admin-statistics-section'),
    path('admin-statistics-users/<section>', admin_statistics_users_view, name='admin-statistics-users'),
    path('admin-statistics-user/<user>', admin_statistics_user_view, name='admin-statistics-user'),
]
