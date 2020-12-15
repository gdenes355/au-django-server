"""
Definition of urls for au_django_server.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.conf.urls import handler404


urlpatterns = [
    path('', admin.site.urls),
    path('sb/', include('sandbox.urls')),
]
