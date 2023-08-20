from django.urls import path

from .views import (
    StudyProfileView, 
    StudyRankingView,
    PersonalProfileView, 
    PersonalRankingView,
)

urlpatterns = [
    path('personal-ranking/', PersonalRankingView.as_view()),
    path('profile/', PersonalProfileView.as_view()),
    path('study/<int:study_id>/', StudyProfileView.as_view()),
    path('study-ranking/', StudyRankingView.as_view()),
]
