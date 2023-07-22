from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework import routers

router = DefaultRouter()
router.register('study-create', StudyModelViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('study-name-is-unique/', StudyNameDuplicatedView.as_view()),
    path('study-date-record/<str:study_name>/<str:solved_at>', DateRecordAPIView.as_view()),
    path('study-homepage/<str:study_name>/<int:week_number>/', UserStudyHomepageAPIView.as_view()),
]   