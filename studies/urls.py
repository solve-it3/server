from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('', StudyModelViewSet)

# register를 study-create로 StudyModelViewSet으로 해줬습니다

urlpatterns = [
    path('', include(router.urls)),
    path('study-name-is-unique/', StudyNameDuplicatedView.as_view()),
    path('study-date-record/<str:study_name>/<str:solved_at>/',
        DateRecordAPIView.as_view()),
    path('home/<str:study_name>/', UserStudyHomepageAPIView.as_view()),
    path('<str:study_name>/week<int:week_num>/', WeekRetrieveAPIView.as_view()),
    path('<str:study_name>/week<int:week_num>/problem/',ProblemCreateAPIView.as_view())
]
