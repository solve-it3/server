from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from studies.models import Study
from .models import User, Notification


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
    rank = serializers.SerializerMethodField()
    problem_count = serializers.SerializerMethodField()
    mvp = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ['id', 'name', 'rank', 'grade', 'members', 'problem_count', 'mvp', ]

    def get_rank(self, obj):
        return obj.get_rank()

    def get_problem_count(self, obj):
        return obj.problem_count()

    def get_mvp(self, obj):
        return obj.get_mvp()


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


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title','content','created_at', 'notification_type']
