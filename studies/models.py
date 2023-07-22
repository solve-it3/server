from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Study(models.Model):
    name = models.CharField(max_length=255, unique=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_studies', null=True)
    members = models.ManyToManyField(User, related_name='joined_studies')
    grade = models.CharField(max_length=255, null=True, blank=True)
    github_repository = models.URLField(null=True, blank=True)
    language = models.CharField(max_length=50, null=True, default=None)
    problems_in_week = models.IntegerField(null=True, default=None)
    start_day = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Week(models.Model):
    study = models.ForeignKey(
        Study, on_delete=models.CASCADE, related_name='weeks')
    # study에 해당하는 week_number -> 몇주차 인지
    week_number = models.IntegerField(null=True, blank=True)
    # 그 스터디를 시작한 날짜
    start_date = models.DateField(null=True, blank=True)
    # 스터디가 그 주차에 끝나는 날짜
    end_date = models.DateField(null=True, blank=True)
    # 어떤 알고리즘으로 할것인지
    algorithms = models.CharField(
        max_length=50, null=False, verbose_name="알고리즘")

    def __str__(self):
        return f"Week of {self.start_date} - {self.end_date} for {self.study}"


class Problem(models.Model):
    week = models.ForeignKey(
        Week, on_delete=models.CASCADE, related_name='problems')
    #문제의 이름
    name = models.CharField(max_length=255)
    #문제 번호
    number = models.IntegerField(null=True, blank=True)
    #문제 url
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProblemStatus(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='statuses')
    # 문제가 풀렸는지
    is_solved = models.BooleanField(default=False)
    # commit 주소
    commit_url = models.URLField(blank=True, null=True)
    # 언제 풀었는지
    solved_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} status for {self.problem}"
