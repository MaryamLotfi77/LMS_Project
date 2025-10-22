from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Category, Course, Level, ClassSession
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LevelSerializer,
    ClassSessionSerializer
)

#-----------------------------------

class IsInstructorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))

# ------------------------------------------------------

class CategoryListCreateView(generics.ListCreateAPIView):

    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]


#----------------------------------------------

class CategoryDetailUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all().prefetch_related('children')
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]

# --------------------------------------------------------

class CourseListCreateView(generics.ListCreateAPIView):

    queryset = Course.objects.all().select_related('category')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]

#---------------------------------------------------------

class CourseDetailUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all().select_related('category')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]

# ---------------------------------------------------------

class LevelListCreateView(generics.ListCreateAPIView):
    serializer_class = LevelSerializer

    def get_queryset(self):
        queryset = Level.objects.all().select_related('course', 'prereq_level')
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]

    def perform_create(self, serializer):
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            serializer.save(course=course)
        else:
            serializer.save()


class LevelDetailUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all().select_related('course', 'prereq_level')
    serializer_class = LevelSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]

# --------------------------------------------------

class ClassSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassSessionSerializer

    def get_queryset(self):
        queryset = ClassSession.objects.all().select_related('level', 'instructor').order_by('start_date')
        level_pk = self.kwargs.get('level_pk')
        if level_pk:
            queryset = queryset.filter(level_id=level_pk)
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]

    def perform_create(self, serializer):
        level_pk = self.kwargs.get('level_pk')
        if level_pk:
            level = get_object_or_404(Level, pk=level_pk)
            serializer.save(level=level)
        else:
            serializer.save()


class ClassSessionDetailUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassSession.objects.all().select_related('level', 'instructor')
    serializer_class = ClassSessionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]