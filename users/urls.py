from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rankings.views import PersonalProfileView
from .views import (
    kakao_login,
    FollowView,
    NotificationAPIView,
    KakaoSignUpView,
    StudyAPIView,
    UserUpdateView,
)

urlpatterns = [
    path('mypage/<str:backjoon_id>/profile/', PersonalProfileView.as_view()),
    path('mypage/<str:backjoon_id>/notification/', NotificationAPIView.as_view()),
    path('mypage/<str:backjoon_id>/study/', StudyAPIView.as_view()),
    path('detail-info/', UserUpdateView.as_view()),
    path('follow/<str:backjoon_id>/', FollowView.as_view()),
    path('kakao/code/', kakao_login),
    path('login/', KakaoSignUpView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),

]
