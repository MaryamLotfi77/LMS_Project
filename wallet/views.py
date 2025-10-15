from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, WalletDepositSerializer


# ----------------------------------------------------------------------

class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.wallet

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Wallet.DoesNotExist:
            wallet_obj = Wallet.objects.create(user=request.user, balance=0)
            return Response(WalletSerializer(wallet_obj).data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.wallet.transactions.all().order_by('-created_at')


# ----------------------------------------------------------------------

class WalletDepositView(generics.GenericAPIView):
    serializer_class = WalletDepositSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet = serializer.save()

        return Response({
            "detail": "عملیات شارژ موفقیت آمیز بود.",
            "new_balance": wallet.balance
        }, status=status.HTTP_200_OK)