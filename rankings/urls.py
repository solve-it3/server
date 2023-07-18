from django.urls import path, include
from .views import RankingView

urlpatterns = [
    path('ranking/', RankingView.as_view()),
]