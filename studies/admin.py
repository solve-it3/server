from django.contrib import admin
from .models import Study, Week, Problem, ProblemStatus

admin.site.register(Study)
admin.site.register(Week)
admin.site.register(Problem)
admin.site.register(ProblemStatus)

