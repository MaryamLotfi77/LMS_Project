from enrollment.models import Enrollment, EnrollmentStatus
from courses.models import ClassSession, Course
from django.db.models import Count, Sum, F, DecimalField


class DashboardService:
    @staticmethod
    # آمار ثبت نام کنندگان
    def get_enrollment_statistics():
        total_enrollments = Enrollment.objects.count()
        active_enrollments = Enrollment.objects.filter(status=EnrollmentStatus.ACTIVE).count()
        reserved_enrollments = Enrollment.objects.filter(status=EnrollmentStatus.RESERVED).count()

        return {
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
            'reserved_enrollments': reserved_enrollments,
        }

    @staticmethod
    def get_top_selling_courses(limit=5):
    # پرفروشترین دوره ها
        return Course.objects.annotate(
            total_enrollments=Count('levels__sessions__enrollments', distinct=True)
        ).order_by('-total_enrollments')[:limit].values('title', 'total_enrollments')

    @staticmethod
    def get_instructor_stats(user):
    # آمار ثبت نام کنندهها و نمرات برای یک مربی خاص
        total_sessions = ClassSession.objects.filter(instructor=user).count()

        enrollment_stats = Enrollment.objects.filter(
            session__instructor=user
        ).aggregate(
            total_students=Count('id', distinct=True),
            active_students=Count('id', filter=Q(status=EnrollmentStatus.ACTIVE)),

        )
        return {
            'total_sessions': total_sessions,
            **enrollment_stats,
        }