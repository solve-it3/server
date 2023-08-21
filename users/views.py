import requests

from django.conf import settings
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from studies.models import Study, Week, Problem, ProblemStatus
from .serializers import UserUpdateSerializer, NotificationSerializer, StudySerializer
from .models import User, UserProblemSolved, Notification


BASE_URL = settings.BASE_URL
KAKAO_REST_API_KEY = settings.KAKAO_REST_API_KEY
REDIRECT_URI = settings.KAKAO_REDIRECT_URI

# 인가코드 받는 부분, 프론트에서 개발 시 삭제
def kakao_login(request):
    redirect_uri = f"{BASE_URL}/api/user/kakao/callback"
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_REST_API_KEY}&redirect_uri={redirect_uri}&response_type=code")


class KakaoSignUpView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": request.data.get('code'),
        }

        # 토큰 받기 요청
        response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            headers=headers,
            data=data
        )

        response_json = response.json()
        if response.status_code != 200:
            return Response(response_json, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = response_json.get("access_token")

        headers = {
            "Authorization": f"Bearer {access_token}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # 카카오 프로필 정보 요청
        kakao_profile = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers=headers
        )

        profile_json = kakao_profile.json()
        if kakao_profile.status_code != 200:
            return Response(profile_json, status=status.HTTP_400_BAD_REQUEST)
        
        kakao_id = profile_json['id']
        profile_image = profile_json['kakao_account']['profile']['thumbnail_image_url']

        # 유저 정보 저장
        user, created = User.objects.get_or_create(kakao_id=kakao_id)
        user.profile_image = profile_image
        user.save()

        # 유저의 스터디 하나 반환
        study = Study.objects.filter(members=user).first()
        if study:
            user_study = study.id
        else:
            user_study = None

        # JWT 발급
        token = TokenObtainPairSerializer.get_token(user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        return Response({
            "created": created,
            "study": user_study,
            "access": access_token,
            "refresh": refresh_token
        })


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated, ]

    def patch(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # UserProblemSolved 모델 생성
            ups, created = UserProblemSolved.objects.get_or_create(user=request.user)
            if created:
                ups.initialize()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {}
        try:
            user = User.objects.get(backjoon_id=kwargs['backjoon_id'])
        except User.DoesNotExist:
            return Response(
                {"message": f"유저 {kwargs['backjoon_id']}를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        request_user = request.user

        study = Study.objects.filter(members=user)
        serializer = StudySerializer(study, many=True, context={'request_user': request_user})
        return Response(serializer.data)


class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(backjoon_id=kwargs['backjoon_id'])
        except User.DoesNotExist:
            return Response(
                {"message": f"유저 {kwargs['backjoon_id']}를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        request_user = request.user
        if request_user != user:
            return Response(
                {"message": "본인의 알림만 볼 수 있습니다."}, 
                status=status.HTTP_204_NO_CONTENT
            )
        
        queryset = Notification.objects.filter(receiver=request_user).order_by('-created_at')
        # TODO 갯수로 자르되 합류 요청은 뜨게 하기
        serializer = NotificationSerializer(queryset, many=True)
        
        return Response(serializer.data)


class FollowView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = kwargs["backjoon_id"]

        if request.user.is_following(user):
            request.user.unfollow(user)
            return Response({"message": "Unfollow Success!"}, status=status.HTTP_200_OK)
        else:
            request.user.follow(user)
            return Response({"message": "Follow Success!"}, status=status.HTTP_201_CREATED)


class ProblemSolvedUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwagrs):
        for user in User.objects.all():
            user.solved_problems.update()

