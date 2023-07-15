from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns =[
    path('study-name-is-unique/', StudyNameDuplicatedView.as_view())

]