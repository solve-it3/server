from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from studies.models import Study
from users.models import User
from .serializers import StudyRankingSerializer, StudyProfileSerializer, PersonalSerializer, PersonalRankingSerializer


class StudyProfileView(RetrieveAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Study.objects.get(name = kwargs['study_name'])
        except Study.DoesNotExist:
            return Response({'message': '해당 스터디는 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

class StudyRankingView(ListAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyRankingSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        sorted_data = sorted(serializer.data, key=lambda x: x['rank'])
        return Response(sorted_data)
    

class PersonalProfileView(RetrieveAPIView):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = PersonalSerializer
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PersonalRankingView(ListAPIView):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = PersonalRankingSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request_user': request.user})
        
        sorted_data = sorted(serializer.data, key=lambda x: x['rank'])
        return Response(sorted_data)


# Study 테이블의 데이터를 모두 가져와서 queryset 필드에 저장
# serializer.data : serialize된 data가 담겨있음
# ex) test = [(1, 8), (2, 3), (7, 9), (6, 1), (4, 5)]
# sorted(test) -> 기본 오름차순 정렬
# lambda 식을 활용하여 특정 key를 기준으로 정렬 가능
# sorted(test, key = lambda x : x) -> x를 기준으로 오름차순 정렬
# sorted(test, key = lambda x : x[0]) -> x[0]을 기준으로 오름차순 정렬
# sorted(test, key = lambda x : x[1], reverse=True) -> x[1]을 기준으로 내림차순 정렬
