from django.contrib import admin
from django.db.models import Count
from .models import Assessment, Question, Option, UserAssessment, UserAnswer


# -------------------------------------------------------------------

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1
    max_num = 10
    fields = ('is_correct', 'text')


# -------------------------------------------------------------------

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview', 'assessment', 'question_type', 'score_weight')
    list_filter = ('assessment', 'question_type')
    search_fields = ('text', 'assessment__title')
    inlines = [OptionInline]

    fieldsets = (
        ("اطلاعات اصلی سؤال", {
            'fields': ('assessment', 'text', 'question_type')
        }),
        ("نمره‌دهی و پاسخ صحیح", {
            'fields': ('score_weight', 'correct_answer_text'),
            'description': 'پاسخ صحیح متنی فقط برای سوالات متنی استفاده می‌شود. برای چندگزینه‌ای، گزینه‌ها را تنظیم کنید.'
        }),
    )

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'متن سؤال'


# -------------------------------------------------------------------

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    inlines = [OptionInline]

    fieldsets = (
        (None, {
            'fields': ('text', 'question_type', 'score_weight', 'correct_answer_text'),
        }),
    )


# -------------------------------------------------------------------

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'target_level',
        'question_count_display',
        'passing_score',
        'duration_minutes',
        'is_active',
        'created_at'
    )
    list_filter = ('is_active', 'target_level')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'target_level')
        }),
        ("تنظیمات آزمون", {
            'fields': ('passing_score', 'duration_minutes', 'is_active'),
            'classes': ('collapse',),
        })
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(question_count=Count('questions'))

    def question_count_display(self, obj):
        return obj.question_count

    question_count_display.short_description = 'تعداد سؤالات'
    question_count_display.admin_order_field = 'question_count'


# -------------------------------------------------------------------

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'user_text_answer', 'is_correct', 'score_earned')
    can_delete = False


@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'final_score', 'is_passed', 'start_time', 'end_time', 'time_taken_display')
    list_filter = ('assessment', 'is_passed')
    search_fields = ('user__username', 'assessment__title')
    readonly_fields = ('user', 'assessment', 'start_time', 'end_time', 'final_score', 'is_passed')
    inlines = [UserAnswerInline]
    raw_id_fields = ('user', 'assessment')

    def time_taken_display(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            minutes, seconds = divmod(duration.total_seconds(), 60)
            return f"{int(minutes)}m {int(seconds)}s"
        return "N/A"

    time_taken_display.short_description = 'زمان سپری شده'