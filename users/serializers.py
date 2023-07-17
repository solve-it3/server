from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from studies.models import Study
from .models import User


class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserUpdateSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ['id', 'kakao_id', 'backjoon_id', 'github_id', 'company']


class MemberSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ['kakao_id', 'backjoon_id', 'profile_image']


class StudySerializer(ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)

    class Meta:
        model = Study
        exclude = ['id', 'github_repository', 'language',
                   'problems_in_week', 'start_day', 'created_at', 'leader']


class UserDetailSerializer(UserBaseSerializer):
    is_follow = serializers.BooleanField()
    followers = serializers.IntegerField()
    following = serializers.IntegerField()
    solved = serializers.CharField()
    # personal_ranking = serializers.IntegerField()
    studies = StudySerializer(many=True, read_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = ['id', 'kakao_id', 'backjoon_id', 'github_id', 'company',
                  'is_follow', 'followers', 'following', 'solved', 'studies']
