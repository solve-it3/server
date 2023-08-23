from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from studies.serializers import StudyResponseSerializer
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
    is_member = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ['id', 'name', 'rank', 'grade', 'members', 'problem_count', 'mvp', 'is_leader', 'is_member', 'is_leader']

    def get_rank(self, obj):
        return obj.get_rank()

    def get_problem_count(self, obj):
        return obj.problem_count()

    def get_mvp(self, obj):
        return obj.get_mvp()

    def get_is_leader(self, obj):
        return obj.leader == self.context['request_user']

    def get_is_member(self, obj):
        return self.context['request_user'] in obj.members.all()


class NotificationSerializer(ModelSerializer):
    study = StudyResponseSerializer()
    class Meta:
        model = Notification
        fields = ['id', 'title', 'content', 'study', 'created_at', 'notification_type']
