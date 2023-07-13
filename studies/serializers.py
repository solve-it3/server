from rest_framework import serializers
from .models import *



class WeekStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Week_study
        fields ='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields ='__all__'

class DayStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study, Week_study
        fields = '__all__'

class StudyNameDuplicatedSerializer(serializers.Serializer):
    is_unique = serializers.BooleanField()

