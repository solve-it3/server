import datetime
import requests

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Study, Week, Problem, ProblemStatus
from .serializers import (
    DateRecordSerializer,
    ProblemCreateSerializer,
    StudyBaseSerializer,
    StudyNameDuplicatedSerializer,
    UserStudyHomepageSerializer,
    WeekBaseSerializer,

)


def calculate(solved_count):
    if solved_count == 0:
        return 1
    elif 0 < solved_count <= 25:
        return 2
    elif 25 < solved_count <= 50:
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
            # Study의 객체들에서 name이 data.get한것의 name을 가져온다
            # 이 객체가 실패하면 False, 유일하면 True를 가져온다
            Study.objects.get(name=request.data.get('name'))
            instance['is_unique'] = False

        except Study.DoesNotExist:
            instance['is_unique'] = True

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class StudyModelViewSet(ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudyBaseSerializer
    permission_classes = [IsAuthenticated]


# user를 가져온다.
class UserStudyHomepageAPIView(APIView):
    queryset = ProblemStatus.objects.all()
    serializers_class = UserStudyHomepageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, study_name):
        data = dict()

        # user, study, week 지정하기
        user = request.user
        study = get_object_or_404(Study, name=study_name)
        week = get_object_or_404(
            Week, study=study, week_number=study.current_week)

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
            mvp_users = mvp_users.filter(num_solved=max_solved_count).values_list(
                'user__github_id', flat=True)
            mvp_users = list(set(mvp_users))  # 중복된 github_id 제거
            mvp = [github_id for github_id in mvp_users]
        else:
            mvp = None
        data['mvp'] = mvp

        # 진척도 구하기
        solved_problems = ProblemStatus.objects.filter(
            user=user, problem__week=week, is_solved=True
        ).count()
        total_week_problem = study.problems_in_week
        data['progress'] = round((solved_problems / total_week_problem) * 100)

        # 총 푼 문제수 구하기
        data['total_solved_problems'] = solved_problems

        # 잔디 색상 기록
        solved_counts = ProblemStatus.objects.filter(
            problem__week__study=study,
            is_solved=True
        ).values('solved_at').annotate(problem_count=Count('problem')).order_by('solved_at')
        jandi = {}
        for entry in solved_counts:
            solved_at = entry['solved_at'].strftime('%Y-%m-%d')
            problem_count = entry['problem_count']
            jandi[solved_at] = problem_count
        data['jandi'] = jandi

        # user별 스터디 목록
        study_list = user.joined_studies.all()
        data['study_list'] = [study.name for study in study_list]

        return JsonResponse(data, safe=False)


# 날짜, 문제 번호, 문제 이름, 푼 사람 , 푼사람의 커밋 내역
class DateRecordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solved_at, study_name):
        # 스터디 이름 예외처리
        try:
            study = Study.objects.get(name=study_name)
        except Study.DoesNotExist:
            return JsonResponse({"message": "그런 스터디는 없소"}, status=status.HTTP_404_NOT_FOUND)
        
        # 스터디의 멤버 리스트
        members = study.members.all()

        # 스터디 유저들의 problemstatus 불러오기
        problem_statuses = ProblemStatus.objects.filter(
            user__in=members,
            solved_at=solved_at, 
            is_solved=True
        )

        # problem status 들의 문제 번호 리스트 (중복 X)
        problem_list = list(set(status.problem.number for status in problem_statuses))

        # 응답으로 넘겨줄 리스트 선언
        problem_data = list()

        # 문제 번호마다 푼 사람 추가하는 반복문
        for problem_number in problem_list:
            # 해당 스터디의 해당 문제 쿼리셋 불러오기
            problem = Problem.objects.get(
                week__study=study,
                number=problem_number
            )

            user_list = list()
            for user in problem.get_solvers():
                # commit url 불러오기, 없으면 null
                try:
                    commit_url = ProblemStatus.objects.get(
                        problem=problem,
                        user=user,
                        is_solved=True,
                        solved_at=solved_at
                    ).commit_url
                except ProblemStatus.DoesNotExist:
                    commit_url = None

                user_list.append({
                    "backjoon_id": user.backjoon_id,
                    "profile_image": user.profile_image,
                    "commit_url": commit_url,
                })

            problem_data.append({
                "problem_number": problem.number,
                "problem_name": problem.name,
                "problem_url": problem.url,
                "solvers": user_list
            })

        return JsonResponse({"data": problem_data})


