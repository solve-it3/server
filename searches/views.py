from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, StudySerializer
from studies.models import Study
from users.models import User


class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query')
        users = User.objects.filter(is_staff=False
        ).filter(is_open=True
        ).filter(Q(backjoon_id__contains=query)
            | Q(github_id__contains=query)
            | Q(company__contains=query)
        )
        studies = Study.objects.filter(
            name__contains=query
        )

        response = {
            "users": UserSerializer(users, many=True).data,
            "studies": StudySerializer(studies, many=True).data
        }
        return Response(response)
