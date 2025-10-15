from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


#------------------------------------

class EnrollmentStatus(models.TextChoices):
    ACTIVE = 'active', 'فعال'
    RESERVED = 'reserved', 'رزرو شده'
    CONDITIONAL_PASS = 'conditional_pass', 'قبول مشروط'
    FAILED = 'failed', 'ناموفق'

#--------------------------------------

class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته‌بندی")
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="والد"
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name



#----------------------------------------

class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses', verbose_name="دسته‌بندی")
    title = models.CharField(max_length=200, verbose_name="عنوان دوره")
    description = models.TextField(verbose_name="توضیحات")

    def __str__(self):
        return self.title




#--------------------------------------------

class Level(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='levels', verbose_name="دوره")
    level_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(25)],
        verbose_name="شماره لول (۱ تا ۲۵)"
    )
    title = models.CharField(max_length=100, verbose_name="عنوان لول")
    prereq_level = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_levels',
        verbose_name="پیش‌نیاز لول"
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'level_number'], name='unique_course_level')
        ]
        ordering = ['level_number']


    def __str__(self):
        return f'{self.course.title} - Level {self.level_number}'

    @property
    def next_level(self):
        try:
            return Level.objects.get(course=self.course, level_number=self.level_number + 1)
        except Level.DoesNotExist:
            return None

    # اعنبارسنجی
    def clean(self):
        super().clean()
        if self.prereq_level and self.prereq_level.course != self.course:
            raise ValidationError("پیش‌نیاز لول باید از همان دوره باشد.")

        if self.prereq_level and self.prereq_level == self:
            raise ValidationError("پیش‌نیاز لول نمی‌تواند برابر با خودش باشد.")
        seen = set()
        current = self.prereq_level

        while current:
            if current == self:
                raise ValidationError("چرخه در پیش‌نیازی لول غیرمجاز است.")
            if current in seen:
                break
            seen.add(current)
            current = current.prereq_level


#----------------------------------------
class ClassSession(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='sessions', verbose_name="سطح")
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_staff': True},
        verbose_name="استاد"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="هزینه کلاس"
    )
    capacity = models.IntegerField(validators=[MinValueValidator(1)], default=20, verbose_name="ظرفیت")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین ویرایش")


    @property
    # تعداد ثبت نام ها
    def current_enrollment_count(self):
        return self.enrollments.filter(status__in=[EnrollmentStatus.ACTIVE, EnrollmentStatus.RESERVED]).count()

    @property
    # بررسی پر بودن کلاس
    def is_full(self):
        return self.current_enrollment_count >= self.capacity


    def __str__(self):
        return f'{self.level.title} - {self.start_date.strftime("%Y-%m-%d")} (ظرفیت: {self.current_enrollment_count}/{self.capacity})'

#--------------------------------------------


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments', verbose_name="زبان‌آموز")
    from .managers import EnrollmentManager
    objects = EnrollmentManager()
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='enrollments', verbose_name="کلاس")
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.RESERVED, verbose_name="وضعیت")
    final_score = models.IntegerField(null=True, blank=True, verbose_name="نمره نهایی")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام")


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'session'], name='unique_user_session')
        ]
    def __str__(self):
        return f'{self.user.username} در {self.session.level.title} - وضعیت: {self.get_status_display()}'