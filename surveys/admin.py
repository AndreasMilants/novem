from django.contrib import admin
from .models import Question, Survey, Answer
from .forms import CreateSurveyForm


class QuestionInline(admin.TabularInline):
    model = Question


class CreateSurveyAdmin(admin.ModelAdmin):
    form = CreateSurveyForm
    inlines = [QuestionInline, ]


admin.site.register(Survey, CreateSurveyAdmin)
admin.site.register(Answer)
