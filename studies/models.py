from django.db import models
from django.conf import settings


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
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    algorithms = models.CharField(
        max_length=50, null=False, verbose_name="알고리즘")
    

    def __str__(self):
        return f"Week of {self.start_date} - {self.end_date} for {self.study}"
    
    def problem_count(self):
        return ProblemStatus.objects.filter(problem__week=self, is_solved=True).count()


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
        return self.name


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
        return f"{self.user} status for {self.problem}"
