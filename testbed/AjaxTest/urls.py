from django import urls
from django.urls import path
from django.urls.conf import include, re_path
from . import views
urlpatterns = [
    path('ajax', views.index, name = 'index')
]