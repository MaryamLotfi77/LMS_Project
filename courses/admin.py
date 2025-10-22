from django.contrib import admin
from django import forms
from .models import Level
from mptt.admin import MPTTModelAdmin
from .models import (
    Category,
    Course,
    Level,
    ClassSession
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





