from django.shortcuts import render
from rest_framework.generics import ListAPIView
from studies.models import Study
from .serializers import RankingSerializer, StudyRankingSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
class RankingView(ListAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyRankingSerializer
    permission_classes = [AllowAny, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # def filter_queryset(self, request, queryset, view):
        #     return queryset.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        sorted_data = sorted(data, key=lambda x: x['problem_count'], reverse=True)

        i = 1
        for data in sorted_data:
            data['rank'] = i
            i += 1
        instance = {}
        instance['study_ranking'] = sorted_data

        response = RankingSerializer(instance)
        return Response(response.data)

# Study 테이블의 데이터를 모두 가져와서 queryset 필드에 저장
# serializer.data : serialize된 data가 담겨있음
# ex) test = [(1, 8), (2, 3), (7, 9), (6, 1), (4, 5)]
# sorted(test) -> 기본 오름차순 정렬
# lambda 식을 활용하여 특정 key를 기준으로 정렬 가능
# sorted(test, key = lambda x : x) -> x를 기준으로 오름차순 정렬
# sorted(test, key = lambda x : x[0]) -> x[0]을 기준으로 오름차순 정렬
# sorted(test, key = lambda x : x[1], reverse=True) -> x[1]을 기준으로 내림차순 정렬