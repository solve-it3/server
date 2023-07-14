from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
from django.conf import settings
import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
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
        print(response.content)
        response_json = response.json()
        access_token = response_json.get("access_token")

        headers = {
            "Authorization": f"Bearer {access_token}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # 정보 받기 요청
        kakao_profile = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers=headers
        )
        profile_json = kakao_profile.json()
        # if kakao_profile.status_code != 200:
        #     print(
        #         f"Error : {kakao_profile.status_code}, {kakao_profile.content}")

        kakao_id = profile_json['id']
        profile_image = profile_json['kakao_account']['profile']['thumbnail_image_url']

        user, created = User.objects.get_or_create(kakao_id=kakao_id)
        user.profile_image = profile_image
        user.save()

        return JsonResponse({'message': 'login success'})
