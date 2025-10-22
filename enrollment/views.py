from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Prefetch

from .models import Enrollment, EnrollmentStatus
from .serializers import (
    EnrollmentCreateSerializer,
    EnrollmentScoreUpdateSerializer,
    EnrollmentSerializer,
)


# --------------------------------------------------------------------------------------

class IsInstructorOfThisSessionOrAdmin(BasePermission):
    message = 'فقط مربی کلاس یا مدیر سیستم مجاز به ثبت نمره هستند.'

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.is_staff:
            return True

        return obj.session.instructor == user

# --------------------------------------------------------------------------------------

class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    create_serializer_class = EnrollmentCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.create_serializer_class
        return self.serializer_class

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related(
            'session__level__course',
            'session__instructor'
        ).order_by('-enrolled_at')


# --------------------------------------------------------------------------------------

class EnrollmentStatusCheckView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        next_level_num_str = request.query_params.get('level')

        if not next_level_num_str:
            return Response({"detail": "پارامتر 'level' الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            next_level_num = int(next_level_num_str)
        except ValueError:
            return Response({"detail": "پارامتر 'level' باید یک عدد صحیح باشد."}, status=status.HTTP_400_BAD_REQUEST)

        if next_level_num < 1:
            return Response({"detail": "Level باید بزرگتر از صفر باشد."}, status=status.HTTP_400_BAD_REQUEST)

        prereq_status = Enrollment.objects.get_user_prerequisite_status(request.user, next_level_num)

        return Response(prereq_status)


# --------------------------------------------------------------------------------------

class EnrollmentUpdateScoreView(generics.UpdateAPIView):

    queryset = Enrollment.objects.all().select_related('user', 'session__level__course')
    serializer_class = EnrollmentScoreUpdateSerializer
    permission_classes = [IsAuthenticated, IsInstructorOfThisSessionOrAdmin]

    http_method_names = ['patch']