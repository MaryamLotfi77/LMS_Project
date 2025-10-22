from django.contrib import admin
from .models import Enrollment, EnrollmentStatus
from courses.models import ClassSession

# ====================================================================

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ('user', 'status', 'final_score', 'enrolled_at')
    readonly_fields = ('enrolled_at',)
    can_delete = True


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'level',
        'instructor',
        'start_date',
        'capacity',
        'current_enrollment_count',
        'is_full',
    )
    list_filter = ('level__course', 'instructor', 'start_date')
    date_hierarchy = 'start_date'
    search_fields = ('level__title', 'instructor__first_name', 'instructor__last_name')
    ordering = ('-start_date',)
    inlines = [EnrollmentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('level__course', 'instructor')
        return qs

#--------------------------------------------

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
        list_display = (
            'user',
            'session_info',
            'status',
            'final_score',
            'enrolled_at',
        )
        list_filter = ('status', 'session__level__course', 'session__instructor')
        search_fields = ('user__username', 'user__first_name', 'session__level__title')
        readonly_fields = ('user', 'session', 'enrolled_at')
        actions = ['set_active', 'set_reserved', 'set_conditional_pass', 'set_failed']
        fieldsets = (
            (None, {
                'fields': ('user', 'session', 'enrolled_at')
            }),
            ('نمرات و وضعیت', {
                'fields': ('status', 'final_score'),
                'description': 'نمره نهایی را فقط برای وضعیت‌های "قبول مشروط" یا "ناموفق" ثبت کنید.'
            }),
        )

        def has_add_permission(self, request):
            return False

        def session_info(self, obj):
            # نمایش دوره و سطح کلاس
            return f'{obj.session.level.course.title} - {obj.session.level.title}'

        session_info.short_description = "کلاس"

        @admin.action(description='فعال کردن وضعیت ثبت‌نام‌های انتخاب شده')
        def set_active(self, request, queryset):
            queryset.update(status=EnrollmentStatus.ACTIVE)

        @admin.action(description='رزرو کردن وضعیت ثبت‌نام‌های انتخاب شده')
        def set_reserved(self, request, queryset):
            queryset.update(status=EnrollmentStatus.RESERVED)

        @admin.action(description='مشروط کردن وضعیت ثبت‌نام‌های انتخاب شده')
        def set_conditional_pass(self, request, queryset):
            queryset.update(status=EnrollmentStatus.CONDITIONAL_PASS)

        @admin.action(description='ناموفق کردن وضعیت ثبت‌نام‌های انتخاب شده')
        def set_failed(self, request, queryset):
            queryset.update(status=EnrollmentStatus.FAILED)
