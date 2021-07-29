from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('fetch', views.fetch, name="fetch"),
    path('display', views.display, name="display")
]