from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from studies.models import Study
from users.models import User
from .serializers import StudyRankingSerializer, StudyProfileSerializer, PersonalSerializer, PersonalRankingSerializer


# 스터디 프로파일을 볼 수 있는 API
class StudyProfileView(RetrieveAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Study.objects.get(id=kwargs['study_id'])
        except Study.DoesNotExist:
            return Response({'message': '해당 스터디는 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
        #serializer를 지정해주는데, study이름이 같은 객체를 넣었을때 serializer를 가져온다
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
# 스터디 랭킹을 볼 수 있는 API
class StudyRankingView(ListAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyRankingSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        #list를 위해서 get_serializer를 통해 querysey이 many to many형식으로 맞춰준다
        serializer = self.get_serializer(queryset, many=True)
        #위에서 정제한 serializer의 데이터를 rank순으로 정리를 한다
        sorted_data = sorted(serializer.data, key=lambda x: x['rank'])
        return Response(sorted_data)
    
# user의 profile을 볼 수 있는 API   
class PersonalProfileView(RetrieveAPIView):
    #admin이 아닌 놈만을 봐야한다
    queryset = User.objects.filter(is_staff=False)
    serializer_class = PersonalSerializer
    permission_classes = [IsAuthenticated, ]

    #객체를 user로 지정하고 그대로 돌려준다
    def retrieve(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# 개인랭킹의 순위를 돌려준다
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
