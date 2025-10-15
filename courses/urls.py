from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    CourseListView, CourseDetailView,
    LevelListView, LevelDetailView,
    ClassSessionListView, ClassSessionDetailView,
    EnrollmentListCreateView, EnrollmentStatusCheckView,
    EnrollmentUpdateScoreView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    path('courses/<int:course_pk>/levels/', LevelListView.as_view(), name='level-list-by-course'),
    path('levels/<int:pk>/', LevelDetailView.as_view(), name='level-detail'), # جزئیات لول مستقل

    path('sessions/', ClassSessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', ClassSessionDetailView.as_view(), name='session-detail'),

    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('enrollments/status/', EnrollmentStatusCheckView.as_view(), name='enrollment-status-check'),
    path('enrollments/<int:pk>/score/', EnrollmentUpdateScoreView.as_view(), name='enrollment-update-score'),
]