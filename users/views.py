import requests

from django.conf import settings
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from studies.models import Study, Week, Problem, ProblemStatus
from .serializers import UserUpdateSerializer, UserDetailSerializer
from .models import User, UserProblemSolved


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

        # JWT 발급
        token = TokenObtainPairSerializer.get_token(user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        return Response({
            "created": created,
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


class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(backjoon_id=kwargs['backjoon_id'])

        # solved.ac api 통해 가져오고 없으면 "?" 반환
        try:
            response = requests.get(
                f"https://solved.ac/api/v3/user/show?handle={user.backjoon_id}")
            response.raise_for_status()
            data = response.json()
            solved = data.get('solvedCount', '?')
        except Exception:
            solved = '?'

        instance = dict()
        instance['id'] = user.id
        instance['kakao_id'] = user.kakao_id
        instance['backjoon_id'] = user.backjoon_id
        instance['github_id'] = user.github_id
        instance['company'] = user.company
        instance['followers'] = user.followers.count()
        instance['following'] = user.following.count()
        instance['solved'] = solved
        instance['is_follow'] = request.user.is_following(
            kwargs['backjoon_id'])
        instance['studies'] = user.get_studies()

        serializer = self.get_serializer(instance)
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

