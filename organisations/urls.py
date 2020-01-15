from django.urls import path
from .views import link_to_organisation

urlpatterns = [
    path('link-to-org', link_to_organisation, name='authenticate-with-org'),
]
