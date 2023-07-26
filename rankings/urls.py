from django.urls import path, include
from .views import RankingView

urlpatterns = [
    path('ranking/<str:study_name>/', RankingView.as_view()),
]
