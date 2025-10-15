from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="کاربر"
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی پروفایل")


    def __str__(self):
        return f"پروفایل {self.user.get_full_name()}"

    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"