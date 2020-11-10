from django.contrib import admin
from django.urls import path
from . import views

from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.home, name='home'),
    path('csv', views.csvHandler, name='csv'),
    # path('download', views.download, name='download'),
    # path('api', views.googleAPI, name='api'),
    # path('url', views.handleUrl, name='handleUrl'),
    path('api', views.List.as_view()),
    path('save', views.saveModel, name='model'),

]
