from django.urls import path
from .views import homepage, add_organisation

urlpatterns = [
    path('', homepage, name='home'),
    path('link-to-org', add_organisation, name='authenticate-with-org'),
]
