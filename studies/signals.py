# signals.py
import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Study, Week


days = ["월", "화", "수", "목", "금", "토", "일"]


@receiver(post_save, sender=Study)
def create_first_week(sender, instance=None, created=False, **kwagrs):
    if created:
        start_date = datetime.date.today()
        target_day = days.index(instance.start_day)
        current_day = start_date.weekday()

        days_until_target = (target_day - current_day + 7) % 7
        next_target_date = start_date + \
            datetime.timedelta(days=days_until_target)

        end_date = next_target_date - datetime.timedelta(days=1)

        if (end_date - start_date).days < 6:
            end_date += datetime.timedelta(days=7)

        Week.objects.create(
            study=instance,
            week_number=1,
            start_date=start_date,
            end_date=end_date,
        )
