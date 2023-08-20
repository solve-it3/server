from jamo import h2j, j2hcj
from operator import itemgetter

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from studies.models import Study
from users.models import User
from .serializers import UserSerializer, StudySerializer


class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def similarity(value, query):
        value = value.lower()
        query = query.lower()
        return sum(1 for _ in j2hcj(h2j(value)).split(query)) - 1

    @staticmethod
    def process_hangeul(value, query):
        value = value.lower()
        query = query.lower()
        return query in j2hcj(h2j(value))
    
    def filter_queryset(self, queryset, fields, query):
        result = [
            (obj, max(
                self.similarity(getattr(obj, field), query)
                if getattr(obj, field) else 0
                for field in fields
            ))
            for obj in queryset if any(
                getattr(obj, field) and self.process_hangeul(getattr(obj, field), query)
                for field in fields
            )
        ]
        # 유사도에 따라 정렬하고, 객체만 추출
        return [item[0] for item in sorted(result, key=itemgetter(1), reverse=True)]
    
    def filter_user(self, query):
        return self.filter_queryset(
            User.objects.filter(is_staff=False, is_open=True),
            ['backjoon_id', 'github_id', 'company'],
            query
        )

    def filter_study(self, query):
        return self.filter_queryset(
            Study.objects.filter(is_open=True),
            ['name'],
            query
        )
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query')
        processed_query = j2hcj(h2j(query))

        return Response({
            "users": UserSerializer(self.filter_user(processed_query), many=True).data,
            "studies": StudySerializer(self.filter_study(processed_query), many=True).data
        })
