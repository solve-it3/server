from django.urls import path
from .views import ProblemAPIView

urlpatterns = [
    path('<str:study_name>/<int:problem_number>/', ProblemAPIView.as_view())
]