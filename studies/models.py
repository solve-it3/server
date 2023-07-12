from django.db import models

# from django.contrib.auth.models import User
class Study(models.Model):
    name = models.CharField(max_length=100, verbose_name="이름", null=False)
    github_repository = models.URLField(max_length=200, verbose_name="GitHub 저장소", null=True)
    # members = models.ManyToManyField(User, on_delete=models.SET_NULL, related_name='study_member', verbose_name="멤버")
    # leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='study_leader', verbose_name="리더")
    language = models.CharField(max_length=50, null=True, default=None)
    default_problem_number = models.IntegerField(max_length=50, null=True, default=None)
    start_date = models.DateField ( auto_now = False , auto_now_add = False)
    grade = (('D', '대류권'),('S', '성층권'),('J', '중간권'), ('Y', '열권'), ('O', '외기권')) 
    study_grade = models.CharField(max_length=2, choices=grade)
    is_open = models.BooleanField()

class Week_study(models.Model):
    study = models.ForeignKey("Study", verbose_name="해당스터디", null= False)
    index = models.IntegerField(null=False, default=None)
    problems = models.ManyToManyField("Problem", null=False, verbose_name="문제들")
    algorithms = models.CharField(null=False, verbose_name="알고리즘")

class Problem_week(models.Model):
    study = models.ForeignKey("Study", verbose_name="해당주차", null=False, through = "Week_study")
    study = models.ForeignKey("Week_study", verbose_name="해당주차", null=False)
    mon_commit = models.JSONField()
    tue_commit = models.JSONField()
    wed_commit = models.JSONField()
    thu_commit = models.JSONField()
    fri_commit = models.JSONField()
    mon_commit = models.JSONField()
    sun_commit = models.JSONField()

class Notification(models.Model):
    # user = models.ForeignKey(User, null=False)
    study = models.ForeignKey("Study", null=False)
    title = models.TextField()
    content = models.TextField()
    is_read = models.BooleanField
