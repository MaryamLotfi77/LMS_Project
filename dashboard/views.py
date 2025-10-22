from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from .services import DashboardService
from .serializers import DashboardSummarySerializer, CourseStatSerializer, InstructorDashboardSerializer


# ----------------------------------------------------------------------

class IsInstructorOrAdmin(BasePermission):
    message = 'فقط مربیان یا مدیران سیستم مجاز به دسترسی به داشبورد هستند.'

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        is_instructor = hasattr(user, 'role') and user.role == 'INSTRUCTOR'  # فرض بر وجود فیلد role

        return user.is_superuser or user.is_staff or is_instructor


# ----------------------------------------------------------------------

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]

    def get(self, request):

        user = request.user

        #  آمار کلی
        if user.is_superuser or user.is_staff:
            enrollment_stats = DashboardService.get_enrollment_statistics()
            top_courses = DashboardService.get_top_selling_courses()

            data = {
                'summary': DashboardSummarySerializer(enrollment_stats).data,
                'top_courses': CourseStatSerializer(top_courses, many=True).data,
            }


        else:  # IsInstructor
            instructor_stats = DashboardService.get_instructor_stats(user)
            data = {
                'summary': InstructorDashboardSerializer(instructor_stats).data
            }

        return Response(data)