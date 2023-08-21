import datetime
import requests
from requests.exceptions import RequestException, JSONDecodeError

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from studies.models import Study, ProblemStatus



class UserManager(BaseUserManager):
    def create_user(self, kakao_id, password=None, backjoon_id=None, github_id=None, **extra_fields):
        if not kakao_id:
            raise ValueError('The given kakao_id must be set')

        user = self.model(
            kakao_id=kakao_id,
            backjoon_id=backjoon_id,
            github_id=github_id,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, kakao_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(kakao_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    kakao_id = models.CharField(max_length=255, unique=True)
    backjoon_id = models.CharField(max_length=255, null=True, blank=True)
    github_id = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default="")
    company = models.CharField(max_length=255, blank=True, null=True)
    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers')
    is_open = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'kakao_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.kakao_id

    def follow(self, backjoon_id):
        user = User.objects.get(backjoon_id=backjoon_id)
        self.following.add(user)

    def unfollow(self, backjoon_id):
        user = User.objects.get(backjoon_id=backjoon_id)
        self.following.remove(user)

    def is_following(self, backjoon_id):
        return self.following.filter(backjoon_id=backjoon_id).exists()

    def is_followed_by(self, backjoon_id):
        return self.followers.filter(backjoon_id=backjoon_id).exists()

    def get_studies(self):
        return list(self.joined_studies.all())
    
    def problem_count(self):
        today = datetime.date.today()
        target_date = today - datetime.timedelta(7)

        count = ProblemStatus.objects.filter(user=self, is_solved=True).filter(
            solved_at__gte=target_date).filter(solved_at__lte=today).count()

        return count
    
    def get_rank(self):
        users = User.objects.filter(is_staff=False)
        rank = dict()
        for user in users:
            rank[f"{user.backjoon_id}"] = user.problem_count()
        rank = dict(sorted(rank.items(), key=lambda x: x[1], reverse=True))
        return list(rank).index(self.backjoon_id) + 1


class Notification(models.Model):
    receiver = models.ManyToManyField(
        User,
        related_name='received_notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.CharField(max_length=100, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.study}] {self.title}"

    @classmethod
    def create_notification(cls, sender, study, notification_type, **kwargs):
        if notification_type == 'solved':
            receivers = study.members.all()
            title = "풀이 완료"
            content = f"{sender}님이 문제를 풀었습니다!"
        elif notification_type == 'join':
            receivers = [study.leader]
            title = "합류 요청"
            content = f"{sender}님의 합류 요청이 있습니다!"
        elif notification_type == 'join_accepted':
            receivers = [kwargs['receivers']]
            title = "합류 요청 수락"
            content = f"{study.name}에 합류하셨습니다."
        elif notification_type == 'join_rejected':
            receivers = [kwargs['receivers']]
            title = "합류 요청 거절"
            content = f"{study.name} 합류 요청이 거절당했습니다."
        else:
            raise TypeError("올바른 notification_type 입력해주세요")

        notification = cls(sender=sender, study=study, title=title, content=content)
        notification.save()
        notification.receiver.set(receivers)  # Use the set() method to update the receivers
        return notification



class UserProblemSolved(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='solved_problems'
    )
    problem = models.JSONField(null=True)

    def __str__(self):
        return f"{self.user.backjoon_id}가 푼 문제 목록"
    
    def initialize(self):
        try:
            response = requests.get(f'https://solved.ac/api/v3/user/show?handle={self.user.backjoon_id}')
            response.raise_for_status()
            solvedCount = response.json().get("solvedCount", 1)
        except (RequestException, JSONDecodeError):
            solvedCount = 1

        problem_dict = dict()
        for i in range(1, solvedCount//50 + 2):
            problem_items = requests.get(
                f'https://solved.ac/api/v3/search/problem?query=@{self.user.backjoon_id}&page={i}').json().get('items')

            for item in problem_items:
                problem_dict[item['problemId']] = None
        
        self.problem = problem_dict
        self.save()

        return self.problem
    
    def update(self):
        try:
            response = requests.get(f'https://solved.ac/api/v3/user/show?handle={self.user.backjoon_id}')
            response.raise_for_status()
            solvedCount = response.json().get("solvedCount", 1)
        except (RequestException, JSONDecodeError):
            solvedCount = 1

        problem_list = []
        for i in range(1, solvedCount//50 + 2):
            problem_items = requests.get(
                f'https://solved.ac/api/v3/search/problem?query=@{self.user.backjoon_id}&page={i}').json().get('items')

            for item in problem_items:
                problem_list.append(item['problemId'])

        for problem in problem_list:
            if problem not in self.problem.keys():
                self.problem[problem] = str(datetime.date.today())

        return self.problem

    def update_all(self):
        try:
            for user in User.objects.all():
                if UserProblemSolved.objects.filter(user=user).exists():
                    user.solved_problems.update()
        except Exception as e:
            raise Exception(e)
