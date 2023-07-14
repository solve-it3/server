from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    kakao_login,
    KakaoSignUpView,
    UserUpdateView,
)

urlpatterns = [
    path('detail-info/', UserUpdateView.as_view()),
    path('kakao/code/', kakao_login),
    path('login/', KakaoSignUpView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),

]
