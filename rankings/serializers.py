from rest_framework.serializers import ModelSerializer
from studies.models import Study, Week
from rest_framework import serializers
from users.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_image", "backjoon_id",]


class StudyRankingSerializer(ModelSerializer):
    problem_count = serializers.SerializerMethodField()
    leader = UserSerializer()
    # mvp = serializers.CharField()
    class Meta:
        model = Study
        fields = ["name", "grade", "leader",
                   #"mvp", "rank", 
                   "problem_count",
                     ]
    def get_problem_count(self, obj):
        week = obj.current_week - 1
        return Week.objects.get(study = obj, week_number = week).problem_count()
    
class RankingSerializer(serializers.Serializer):
    study_ranking = serializers.ListField()
    # personal_ranking = serializers.SerializerMethodField()
