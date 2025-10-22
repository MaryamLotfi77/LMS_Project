from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailUpdateDestroyView,
    CourseListCreateView, CourseDetailUpdateDestroyView,
    LevelListCreateView, LevelDetailUpdateDestroyView,
    CourseListCreateView, CourseDetailUpdateDestroyView,
    CategoryListCreateView, CategoryDetailUpdateDestroyView,
    ClassSessionListCreateView, ClassSessionDetailUpdateDestroyView,
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailUpdateDestroyView.as_view(), name='category-detail-update-destroy'),

    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailUpdateDestroyView.as_view(), name='course-detail-update-destroy'),
    path('courses/<int:course_pk>/levels/', LevelListCreateView.as_view(), name='level-list-create-by-course'),

    path('levels/<int:pk>/', LevelDetailUpdateDestroyView.as_view(), name='level-detail-update-destroy'),
    path('levels/<int:level_pk>/sessions/', ClassSessionListCreateView.as_view(), name='session-list-create-by-level'),

    path('sessions/<int:pk>/', ClassSessionDetailUpdateDestroyView.as_view(), name='session-detail-update-destroy'),
]