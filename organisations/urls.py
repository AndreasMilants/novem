from django.urls import path
from .views import link_to_organisation, link_to_section

urlpatterns = [
    path('link-to-org', link_to_organisation, name='authenticate-with-org'),
    path('link-to-section', link_to_section, name='link-to-section'),
]
