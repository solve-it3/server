from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    kakao_login,
    FollowView,
    KakaoSignUpView,
    UserDetailView,
    UserUpdateView,
)

urlpatterns = [
    path('detail/<str:backjoon_id>/', UserDetailView.as_view()),
    path('detail-info/', UserUpdateView.as_view()),
    path('follow/<str:backjoon_id>/', FollowView.as_view()),
    path('kakao/code/', kakao_login),
    path('login/', KakaoSignUpView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),

]
