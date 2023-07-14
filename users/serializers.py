from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User


class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserUpdateSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ['id', 'kakao_id', 'backjoon_id', 'github_id', 'company']


class UserDetailSerializer(UserBaseSerializer):
    is_follow = serializers.BooleanField()
    followers = serializers.IntegerField()
    following = serializers.IntegerField()
    solved = serializers.CharField()
    # personal_ranking = serializers.IntegerField()
    # studies = StudyDetailSerializer()

    class Meta(UserBaseSerializer.Meta):
        fields = ['id', 'kakao_id', 'backjoon_id', 'github_id',
                  'company', 'is_follow', 'followers', 'following', 'solved']
