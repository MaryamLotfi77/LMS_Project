from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Category, Course, Level, ClassSession, Enrollment, EnrollmentStatus
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LevelSerializer,
    ClassSessionSerializer,
    EnrollmentCreateSerializer,
    EnrollmentSerializer,
    EnrollmentScoreUpdateSerializer
)

# --------------------------------------------------------------------------------------


class IsInstructorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))

# --------------------------------------------------------------------------------------

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all().prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# --------------------------------------------------------------------------------------

class CourseListView(generics.ListAPIView):

    queryset = Course.objects.all().select_related('category')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all().select_related('category')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


# --------------------------------------------------------------------------------------

class LevelListView(generics.ListAPIView):
    serializer_class = LevelSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Level.objects.all().select_related('course', 'prereq_level')
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
        return queryset


class LevelDetailView(generics.RetrieveAPIView):
    queryset = Level.objects.all().select_related('course', 'prereq_level')
    serializer_class = LevelSerializer
    permission_classes = [AllowAny]


# --------------------------------------------------------------------------------------

class ClassSessionListView(generics.ListAPIView):

    queryset = ClassSession.objects.all().select_related('level', 'instructor').order_by('start_date')
    serializer_class = ClassSessionSerializer
    permission_classes = [IsAuthenticated]


class ClassSessionDetailView(generics.RetrieveAPIView):
    queryset = ClassSession.objects.all().select_related('level', 'instructor')
    serializer_class = ClassSessionSerializer
    permission_classes = [IsAuthenticated]


# --------------------------------------------------------------------------------------

class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related('session__level__course').order_by(
            '-enrolled_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EnrollmentStatusCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        next_level_num = request.query_params.get('level')

        if next_level_num is None:
            return Response({"detail": "پارامتر 'level' الزامی است."}, status=400)

        try:
            next_level_num = int(next_level_num)
        except ValueError:
            return Response({"detail": "پارامتر 'level' باید یک عدد باشد."}, status=400)

        prereq_status = Enrollment.objects.get_user_prerequisite_status(request.user, next_level_num)

        return Response(prereq_status)


# --------------------------------------------------------------------------------------

class EnrollmentUpdateScoreView(generics.UpdateAPIView):
    queryset = Enrollment.objects.all().select_related('user', 'session__level__course')
    serializer_class = EnrollmentScoreUpdateSerializer
    permission_classes = [IsInstructorOrAdmin]
    http_method_names = ['patch']