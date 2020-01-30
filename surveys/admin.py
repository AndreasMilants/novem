from django.contrib import admin
from .models import Question, Survey, Answer, ImportantLevelAnswer, SurveyInstance
from .forms import CreateSurveyForm, SurveyInstanceFormAdmin


class QuestionInline(admin.TabularInline):
    model = Question


class CreateSurveyAdmin(admin.ModelAdmin):
    form = CreateSurveyForm
    inlines = [QuestionInline, ]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class ImportantLevelAnswerInline(admin.TabularInline):
    model = ImportantLevelAnswer
    max_num = 3


class SurveyInstanceAdmin(admin.ModelAdmin):
    form = SurveyInstanceFormAdmin
    inlines = [AnswerInline, ImportantLevelAnswerInline, ]


admin.site.register(Survey, CreateSurveyAdmin)
# admin.site.register(SurveyInstance, SurveyInstanceAdmin) I don't think staff should see this
