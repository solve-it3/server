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
    current_week = models.IntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    current_week = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        return self.name


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
    
    def problem_count(self):
        return ProblemStatus.objects.filter(problem__week=self, is_solved=True).count()
    
    def mvp(self):
        member_list = self.study.members.all()
        member_problem = {} # 딕셔너리 형태
        for member in member_list:
            member_problem[member] = ProblemStatus.objects.filter(user = member, is_solved=True).count()
        result = max(member_problem, key=member_problem.get)
        return result


class Problem(models.Model):
    week = models.ForeignKey(
        Week,
        on_delete=models.CASCADE,
        related_name='problems'
    )
    name = models.CharField(max_length=255)
    #문제 번호
    number = models.IntegerField(null=True, blank=True)
    #문제 url
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return str(self.number)


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
    # commit 주소
    commit_url = models.URLField(blank=True, null=True)
    # 언제 풀었는지
    solved_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}가 {self.problem}번을 풀었습니다."
