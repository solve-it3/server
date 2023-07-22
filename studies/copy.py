from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, permission_classes
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView, View
from rest_framework import viewsets
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# Create your views here.

def calculate(solved_count):
    if solved_count ==0:
        return 1
    elif 0< solved_count <=25:
        return 2
    elif 25 < solved_count <= 50 :
        return 3
    elif 50 < solved_count <= 75:
        return 4
    else:
        return 5 

class StudyNameDuplicatedView(generics.RetrieveAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyNameDuplicatedSerializer
    # 보는 것만 해야하니까 RetrieveAPIView만 만들어준다
    # retrieve를 오버라이딩해준다
    def retrieve(self, request, *args, **kwargs):
        # instance는 딕셔너리 json파일 형태로 하고
        instance = {}
        try:
            #Study의 객체들에서 name이 data.get한것의 name을 가져온다
            #이 객체가 실패하면 False, 유일하면 True를 가져온다
            Study.objects.get(name=request.data.get('name'))
            instance['is_unique'] = False

        except Study.DoesNotExist:
            instance['is_unique'] = True

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreatStudyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Study.objects.all()
    serializer_class = CreateStudySerializer

class StudyModelViewSet(ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudyBaseSerializer
    permission_classes = [AllowAny,]


#user를 가져온다. 
class UserStudyHomepageAPIView(APIView):
    queryset = ProblemStatus.objects.all()
    serializers_class = MVPSerializer
    permission_classes = [AllowAny]


# 그 주차의 문제를 푼 개수가 가장 많은 사람을 뽑아야한다. 
# 그 수가 여러명이면 어느정도까지 보여줄 지도 정해야한다
class MVPAPIView(APIView):
    queryset = ProblemStatus.objects.all()
    serializers_class = MVPSerializer
    permission_classes = [AllowAny]
    def get(self, request, week_number, study_name):
        study = get_object_or_404(Study, name=study_name)
        week = get_object_or_404(Week, study=study, week_number=week_number)
        mvp_user = ProblemStatus.objects.filter(
            problem__week = week,
            is_solved = True,
            problem__week__study__name = study_name
        ).values('user__github_id').annotate(
            num_solved = Count('problem')
        ).order_by('-num_solved').first()

        if mvp_user:
            github_id = mvp_user['user__github_id']
            return Response({'github_id':github_id})
        else:
            return Response({'message': '해당주차에 문제를 푼 사용자는 없다'}, status=status.HTTP_404_NOT_FOUND)


class ProgressAPIView(APIView):
    queryset = ProblemStatus.objects.all()
    serializers_class = ProgressSerializer
    permission_classes =[AllowAny]
    def get(self, request,user_name, week_number, study_name):
        user = get_object_or_404(User, backjoon_id = user_name)
        study = get_object_or_404(Study, name=study_name)
        week = get_object_or_404(Week, study=study, week_number=week_number)
        solved_problems = ProblemStatus.objects.filter(
            user = user, problem__week=week, is_solved=True).count()
        total_week_problem = study.problems_in_week
        return JsonResponse({'progress' : round((solved_problems/total_week_problem)*100)})
        
class UserTotalProblemAPIView(APIView):
    queryset = ProblemStatus.objects.all()
    serializers_class=UserTotalProblemSerializer
    permission_classes = [AllowAny]
    def get(self, request, user_name, study_name):
        user = get_object_or_404(User, backjoon_id = user_name)
        solved_problem = ProblemStatus.objects.filter(
            user=user, is_solved=True).count()
        return JsonResponse({'solved_problem':solved_problem})
        
# 날짜, 문제 번호, 문제 이름, 푼 사람 , 푼사람의 커밋 내역
class DateRecordAPIView(APIView):
    
    queryset = Study.objects.all()
    serializers_class = DateRecordSerializer
    permission_classes = [AllowAny]
    def get(self, request, solved_at, study_name):
        user =request.user
        problem_list = ProblemStatus.objects.filter(solved_at=solved_at, is_solved=True)
        problem_data =[]
        for problems in problem_list:
            problem = problems.problem
            problem_data.append({
                'sovled_at' : solved_at,
                'problem_number': problem.number,
                'problem_name' : problem.name,
                'user' : problems.user.backjoon_id,
                'commit_url' : problems.commit_url,
                'kakao_id' : problems.user.kakao_id,
                'image_file' : problems.user.profile_image,
            })
    
        return JsonResponse({"date_record" : problem_data})



# 잔디 색상 기록하도록 함
class JandiAPIView(APIView):
    queryset = Study.objects.all()
    permission_classes = [AllowAny]
    serializer_classes = JandiSerializer
    def get(self, request, study_name):
        study = get_object_or_404(Study, name=study_name)

        # 해당 스터디의 모든 주차 가져오기
        weeks = Week.objects.filter(study=study)

        # 스터디원 수 계산
        members_count = study.members.count()

        # 날짜별로 스터디원들이 푼 문제 수 계산
        solved_data_by_date = []

        for week in weeks:
            solved_counts = ProblemStatus.objects.filter(
                problem__week=week, is_solved=True
            ).values('solved_at').annotate(solved_count=Count('user')).order_by('solved_at')

            for data in solved_counts:
                solved_count = data['solved_count']
                level = calculate(solved_count)
                data['level'] = level

                # 스터디원 수로 나누어서 평균 레벨 계산
                data['average_level'] = round(solved_count / members_count)

                solved_data_by_date.append(data)

        return JsonResponse({'solved_data': solved_data_by_date})
    
class StudyChangeAPIView(APIView):
    queryset = Study.objects.all()
    permission_classes = [AllowAny]
    serializer_classes = StudyChangeSerializer
    def get(self, request, user_name):
        user = get_object_or_404(User, backjoon_id = user_name)
        #user랑 studies랑 many to many join을 하고 values값들중 name을 가져온다
        study_names = user.joined_studies.values_list('name', flat=True)
        return JsonResponse({'study_names': list(study_names)})
    
