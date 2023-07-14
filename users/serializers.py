from rest_framework.serializers import ModelSerializer
from .models import User


class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserUpdateSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ['id', 'kakao_id', 'backjoon_id', 'github_id', 'company']
