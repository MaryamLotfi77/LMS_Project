from django.urls import path
from wallet.urls import urlpatterns
from. views import (EnrollmentListCreateView,
                    EnrollmentStatusCheckView,
                    EnrollmentUpdateScoreView,
                    )

urlpatterns = [
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('enrollments/status/', EnrollmentStatusCheckView.as_view(), name='enrollment-status-check'),
    path('enrollments/<int:pk>/score/', EnrollmentUpdateScoreView.as_view(), name='enrollment-update-score'),

]