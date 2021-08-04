from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.index, name="index"),
    path('display', views.display, name="display"),
    path('initialize', views.initialize, name="initialize"),
    path('combineData', views.combineData, name="combineData")
]

urlpatterns += staticfiles_urlpatterns()