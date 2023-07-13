from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.response import Response


# Create your views here.

class StudyNameDuplicatedView(generics.RetrieveAPIView):
    queryset = Study.objects.all()
    serializer_class = StudyNameDuplicatedSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = {}
        try:
            Study.objects.get(name=request.data.get('name'))
            instance['is_unique'] = False

        except Study.DoesNotExist:
            instance['is_unique'] = True

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
