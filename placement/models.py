from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Level
from datetime import timedelta,timezone
# -------------------------------------------------------------------

# مدل آزمون
class Assessment(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان آزمون")
    description = models.TextField(verbose_name="توضیحات آزمون")
    target_level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessments',
        verbose_name="سطح هدف"
    )
    passing_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=60,
        verbose_name="نمره قبولی"
    )
    duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        verbose_name="مدت زمان (دقیقه)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    def __str__(self):
        return self.title

# -------------------------------------------------------------------
# مدل سؤالات

class Question(models.Model):

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'mc', 'چند گزینه‌ای'
        TRUE_FALSE = 'tf', 'درست/غلط'
        TEXT_INPUT = 'ti', 'پاسخ متنی کوتاه'
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="آزمون"
    )
    text = models.TextField(verbose_name="متن سؤال")
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
        verbose_name="نوع سؤال"
    )
    score_weight = models.IntegerField(default=1, verbose_name="وزن نمره")
    correct_answer_text = models.TextField(
        null=True,
        blank=True,
        verbose_name="پاسخ صحیح متنی/بولی"
    )

    def __str__(self):
        return f'{self.assessment.title} - سوال {self.id}'

# -------------------------------------------------------------------
# مدل های گزینه پاسخ
class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="سؤال"
    )
    text = models.CharField(max_length=500, verbose_name="متن گزینه")
    is_correct = models.BooleanField(default=False, verbose_name="پاسخ صحیح")

    def __str__(self):
        return f'{self.text[:50]} ({self.question.id})'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question'],
                condition=models.Q(is_correct=True),
                name='unique_correct_option_per_question'
            )
        ]

# -------------------------------------------------------------------
# مدل نتیجه ارزیابی کاربر

class UserAssessment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessments_taken',
        verbose_name="کاربر"
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name="آزمون"
    )
    final_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نمره نهایی"
    )
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="زمان شروع")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="زمان اتمام")
    is_passed = models.BooleanField(default=False, verbose_name="قبولی")

    @property
    def is_expired(self):
        if self.is_passed and self.end_time:
            return self.end_time < (timezone.now() - timedelta(days=180))
        return False

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.user.username} - {self.assessment.title}'


#------------------------------------------------

#  ذخیره پاسخ های کاربر
class UserAnswer(models.Model):
    user_assessment = models.ForeignKey(
        'UserAssessment',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="نتیجه ارزیابی"
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        verbose_name="سؤال"
    )
    selected_option = models.ForeignKey(
        'Option',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="گزینه انتخابی"
    )
    user_text_answer = models.TextField(
        null=True,
        blank=True,
        verbose_name="پاسخ متنی کاربر"
    )
    is_correct = models.BooleanField(default=False, verbose_name="پاسخ صحیح بود")
    score_earned = models.IntegerField(default=0, verbose_name="نمره کسب شده")

    class Meta:
        verbose_name = "پاسخ کاربر"
        verbose_name_plural = "پاسخ‌های کاربران"
        unique_together = ('user_assessment', 'question')

    def __str__(self):
        return f'{self.user_assessment.user.username} - پاسخ به {self.question.id}'