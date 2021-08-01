from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('display', views.display, name="display"),
    path('initialize', views.initialize, name="initialize"),
    path('combineData', views.combineData, name="combineData")
]