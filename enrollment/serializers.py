from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Enrollment, EnrollmentStatus
from .services import EnrollmentService
from courses.models import ClassSession
from courses.serializers import ClassSessionSerializer


# ----------------------------------------------------------------------
class EnrollmentSerializer(serializers.ModelSerializer):

    session_details = ClassSessionSerializer(source='session', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'status', 'final_score', 'enrolled_at',
            'session', 'session_details',
        ]
        read_only_fields = fields


# ----------------------------------------------------------------------
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    course_price = serializers.DecimalField(
        source='session.price', read_only=True, max_digits=10, decimal_places=0
    )

    class Meta:
        model = Enrollment
        fields = ['session', 'user', 'course_price']

    def validate(self, data):
        user = data['user']
        session = data['session']

        if Enrollment.objects.filter(user=user, session=session).exists():
            raise serializers.ValidationError("شما قبلاً در این کلاس ثبت‌نام کرده‌اید.")
        if session.current_enrollment_count >= session.capacity:
            raise serializers.ValidationError("ظرفیت این کلاس پر شده است.")

        prereq_status_data = Enrollment.objects.get_user_prerequisite_status(user, session.level.level_number)

        if prereq_status_data.get('status') == 'ineligible':
            raise serializers.ValidationError({
                "detail": f"شما واجد شرایط ثبت‌نام در این سطح نیستید. {prereq_status_data.get('reason')}"
            })

        data['prereq_status_data'] = prereq_status_data
        return data

    def create(self, validated_data):
        user = validated_data['user']
        session = validated_data['session']
        course_price = session.price
        prereq_status_data = validated_data.pop('prereq_status_data')

        try:
            enrollment = EnrollmentService.create_new_enrollment(
                user=user,
                session=session,
                course_price=course_price,
                prereq_status_data=prereq_status_data
            )
            return enrollment
        except ValidationError as e:
            raise serializers.ValidationError(e.detail)


# ----------------------------------------------------------------------
class EnrollmentScoreUpdateSerializer(serializers.ModelSerializer):
    final_score = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        required=True
    )

    class Meta:
        model = Enrollment
        fields = ['final_score']
        read_only_fields = ['status', 'enrolled_at', 'user', 'session']

    def update(self, instance, validated_data):
        final_score = validated_data.get('final_score')

        try:
            instance = EnrollmentService.finalize_score(instance, final_score)
            return instance
        except Exception as e:
            raise serializers.ValidationError({"detail": f"خطا در ثبت نمره نهایی: {str(e)}"})