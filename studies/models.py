import datetime

from django.conf import settings
from django.db import models


class Study(models.Model):
    name = models.CharField(max_length=255, unique=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='led_studies',
        null=True
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_studies'
    )
    grade = models.CharField(max_length=255, null=True, blank=True)
    github_repository = models.URLField(null=True, blank=True)
    language = models.CharField(max_length=50, null=True, default=None)
    problems_in_week = models.IntegerField(null=True, default=None)
    start_day = models.CharField(max_length=10, null=True, blank=True)
    current_week = models.IntegerField(null=True, blank=True, default=1)
    created_at = models.DateField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def problem_count(self):
        today = datetime.date.today()
        target_date = today - datetime.timedelta(7)

        members = self.members.all()

        count = 0
        for member in members:
            count += ProblemStatus.objects.filter(user=member, is_solved=True).filter(
                solved_at__gte=target_date).filter(solved_at__lte=today).count()

        return count

    def get_rank(self):
        studies = Study.objects.all()
        rank = dict()
        for study in studies:
            rank[f"{study.name}"] = study.problem_count()
        sorted(rank.items(), key=lambda x: x[1], reverse=True)

        return list(rank).index(self.name) + 1
    
    def add_member(self, user):
        if user not in self.members.all():
            self.members.add(user)


class Week(models.Model):
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='weeks'
    )
    week_number = models.IntegerField(null=True, blank=True)
    # 그 스터디를 시작한 날짜
    start_date = models.DateField(null=True, blank=True)
    # 스터디가 그 주차에 끝나는 날짜
    end_date = models.DateField(null=True, blank=True)
    # 어떤 알고리즘으로 할것인지
    algorithms = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="알고리즘"
    )

    def __str__(self):
        return f"[{self.week_number}주차] {self.study}"

    def mvp(self):
        member_list = self.study.members.all()
        member_problem = {}  # 딕셔너리 형태
        for member in member_list:
            member_problem[member] = ProblemStatus.objects.filter(
                user=member, is_solved=True).count()
        result = max(member_problem, key=member_problem.get)
        return result


class Problem(models.Model):
    week = models.ForeignKey(
        Week,
        on_delete=models.CASCADE,
        related_name='problems'
    )
    name = models.CharField(max_length=255) # 문제 이름
    number = models.IntegerField(null=True, blank=True) # 문제 번호
    url = models.URLField(null=True, blank=True) # 문제 url
    algorithms = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.number)

    def get_solvers(self):
        members=self.week.study.members.all()
        statuses = self.statuses.filter(user__in=members, is_solved=True)
        return [status.user for status in statuses]


class ProblemStatus(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='statuses'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='statuses'
    )
    is_solved = models.BooleanField(default=False)
    commit_url = models.URLField(blank=True, null=True) # commit 주소
    solved_at = models.DateField(null=True) # 언제 풀었는지


    def __str__(self):
        if self.is_solved:
            return f"{self.user}가 {self.problem}번을 풀었습니다."
        else:
            return f"{self.user}가 {self.problem}번을 안 풀었습니다."