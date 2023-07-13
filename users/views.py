from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
from django.conf import settings
import requests
from django.http import JsonResponse

BASE_URL = settings.BASE_URL
KAKAO_REST_API_KEY = settings.KAKAO_REST_API_KEY


# 인가코드 받는 부분, 프론트에서 개발 시 삭제
def kakao_login(request):
    redirect_uri = f"{BASE_URL}/user/kakao/callback"
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_REST_API_KEY}&redirect_uri={redirect_uri}&response_type=code")


def kakao_callback(request):
    User = get_user_model()
    code = request.GET.get("code")
    redirect_uri = f"{BASE_URL}/user/kakao/callback"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    # 토큰을 얻기 위해 카카오에 POST 요청
    response = requests.post(
        "https://kauth.kakao.com/oauth/token", headers=headers, data=data)
    response_json = response.json()
    access_token = response_json.get("access_token")

    # 토큰을 이용해 사용자 정보를 얻습니다.
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers=headers)
    response_json = response.json()
    kakao_id = response_json.get("id")
    profile_image = response_json.get("properties").get("thumbnail_image")
    print(f"kakao_id={kakao_id}\nprofile_image={profile_image}")

    try:
        user = User.objects.get(kakao_id=kakao_id)
    except User.DoesNotExist:
        user = User.objects.create_user(kakao_id=kakao_id)

    login(request, user)

    return JsonResponse({'message': 'Logged in successfully'})
