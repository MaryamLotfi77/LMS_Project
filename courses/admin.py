from django.contrib import admin
from django import forms
from .models import Level
from mptt.admin import MPTTModelAdmin
from .models import (
    Category,
    Course,
    Level,
    ClassSession,
    Enrollment,
    EnrollmentStatus,
)


# ====================================================================

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    mptt_level_indent = 20

# ====================================================================

class LevelInline(admin.StackedInline):
    model = Level
    extra = 1
    fields = ('level_number', 'title', 'prereq_level')
    ordering = ('level_number',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level_count')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    inlines = [LevelInline]

    def level_count(self, obj):
        return obj.levels.count()

    level_count.short_description = "تعداد سطوح"


# ====================================================================

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'level_number', 'prereq_level')
    list_filter = ('course',)
    search_fields = ('title',)
    readonly_fields = ('next_level',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "prereq_level":
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



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



# ====================================================================

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