from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    # path('fetch', views.fetch, name="fetch"),
    path('display', views.display, name="display"),
    path('initialize', views.initialize, name="initialize"),
    path('call1', views.call1, name="call1"),
    path('call2', views.call2, name="call2"),
    path('call3', views.call3, name="call3"),
    path('call4', views.call4, name="call4"),
    path('combineData', views.combineData, name="combineData")
]