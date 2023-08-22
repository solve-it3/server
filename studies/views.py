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

from users.models import User, Notification
from .models import Study, Week, Problem, ProblemStatus
from .serializers import (
    ProblemCreateSerializer,
    ProblemStatusSerializer,
    StudyBaseSerializer,
    StudyResponseSerializer,
    UserStudyHomepageSerializer,
    WeekBaseSerializer,

)

# 단계를 만들어주는 함수
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
    

def wrong_study_response():
    study_response = StudyResponseSerializer(Study.objects.all(), many=True).data
    return Response(
        {
            "message": "해당 id값을 가진 스터디는 없습니다.",
            "study": study_response
        }, 
        status=status.HTTP_404_NOT_FOUND
    )


# study name이 중복이 되는지 확인을 해주는 API -> 하나를 확인만 하니까 Retrieve만 해주면 된다
class StudyNameDuplicatedView(APIView):
    permission_classes = [IsAuthenticated]
    # 굳이 serializer 사용하지 않고 objects.get을 통해서 kwargs로 그 이름에 대한 것이 존재하는지 확인만헤서 response로 전달을 해주면 된다
    def get(self, request, *args, **kwargs):
        study_name = kwargs['study_name']
        is_unique = not Study.objects.filter(name=study_name).exists()
        return Response({'is_unique': is_unique})


