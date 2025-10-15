# wallet/urls.py

from django.urls import path
from .views import WalletDetailView, TransactionListView, WalletDepositView

urlpatterns = [
    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),

    path('wallet/deposit/', WalletDepositView.as_view(), name='wallet-deposit'),

    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]