class WeekRetrieveAPIView(generics.RetrieveAPIView):
    # week 싹다 가져오고
    queryset = Week.objects.all() #필수
    # 하나만 있어야함
    serializer_class = WeekBaseSerializer #필수
    # 로그인 필요
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    # Get요청에는 retrieve가 실행이 됨.
    def retrieve(self, request, *args, **kwargs):
        # url 속에 있는 변수들
        week_num = kwargs['week_num']
        study_name = kwargs['study_name']

        # 예외처리만 하는 것
        try:
            study = Study.objects.get(name=study_name)
        except Study.DoesNotExist:
            return Response({'message': '그런 이름을 가진 스터디는 없소!'}, status=status.HTTP_404_NOT_FOUND)

        # 필터링 get_or_create는 return 값이 두개!
        week, created = Week.objects.get_or_create(
            study=study,
            week_number=week_num
        )

        # 존재하지 않았을 경우
        if created:
            # 전주차것 가져와서
            last_week = Week.objects.get(study=study, week_number=week_num-1)
            week.start_date = last_week.end_date + datetime.timedelta(1)
            week.end_date = last_week.end_date + datetime.timedelta(7)
            # create는 위에서 되었고 여기서 update
            week.save()
        # serializer_class에 해당하는 serializer를 가져온다.
        # jwt Token이 있어야 request.user를 쓸 수 있다.
        serializer = self.get_serializer(week, context={'request_user': request.user})
        return Response(serializer.data)


class ProblemCreateDestroyAPIView(generics.GenericAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # url 정보 가져오기
        study_name = kwargs["study_name"]
        week_number = kwargs["week_num"]
        problem_num = kwargs["problem_num"]
        
        study_id = Study.objects.get(name=study_name).id
        week_id = Week.objects.get(study=study_id, week_number=week_number).id
        
        # 이미 추가된 문제일 경우 예외처리
        try:
            Problem.objects.get(week=week_id, number=problem_num)
            return Response({"message":"이미 추가한 문제입니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Problem.DoesNotExist:
            pass

        # 백준에서 문제 가져오기
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_num}"
        response = requests.get(url=url)
        if response.status_code != 200 :
            return Response({"message": "없는 문제 번호입니다."}, status=status.HTTP_404_NOT_FOUND)
        else :
            response_json = response.json()

        # 저장할 정보 저장
        data = {
            "number": problem_num,
            "name": response_json.get("titleKo"),
            "url": f"https://acmicpc.net/problem/{problem_num}",
            "algorithms": response_json["tags"][0]["displayNames"][0]["name"],
            "week": week_id
        }

        # 유효성 검사 후 저장
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 헤더 추가
        try:
            headers = {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            headers = {}
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def delete(self, request, *args, **kwargs):
        # url 정보 가져오기
        study_name = kwargs["study_name"]
        week_number = kwargs["week_num"]
        problem_num = kwargs["problem_num"]

        # study 찾기
        try:
            study = Study.objects.get(name=study_name)
        except Study.DoesNotExist:
            return Response({"message": "해당 스터디를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # week 찾기
        try:
            week = Week.objects.get(study=study, week_number=week_number)
        except Week.DoesNotExist:
            return Response({"message": "추가하지 않은 주차입니다."}, status=status.HTTP_404_NOT_FOUND)

        # problem 찾기
        try:
            problem = Problem.objects.get(week=week, number=problem_num)
        except Problem.DoesNotExist:
            return Response({"message": "이미 삭제했거나 추가한 적 없는 문제 번호입니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 해당 문제 삭제
        problem.delete()

        return Response({'message': '삭제 완료'}, status=status.HTTP_204_NO_CONTENT)
