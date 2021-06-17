from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('commonwords/', views.common_words),
    path('displaycommonwords/', views.display_common_words)
]