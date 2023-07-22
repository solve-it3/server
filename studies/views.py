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
from users.models import *
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
    serializers_class = UserStudyHomepageSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, study_name, week_number):
        data = []
        # user, study, week 지정하기
        user = request.user
        study = get_object_or_404(Study, name=study_name)
        week = get_object_or_404(Week, study=study, week_number=week_number)

        # mvp 정하기
        mvp_users = ProblemStatus.objects.filter(
            problem__week=week,
            is_solved=True,
            problem__week__study__name=study_name
        ).values('user__github_id').annotate(
            num_solved=Count('problem')
        ).order_by('-num_solved')

        if mvp_users:
            max_solved_count = mvp_users.first()['num_solved']
            mvp_users = mvp_users.filter(num_solved=max_solved_count).values_list('user__github_id', flat=True)
            mvp_users = list(set(mvp_users))  # 중복된 github_id 제거
            data.extend({'mvp_github_id': github_id} for github_id in mvp_users)
        else:
            data.append({'message': '해당주차에 문제를 푼 사용자는 없다'}, status=status.HTTP_404_NOT_FOUND)

        # 진척도 구하기
        solved_problems = ProblemStatus.objects.filter(
            user=user, problem__week=week, is_solved=True
        ).count()
        total_week_problem = study.problems_in_week
        data.append({'progress': round((solved_problems / total_week_problem) * 100)})

        # 총 푼 문제수 구하기
        data.append({'total_solved_problems': solved_problems})

        # 잔디 색상 기록
        solved_counts = ProblemStatus.objects.filter(
            problem__week__study = study,
            is_solved = True
        ).values('solved_at').annotate(problem_count=Count('problem')).order_by('solved_at')
        jandi ={}
        for entry in solved_counts:
            solved_at = entry['solved_at'].strftime('%Y-%m-%d')
            problem_count = entry['problem_count']
            jandi[solved_at] = problem_count
        data.append(jandi)



        # user별 스터디 목록
        study_list = user.joined_studies.all()
        data.append({'study_list': [study.name for study in study_list]})

        return JsonResponse(data, safe=False)

    
        
# 날짜, 문제 번호, 문제 이름, 푼 사람 , 푼사람의 커밋 내역
class DateRecordAPIView(APIView):
    
    queryset = Study.objects.all()
    serializers_class = DateRecordSerializer
    permission_classes = [AllowAny]
    def get(self, request, solved_at, study_name):
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



