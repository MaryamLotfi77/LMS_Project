from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


# ---------------------------------------------------------------------

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name="کاربر"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="موجودی"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")

    def __str__(self):
        return f'کیف پول {self.user.get_full_name()} | موجودی: {self.balance} تومان'

    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف پول‌ها"


# ---------------------------------------------------------------------

class TransactionType(models.TextChoices):
    DEPOSIT = 'deposit', 'شارژ کیف پول'
    PAYMENT = 'payment', 'پرداخت هزینه دوره'
    REFUND = 'refund', 'برگشت وجه'


# ----------------------------------------------------------------------

class TransactionManager(models.Manager):
    def create_successful_transaction(self, wallet, amount, transaction_type, **kwargs):
        return self.create(
            wallet=wallet,
            amount=amount,
            transaction_type=transaction_type,
            is_successful=True,
            **kwargs
        )


# ----------------------------------------------------------------------

class Transaction(models.Model):
    objects = TransactionManager()

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="کیف پول مرتبط"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="مبلغ",
        validators=[MinValueValidator(1)]
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        verbose_name="نوع تراکنش"
    )
    enrollment = models.ForeignKey(
        'courses.Enrollment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ثبت‌نام مرتبط"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تراکنش")
    is_successful = models.BooleanField(default=True, verbose_name="موفقیت‌آمیز")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    def __str__(self):
        return f'[{self.get_transaction_type_display()}] {self.amount} ({self.wallet.user.username})'

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ['-created_at']