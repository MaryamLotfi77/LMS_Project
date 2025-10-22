from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'updated_at')
    search_fields = ('user__username', 'user__email')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'ایمیل'
