from rest_framework import serializers
from .models import *
from users.models import *
from rest_framework import request
# 스터디명 중복확인 serializer


class StudyNameDuplicatedSerializer(serializers.Serializer):
    is_unique = serializers.BooleanField()


class StudyBaseSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
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
        fields = '__all__'


class MVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatus
        fields = '__all__'


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatus
        fields = '__all__'


class UserTotalProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatus
        fields = '__all__'


class DateRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'


class JandiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'


class StudyChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'

class ProblemSolverSerializer(serializers.ModelSerializer):
    commit_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["backjoon_id", "profile_image", "commit_url"]
    # obj는 User이다 model이 User이므로
    # 역참조를 쓰기위해 related_name을 사용
    def get_commit_url(self, obj ):
        # problem의 number가 problem_number와 같은 obj의 status들을 가져오는 것
        problem_number = self.context.get("problem_number")
        try:
            commit = obj.statuses.get(problem__number = problem_number)
        except Exception:
            return None
        return commit.commit_url
    

class ProblemBaseSerializer(serializers.ModelSerializer):
    # 함수써서 Get 해서 가져오는 것
    is_solved = serializers.SerializerMethodField()
    solvers = serializers.SerializerMethodField()
    commit_url = serializers.SerializerMethodField()
    class Meta:
        model = Problem
        fields = ["number", "name", "url", "algorithms", "solvers", "is_solved", "commit_url"]
    # obj가 problem이니깐
    # self는 serializer
    def get_solvers(self, obj):
        members = obj.week.study.members.all()
        solvers = list()
        for member in list(members):
            try:
                member.statuses.get(problem=obj, is_solved=True)
                solvers.append(member)
            except Exception:
                pass
        return ProblemSolverSerializer(solvers,many=True,context={'problem_number':obj.number}).data
    
    def get_is_solved(self, obj):
        request_user = self.context["request_user"]
        try :
            request_user.statuses.get(problem=obj)
            return True
        except Exception :
            return False
        
    def get_commit_url(self, obj):
        request_user = self.context["request_user"]
        try :
            status = request_user.statuses.get(problem=obj)
            return status.commit_url
        except Exception :
            return None
    

# 스터디이름
# 몇주차?
# 날짜
# 알고리즘
# 문제 -> 번호, 이름
# 푼사람, 풀었는지 여부
#
class WeekBaseSerializer(serializers.ModelSerializer):
    # foreign_key를 이름으로 볼 수 있다.
    study = serializers.SlugRelatedField(
        queryset=Study.objects.all(),
        slug_field='name'
    )
    # nested_serializer
    class Meta:
        model = Week
        fields = ["id", "study", "week_number", "start_date", "end_date", "algorithms", "problems" ]

    def to_representation(self, instance):
        # ProblemBaseSerializer 호출 시 context에 request_user 전달
        representation = super().to_representation(instance)
        representation['problems'] = ProblemBaseSerializer(instance.problems.all(), many=True, context=self.context).data
        return representation