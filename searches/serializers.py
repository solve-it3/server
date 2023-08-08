from rest_framework.serializers import ModelSerializer

from users.models import User
from studies.models import Study


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['backjoon_id', 'profile_image', 'github_id', 'company']


class StudySerializer(ModelSerializer):
    members = UserSerializer(many=True)
    class Meta:
        model = Study
        fields = ['name', 'members', 'language']