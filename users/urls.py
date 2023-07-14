from django.urls import path, include
from .views import *

urlpatterns = [
    path('kakao/code/', kakao_login),
    path('login/', KakaoSignUpView.as_view(), name='kakao_login'),
]
