from django.urls import path
from . import views


urlpatterns = [
    path('', views.welcome),
    path('search/', views.index),
    path('commonwords/', views.common_words),
    path('displaycommonwords/', views.display_common_words),
    path('cooccurance/', views.cooccurance_words_view),
    path('cooccurance_words/', views.cooccurance_words),
    path('sentimentall/', views.sentiment_all),
    path('sentimentgraph/', views.sentiment_graph),
    path('filter/', views.FilterView)
]