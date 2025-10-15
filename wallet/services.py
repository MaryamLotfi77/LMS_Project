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