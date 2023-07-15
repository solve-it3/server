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
    default_problem_number = models.IntegerField(null=True, default=None)
    start_date = models.DateField ( auto_now = False , auto_now_add = False)
    is_open = models.BooleanField()
    

    def __str__(self):
        return self.name


class Week(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='weeks')
    start_date = models.DateField()
    end_date = models.DateField()
    algorithms = models.CharField(max_length=50, null=False, verbose_name="알고리즘")


    def __str__(self):
        return f"Week of {self.start_date} - {self.end_date} for {self.study}"


class Problem(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='problems')
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    url = models.URLField()
    def __str__(self):
        return self.name


class ProblemStatus(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statuses')
    is_solved = models.BooleanField(default=False)
    commit_url = models.URLField(blank=True, null=True)
    solved_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.user} status for {self.problem}"

