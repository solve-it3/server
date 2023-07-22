from rest_framework import serializers
from .models import *
from users.models import *
from rest_framework import request
# 스터디명 중복확인 serializer


class StudyNameDuplicatedSerializer(serializers.Serializer):
    is_unique = serializers.BooleanField()


class CreateStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields ='__all__'
        exclude =['grade', 'study_grade']

class StudyBaseSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many = True,
        queryset=User.objects.all(),
        slug_field='backjoon_id'
    )
    leader = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='backjoon_id'
    )
    class Meta:
        model = Study
        fields = '__all__'

# user_id, 유저 스터디 목록, 현재 스터디의 주차, 스터디 이름, 스터디 등급, 진척도, MVP, request user가 푼 문제수, 스터디 잔디
# 스터디 이름, 리더, members, grade, 깃헙, 언어, 문제풀 수, 시작날짜, 만들어 진거, 오픈할지 존재

# id에 대한 모든 스터디 목록이 필요 user_study로 만들기
# 현재 스터디의 주차 -> Week에서 week number를 가져온다. week number는 start_date
# 진척도 
# mvp -> user
# 지금까지 푼 문제수 -> user의 지금까지 푼 문제수
class UserStudyHomepageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields ='__all__'



class MVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatus
        fields ='__all__'



class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatus
        fields ='__all__'

class UserTotalProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatus
        fields ='__all__'

class DateRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields ='__all__'

class JandiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields ='__all__'

class StudyChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'

