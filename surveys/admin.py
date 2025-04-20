from django.contrib import admin
from .models import Survey, Question, Choice, Response, Answer, SelectedChoice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class SelectedChoiceInline(admin.TabularInline):
    model = SelectedChoice
    extra = 0
    readonly_fields = ('choice',)
    can_delete = False

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'text_answer', 'date_answer')
    can_delete = False
    inlines = [SelectedChoiceInline]

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'updated_at', 'created_by')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]
    readonly_fields = ('access_code',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'required', 'order')
    list_filter = ('survey', 'question_type', 'required')
    search_fields = ('text', 'survey__title')
    inlines = [ChoiceInline]

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'respondent_id', 'submitted_at')
    list_filter = ('survey', 'submitted_at')
    inlines = [AnswerInline]
    readonly_fields = ('survey', 'respondent_id', 'submitted_at')

# These are simpler models, so we use the default admin
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(SelectedChoice)
