from rest_framework import serializers
from .models import *
from users.models import *
# 스터디명 중복확인 serializer

class StudyNameDuplicatedSerializer(serializers.Serializer):
    is_unique = serializers.BooleanField()

# 스터디명, 깃헙, 팀원, 스터디 언어, 문제수, 요일, 팀장 저장 -> 생성

class CreateStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'
        exclude = ['grade', 'study_grade']
