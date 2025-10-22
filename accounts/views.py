from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from django. contrib. auth import get_user_model
from .serializers import (
    UserProfileUpdateSerializer,
    RegisterSerializer,
    LogoutSerializer
)



class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

#-------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    model = get_user_model()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]



#--------------------------------------------------------

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({"detail": "با موفقیت خارج شدید."}, status=status.HTTP_205_RESET_CONTENT)

