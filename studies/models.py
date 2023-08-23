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

    @property
    def grade(self):
        total_solved_problem = self.total_solved_problem()
        if 0 <= total_solved_problem < 20:
            return "✈️ 성층권"
        elif 20 <= total_solved_problem < 40:
            return "🛰️ 카르만선"
        elif 40 <= total_solved_problem < 60:
            return "🌖 지구-달"
        elif 60 <= total_solved_problem < 80:
            return "🎆 랑그라주점"
        elif 80 <= total_solved_problem < 100:
            return "🌫️ 오르트구름"
        else:
            return "🚀 성간우주"

    def total_solved_problem(self):
        return ProblemStatus.objects.filter(user__in=self.members.all(), is_solved=True).count()

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
        scores = []
        for study in studies:
            scores.append((study.name, study.problem_count()))

        # 문제 수로 정렬
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # 등수 부여 (동점자 고려)
        rank = 1
        last_score = -1
        ranks = {}
        for name, score in sorted_scores:
            if score != last_score:  # 이전 점수와 다르면 등수 증가
                rank += len([x for x, y in ranks.items() if y == last_score])  # 이전 점수와 동일한 사람 수만큼 등수 증가
                last_score = score
            ranks[name] = rank

        return ranks.get(self.name, 0)

    def get_mvp(self):
        today = datetime.date.today()
        target_date = today - datetime.timedelta(7)

        members = self.members.all()
        mvp = None
        max_problem_count = 0

        for member in members:
            problem_count = ProblemStatus.objects.filter(
                user=member, is_solved=True
            ).filter(
                solved_at__gte=target_date, solved_at__lte=today
            ).count()

            if problem_count > max_problem_count:
                max_problem_count = problem_count
                mvp = member
        
        if mvp:
            return mvp.backjoon_id
        return mvp
        

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