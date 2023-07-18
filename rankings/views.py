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
