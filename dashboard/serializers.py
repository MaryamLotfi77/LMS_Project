from rest_framework import serializers


class CourseStatSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    total_enrollments = serializers.IntegerField(read_only=True)


# ----------------------------------------------------------------------
class DashboardSummarySerializer(serializers.Serializer):
    # آمار کلی
    total_enrollments = serializers.IntegerField(read_only=True)
    active_enrollments = serializers.IntegerField(read_only=True)
    reserved_enrollments = serializers.IntegerField(read_only=True)

    # آمار مربیان (اختیاری)
    total_sessions = serializers.IntegerField(required=False)
    total_students = serializers.IntegerField(required=False)
    active_students = serializers.IntegerField(required=False)


# ----------------------------------------------------------------------


class InstructorDashboardSerializer(serializers.Serializer):
    total_sessions = serializers.IntegerField()
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()