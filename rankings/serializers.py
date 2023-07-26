from rest_framework.serializers import ModelSerializer
from studies.models import Study, Week
from rest_framework import serializers
from users.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_image", "backjoon_id", ]


class StudySerializer(ModelSerializer):
    rank = serializers.SerializerMethodField()
    members = UserSerializer(many=True)
    mvp = serializers.SerializerMethodField()
    problem_count = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ['rank', 'name',  'grade', 'mvp',
                  'problem_count', 'members', 'is_open']

    def get_rank(self, obj):
        return obj.get_rank()

    def get_problem_count(self, obj):
        # week = obj.current_week - 1
        # return Week.objects.get(study = obj, week_number = week).problem_count()
        return Study.objects.get(name=obj).problem_count()

    def get_mvp(self, obj):
        week = obj.current_week
        return Week.objects.get(study=obj, week_number=week).mvp().backjoon_id


class StudyRankingSerializer(ModelSerializer):
    rank = serializers.SerializerMethodField()
    problem_count = serializers.SerializerMethodField()
    leader = UserSerializer()
    mvp = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ["rank", "name", "grade", "leader", "mvp", "problem_count"]

    def get_rank(self, obj):
        return obj.get_rank()

    def get_problem_count(self, obj):
        # week = obj.current_week - 1
        # return Week.objects.get(study = obj, week_number = week).problem_count()
        return Study.objects.get(name=obj).problem_count()

    def get_mvp(self, obj):
        week = obj.current_week
        return Week.objects.get(study=obj, week_number=week).mvp().backjoon_id


class RankingSerializer(serializers.Serializer):
    my_study = StudySerializer()
    study_ranking = serializers.ListField()
    # personal_ranking = serializers.SerializerMethodField()


# SerializerMethodField를 통해 임의의 필드를 사용할 수 있음
# SerializerMethodField를 선언하면 해당 필드 조회할 때, 실행할 함수를 생성해야 함
# -> def get_<필드명> 형태로 함수 생성
# -> 데이터 조회될 때, 이 함수가 실행됨
# def get_problem_count(self, obj)
# -> 여기서, obj 즉 object는 serializer에 인자로 들어간 instance를 뜻함
# 즉, 이 예시에서는 obj에 Study 객체(instance)가 들어가는 것
