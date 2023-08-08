from django.urls import path

from .views import SearchAPIView

urlpatterns = [
    path("", SearchAPIView.as_view()),

]