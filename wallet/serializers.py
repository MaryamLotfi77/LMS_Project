from rest_framework import serializers
from .models import Wallet, Transaction, TransactionType
from django.core.validators import MinValueValidator

from .services import WalletService
from enrollment.models import Enrollment

# ----------------------------------------------------------------------

class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    user_id = serializers.IntegerField(source='wallet.user.id', read_only=True)
    enrollment_id = serializers.IntegerField(source='enrollment.id', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'transaction_type', 'transaction_type_display',
            'is_successful', 'created_at', 'description', 'user_id', 'enrollment_id'
        ]
        read_only_fields = fields


# ----------------------------------------------------------------------

class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ['balance', 'updated_at']
        read_only_fields = fields


# ----------------------------------------------------------------------

class WalletDepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(1000)],
        help_text="مبلغ شارژ به تومان"
    )

    def validate_amount(self, value):
        if value % 1000 != 0:
            raise serializers.ValidationError("مبلغ شارژ باید مضربی از ۱۰۰۰ باشد.")
        return value

    def save(self):
        user = self.context['request'].user
        amount = self.validated_data['amount']

        wallet = WalletService.deposit(user=user, amount=amount)

        return wallet