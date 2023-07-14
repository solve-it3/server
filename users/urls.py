from django.urls import path, include
from .views import *

urlpatterns = [
    path('kakao/', kakao_login),
    path('kakao-login/', KakaoSignUpView.as_view(), name='kakao_login'),
]
