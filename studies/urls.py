from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DateRecordAPIView,
    ProblemCreateDestroyAPIView,
    ProblemStatusUpdateAPIView,
    StudyModelViewSet,
    StudyNameDuplicatedView,
    UserStudyHomepageAPIView,
    WeekRetrieveAPIView,
)

router = DefaultRouter()
router.register('', StudyModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('study-name-is-unique/<str:study_name>/', StudyNameDuplicatedView.as_view()),
    path('home/<int:study_id>/', UserStudyHomepageAPIView.as_view()),
    path('home/<int:study_id>/<str:solved_at>/', DateRecordAPIView.as_view()),
    path('<int:study_id>/week<int:week_num>/', WeekRetrieveAPIView.as_view()),
    path('<int:study_id>/week<int:week_num>/<int:problem_num>/', ProblemCreateDestroyAPIView.as_view()),
    path('<int:study_id>/week<int:week_num>/<int:problem_num>/commit/', ProblemStatusUpdateAPIView.as_view()),
]
