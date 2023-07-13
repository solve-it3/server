from django.urls import path, include
from .views import *

urlpatterns = [
    path('kakao/', kakao_login),
    path('kakao/callback/', kakao_callback),
]
