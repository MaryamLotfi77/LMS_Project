from django.contrib import admin
from .models import Wallet, Transaction


# ----------------------------------------------------------------------

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'user_full_name',
        'balance',
        'updated_at'
    )
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name'
    )
    readonly_fields = ('balance', 'updated_at', 'user',)
    list_filter = ('updated_at',)

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'کاربر'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ----------------------------------------------------------------------

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'user_wallet',
        'amount',
        'transaction_type',
        'is_successful',
        'created_at',
    )
    search_fields = (
        'wallet__user__username',
        'wallet__user__first_name',
        'description'
    )
    list_filter = (
        'is_successful',
        'transaction_type',
        'created_at'
    )
    readonly_fields = (
        'amount',
        'transaction_type',
        'enrollment',
        'created_at',
        'is_successful',
    )


    def user_wallet(self, obj):
        return f'{obj.wallet.user.get_full_name() or obj.wallet.user.username} (ID: {obj.wallet.id})'
    user_wallet.short_description = 'کاربر (کیف پول)'

    def transaction_id(self, obj):
        return f'T#{str(obj.id)[:5]}...'
    transaction_id.short_description = 'شناسه تراکنش'

    def has_add_permission(self, request):
        return False