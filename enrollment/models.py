from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import ClassSession
from .managers import EnrollmentManager

# ------------------------------------
class EnrollmentStatus(models.TextChoices):
    ACTIVE = 'active', 'فعال'
    RESERVED = 'reserved', 'رزرو شده'
    CONDITIONAL_PASS = 'conditional_pass', 'قبول مشروط'
    FAILED = 'failed', 'ناموفق'

# --------------------------------------------
class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments', verbose_name="زبان‌آموز")
    objects = EnrollmentManager()
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='enrollments', verbose_name="کلاس")
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.RESERVED, verbose_name="وضعیت")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام")
    final_score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="نمره نهایی",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'session'], name='unique_user_session')
        ]


    def __str__(self):
        return f'{self.user.username} در {self.session.level.title} - وضعیت: {self.get_status_display()}'