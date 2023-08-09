import requests

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from studies.models import Study
from .serializers import UserSerializer


class ProblemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        problem_num = kwargs['problem_number']
        try:
            study = Study.objects.get(name=kwargs['study_name'])
        except Study.DoesNotExist:
            Response({"message": "그런 스터디 이름은 없읍니다..."}, status=status.HTTP_404_NOT_FOUND)

        url = f"https://solved.ac/api/v3/problem/show?problemId={problem_num}"
        response = requests.get(url)
        
        if response.status_code != 200 :
            return Response({"message": "없는 문제 번호입니다..."}, status=status.HTTP_404_NOT_FOUND)
        else :
            response_json = response.json()

        solved_member = [member for member in study.members.all() 
                         if str(problem_num) in member.solved_problems.problem.keys()]

        data = {
            "number": problem_num,
            "name": response_json.get("titleKo"),
            "algorithms": response_json["tags"][0]["displayNames"][0]["name"],
            "solved_members": UserSerializer(solved_member, many=True).data
        }
        
        return Response(data)