#CRUD 다 구현해주는 ModelViewSet -> url 속 name을 통해 찾는다.
class StudyModelViewSet(ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudyBaseSerializer
    permission_classes = [IsAuthenticated]


# user를 가져온다.
class UserStudyHomepageAPIView(APIView):
    queryset = ProblemStatus.objects.all()
    serializers_class = UserStudyHomepageSerializer
    permission_classes = [IsAuthenticated]

    # 정보를 가져오기만 하면 된다.
    def get(self, request, study_id):
        #data는 dict()형식으로 만들어준다
        data = dict()

        # user, study, week 지정하기
        # user는 request로 지정한 user를 가져온다
        user = request.user
        study = get_object_or_404(Study, id=study_id)
        week = get_object_or_404(Week, study=study, week_number=study.current_week)

        data['request_user_joined'] = user in study.members.all()

        # mvp 정하기

        #problem foreign key의 week와 week가 같고 문제를 풀었고, 그 스터디 이름이 같을때
        #user foreign key의 github아이디를 prblem의 기준으로 정렬한것을 가져온 객체
        mvp_users = (
            ProblemStatus.objects.filter(
                problem__week=week,
                is_solved=True,
                problem__week__study__id=study_id
            )
            .values('user__github_id')
            #mvp_user는 user의 github_id로 분류해서 가져오는데 num_solved라는 count를 사용해서 이걸 역순으로 가장 많은 것을 가져온다
            .annotate(num_solved=Count('problem'))
            .order_by('-num_solved')
        )

        if mvp_users:
            # mvp_users는 objects로 만들어진 집합이므로 첫번째꺼의 num_solved를 뽑아준다
            max_solved_count = mvp_users.first()['num_solved']
            mvp_users = mvp_users.filter(num_solved=max_solved_count).values_list('user__github_id', flat=True)
            mvp = list(set(mvp_users))
        else:
            mvp = None
        data['mvp'] = mvp

        # 진척도 구하기
        solved_problems = ProblemStatus.objects.filter(
            # foreign key는 __ 로표시한다. 
            user=user, problem__week=week, is_solved=True
        ).count()
        
        total_week_problem = study.problems_in_week
        data['progress'] = round((solved_problems / total_week_problem) * 100)

        # 총 푼 문제수 구하기
        data['total_solved_problems'] = solved_problems

        # 잔디 색상 기록
        solved_counts = (
            ProblemStatus.objects.filter(
                problem__week__study=study,
                is_solved=True,
            )
            .values('solved_at')
            .annotate(problem_count=Count('problem'))
            .order_by('solved_at')
        )
        jandi = {entry['solved_at'].strftime('%Y-%m-%d'): entry['problem_count'] for entry in solved_counts}
        data['jandi'] = jandi

        # user별 스터디 목록
        study_list = user.joined_studies.all()
        data['study_list'] = StudyResponseSerializer(study_list, many=True).data

        return JsonResponse(data, safe=False)


# 날짜, 문제 번호, 문제 이름, 푼 사람 , 푼사람의 커밋 내역
class DateRecordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solved_at, study_id):
        # 스터디 이름 예외처리
        try:
            study = Study.objects.get(id=study_id)
        except Study.DoesNotExist:
            return wrong_study_response()

        # 스터디 유저들의 problemstatus 불러오기
        problem_statuses = ProblemStatus.objects.filter(
            #user객체가 study.members.all()에 속하는 하나의 객체일때 즉 모든 user에 대해서
            problem__week__study=study,
            user__in=study.members.all(),
            solved_at=solved_at, 
            is_solved=True
        )
        # 위의 problem status와 같다
        # problem status 들의 문제 번호 리스트 (중복 X)
        problem_list = list(set(status.problem.number for status in problem_statuses))

        # 응답으로 넘겨줄 리스트 선언
        problem_data = list()

        # 문제 번호마다 푼 사람 추가하는 반복문
        # problem_number는 그 주차에 풀었다고 되어있는 문제들 전체다
        for problem_number in problem_list:
            # 해당 스터디의 해당 문제 쿼리셋 불러오기
            # 한 문제당 그 문제에 해당하는 걸 들고오기
            problem = Problem.objects.get(
                week__study=study,
                number=problem_number
            )
            user_list = list()
            problem_statuses_for_problem = problem_statuses.filter(problem=problem, solved_at=solved_at)
            
            for status in problem_statuses_for_problem:
                user = status.user
                # commit url 불러오기, 없으면 null
                commit_url = status.commit_url or None

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

        return Response(problem_data)


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
        # url 속에 있는 변수들 -> 넣어줘야 하는 것들
        week_num = kwargs['week_num']
        study_id = kwargs['study_id']

        # 예외처리만 하는 것
        try:
            study = Study.objects.get(id=study_id)
        except Study.DoesNotExist:
            return wrong_study_response()

        # 필터링 get_or_create는 return 값이 두개!
        week, created = Week.objects.get_or_create(
            study=study,
            week_number=week_num
        )

        # 존재하지 않았을 경우
        if created:
            # 전주차것 가져와서
            last_week = Week.objects.get(study=study, week_number=week_num-1)
            #timedelta를 통해서 확인 가능하다
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
        # 하나씩 지정해준다는 느낌
        study_id = kwargs["study_id"]
        week_number = kwargs["week_num"]
        problem_num = kwargs["problem_num"]
        
        week_id = Week.objects.get(study=study_id, week_number=week_number).id
        
        # 이미 추가된 문제일 경우 예외처리
        # week자체의 id를(하나일때)가져와서 설정해도 괜찮다
        try:
            Problem.objects.get(week=week_id, number=problem_num)
            return Response({"message":"이미 추가한 문제입니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Problem.DoesNotExist:
            pass
        

        # 백준에서 문제 가져오기
        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_num}"
        # response에 url정보를 가져온것을 담는ㄷ
        response = requests.get(url=url)
        if response.status_code != 200 :
            return Response({"message": "없는 문제 번호입니다."}, status=status.HTTP_404_NOT_FOUND)
        else :
            # json파일로 전달을 해준다
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
        
        # problemstatus만들어주기
        problem = Problem.objects.get(week=week_id, number=problem_num)
        # many to many여서 .all()해야함
        members = Study.objects.get(id=study_id).members.all()
        for member in members:
            ProblemStatus(problem=problem, user=member, solved_at=None).save()

        # 헤더 추가
        try:
            #어떤 필드에 대해 리디렉션 URI를 제공할 것인지를 나타내는 설정 변수
            headers = {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            headers = {}
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def delete(self, request, *args, **kwargs):
        # url 정보 가져오기
        study_id = kwargs["study_id"]
        week_number = kwargs["week_num"]
        problem_num = kwargs["problem_num"]

        # study 찾기
        try:
            study = Study.objects.get(id=study_id)
        except Study.DoesNotExist:
            return wrong_study_response()

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


class ProblemStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = ProblemStatus.objects.all()
    serializer_class = ProblemStatusSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        study_id = kwargs["study_id"]
        week_number = kwargs["week_num"]
        problem_num = kwargs["problem_num"]
        member = request.user
        commit_url = request.data["commit_url"]
        current_time = datetime.datetime.now()

        # study 찾기
        try:
            study = Study.objects.get(id=study_id)
        except Study.DoesNotExist:
            return wrong_study_response()

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
        
        problem_status = ProblemStatus.objects.get(problem=problem, user=member)
        problem_status.commit_url = commit_url
        problem_status.solved_at = current_time
        # 변경사항을 저장
        problem_status.save()
        
        return Response({"message": "Commit반영함"}, status=status.HTTP_202_ACCEPTED)


class StudyJoinAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request_user = request.user
        try:
            study = Study.objects.get(id=kwargs['study_id'])
        except Study.DoesNotExist:
            return wrong_study_response()

        try:
            Notification.objects.get(
                receiver=study.leader,
                sender=request_user,
                study=study,
                title="합류 요청"
            )
            return Response({"message": "이미 보낸 요청입니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Notification.DoesNotExist:
            pass

        if request_user in study.members.all():
            return Response({"message": "이미 합류해있는 멤버입니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            Notification.create_notification(request_user, study, "join")
            return Response({"message": "합류 요청 완료"}, status=status.HTTP_201_CREATED)
    

class StudyJoinAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_user = request.user

        try:
            joined_user = User.objects.get(backjoon_id=kwargs['backjoon_id'])
        except User.DoesNotExist:
            return Response(
                {"message": f"{kwargs['backjoon_id']} 유저를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            study = Study.objects.get(id=kwargs['study_id'])
        except Study.DoesNotExist:
            return wrong_study_response()

        try:
            join_request = Notification.objects.get(
                sender=joined_user,
                receiver=study.leader,
                study=study,
                notification_type='join'
            )
        except Notification.DoesNotExist:
            Response({"message": "해당 요청을 찾을 수 없습니다."})
        
        if join_request.is_read:
            return Response({"message": "이미 처리된 요청입니다."})
        join_request.is_read=True
        join_request.save()

        study.add_member(joined_user)
        Notification.create_notification(
            sender=request_user, 
            study=study, 
            notification_type="join_accepted", 
            receivers=joined_user
        )

        return Response({"message": "합류 수락 완료"})


class StudyJoinRejectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_user = request.user

        try:
            joined_user = User.objects.get(backjoon_id=kwargs['backjoon_id'])
        except User.DoesNotExist:
            return Response(
                {"message": f"{kwargs['backjoon_id']} 유저를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            study = Study.objects.get(id=kwargs['study_id'])
        except Study.DoesNotExist:
            return wrong_study_response()

        try:
            join_request = Notification.objects.get(
                sender=joined_user,
                receiver=study.leader,
                study=study,
                notification_type='join'
            )
        except Notification.DoesNotExist:
            Response({"message": "해당 요청을 찾을 수 없습니다."})

        if join_request.is_read:
            return Response({"message": "이미 처리된 요청입니다."})
        join_request.is_read=True
        join_request.save()

        Notification.create_notification(
            sender=request_user, 
            study=study, 
            notification_type="join_rejected", 
            receivers=joined_user
        )

        return Response({"message": "합류 거절 완료"})