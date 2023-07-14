import requests

from django.conf import settings
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import UserUpdateSerializer
from .models import User


BASE_URL = settings.BASE_URL
KAKAO_REST_API_KEY = settings.KAKAO_REST_API_KEY


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
            "redirect_uri": f"{BASE_URL}/api/user/kakao/callback",
            "code": request.data.get('code'),
        }

        # 토큰 받기 요청
        response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            headers=headers,
            data=data
        )

        response_json = response.json()
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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
