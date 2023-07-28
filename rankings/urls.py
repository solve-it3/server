from django.urls import path, include
from .views import StudyProfileView, StudyRankingView, PersonalProfileView, PersonalRankingView

urlpatterns = [
    path('study/<str:study_name>/', StudyProfileView.as_view()),
    path('study-ranking/', StudyRankingView.as_view()),
    path('profile/', PersonalProfileView.as_view()),
    path('personal-ranking/', PersonalRankingView.as_view()),
]
