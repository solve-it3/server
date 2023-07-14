from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('kakao/code/', kakao_login),
    path('login/', KakaoSignUpView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('detail-info/', UserUpdateView.as_view()),
]
