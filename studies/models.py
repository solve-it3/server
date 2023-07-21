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

    def __str__(self):
        return self.name


class Week(models.Model):
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='weeks'
    )
    week_number = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    algorithms = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="알고리즘"
    )

    def __str__(self):
        return f"[{self.week_number}주차] {self.study}"


class Problem(models.Model):
    week = models.ForeignKey(
        Week,
        on_delete=models.CASCADE,
        related_name='problems'
    )
    name = models.CharField(max_length=255)
    number = models.IntegerField(null=True, blank=True)
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
    commit_url = models.URLField(blank=True, null=True)
    solved_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}가 {self.problem}번을 풀었습니다."
