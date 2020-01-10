from django.urls import path
from .views import add_organisation

urlpatterns = [
    path('link-to-org', add_organisation, name='authenticate-with-org'),
]
