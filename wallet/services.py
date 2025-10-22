from django.db import transaction
from .models import Wallet, Transaction, TransactionType
from django.db.models import F

class WalletService:
    @staticmethod
    def deposit(user, amount):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=user)
            wallet.balance += amount
            wallet.save()

            Transaction.objects.create_successful_transaction(
                wallet=wallet,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                description=f'شارژ موفق کیف پول به مبلغ {amount} تومان',
            )
            return wallet

    @staticmethod
    def pay_for_enrollment(user, amount, enrollment_obj):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=user)

            if wallet.balance < amount:
                raise ValueError("موجودی کیف پول کافی نیست.")

            wallet.balance = F('balance') - amount
            wallet.save()
            wallet.refresh_from_db()

            Transaction.objects.create_successful_transaction(
                wallet=wallet,
                amount=amount,
                transaction_type=TransactionType.PAYMENT,
                enrollment=enrollment_obj,
                description=f'پرداخت هزینه ثبت‌نام دوره {enrollment_obj.course.title}',
            )
            return wallet

    @staticmethod
    def refund_enrollment(enrollment_obj, amount):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=enrollment_obj.user)
            wallet.balance = F('balance') + amount
            wallet.save()
            wallet.refresh_from_db()

            Transaction.objects.create_successful_transaction(
                wallet=wallet,
                amount=amount,
                transaction_type=TransactionType.REFUND,
                enrollment=enrollment_obj,
                description=f'برگشت وجه ثبت‌نام به دلیل لغو/مشروطی دوره {enrollment_obj.course.title}',
            )
            return wallet