import datetime
from django.shortcuts import render

from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *


# Create your views here.

class StudyNameDuplicatedView(generics.RetrieveAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyNameDuplicatedSerializer
    # 보는 것만 해야하니까 RetrieveAPIView만 만들어준다
    # retrieve를 오버라이딩해준다

    def retrieve(self, request, *args, **kwargs):
        # instance는 딕셔너리 json파일 형태로 하고
        instance = {}
        try:
            # Study의 객체들에서 name이 data.get한것의 name을 가져온다
            # 이 객체가 실패하면 False, 유일하면 True를 가져온다
            Study.objects.get(name=request.data.get('name'))
            instance['is_unique'] = False

        except Study.DoesNotExist:
            instance['is_unique'] = True

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreateStudyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Study.objects.all()
    serializer_class = CreateStudySerializer


class WeekRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Week.objects.all()
    serializer_class = WeekBaseSerializer
    permission_classes = [AllowAny, ]

    def retrieve(self, request, *args, **kwargs):
        week_num = kwargs['week_num']
        study_name = kwargs['study_name']

        try:
            study = Study.objects.get(name=study_name)
        except Study.DoesNotExist:
            return Response({'error': '그런 이름을 가진 스터디는 없소!'}, status=404)

        week, created = Week.objects.get_or_create(
            study=study,
            week_number=week_num
        )

        if created:
            last_week = Week.objects.get(study=study, week_number=week_num-1)
            week.start_date = last_week.end_date + datetime.timedelta(1)
            week.end_date = last_week.end_date + datetime.timedelta(7)
            week.save()

        serializer = self.get_serializer(week)
        return Response(serializer.data)
