from rest_framework import serializers
from .models import Category, Course, Level, ClassSession, Enrollment, EnrollmentStatus # EnrollmentStatus را ایمپورت کنید
from wallet.models import Wallet, Transaction, TransactionType

# ----------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children', 'level', 'tree_id']
        read_only_fields = ['level', 'tree_id']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return None


# ----------------------------------------------------------------------

class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'category', 'category_name']
        read_only_fields = ['category_name']


# ----------------------------------------------------------------------

class LevelSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(source='course.title', read_only=True)
    prereq_level_number = serializers.IntegerField(source='prereq_level.level_number', read_only=True)

    class Meta:
        model = Level
        fields = [
            'id',
            'course', 'course_title',
            'level_number',
            'title',
            'prereq_level', 'prereq_level_number'
        ]
        read_only_fields = ['course_title', 'prereq_level_number']


# ----------------------------------------------------------------------

class ClassSessionSerializer(serializers.ModelSerializer):
    level_title = serializers.CharField(source='level.title', read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)

    current_enrollment_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            'id', 'level', 'level_title', 'instructor', 'instructor_name',
            'capacity', 'start_date', 'current_enrollment_count', 'is_full',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'current_enrollment_count', 'is_full', 'created_at', 'updated_at'
        ]


# ----------------------------------------------------------------------


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Enrollment
        fields = ['session', 'user']

    def create(self, validated_data):
        session = validated_data['session']
        user = validated_data['user']
        course_price = session.price

        if Enrollment.objects.filter(user=user, session=session).exists():
            raise serializers.ValidationError("شما قبلاً در این کلاس ثبت‌نام کرده‌اید.")
        if session.is_full:
            raise serializers.ValidationError("ظرفیت این کلاس پر شده است.")

        try:
            user_wallet = user.wallet  
        except Exception:  # Wallet.DoesNotExist:
            raise serializers.ValidationError("کیف پول کاربر یافت نشد. لطفاً با پشتیبانی تماس بگیرید.")

        if user_wallet.balance < course_price:
            remaining_amount = course_price - user_wallet.balance
            raise serializers.ValidationError(
                {"detail": f"موجودی کیف پول شما کافی نیست. {remaining_amount} کسری دارید."}
            )

        next_level_num = session.level.level_number
        prereq_status_data = Enrollment.objects.get_user_prerequisite_status(user, next_level_num)
        prereq_status = prereq_status_data.get('status')

        if prereq_status in ['fail', 'ineligible']:
            reason = prereq_status_data.get('reason', 'پیش‌نیاز لازم را ندارید.')
            raise serializers.ValidationError(
                {"detail": f"شما مجاز به ثبت‌نام در این سطح نیستید. {reason}"}
            )

        from django.db import transaction

        with transaction.atomic():
            user_wallet.balance -= course_price
            user_wallet.save()

            if prereq_status == 'conditional':
                validated_data['status'] = EnrollmentStatus.RESERVED
            elif prereq_status in ['pass', 'eligible']:
                validated_data['status'] = EnrollmentStatus.ACTIVE

            enrollment_instance = super().create(validated_data)

            Transaction.objects.create(
                user=user,
                amount=course_price,
                transaction_type=TransactionType.PAYMENT,
                enrollment=enrollment_instance,
                description=f'پرداخت هزینه برای دوره {session.level.title} ({course_price} تومان)'
            )

        return enrollment_instance
#---------------------------------------------

class EnrollmentSerializer(serializers.ModelSerializer):

    user_info = serializers.CharField(source='user.get_full_name',
                                      read_only=True)
    session_info = ClassSessionSerializer(source='session', read_only=True)

    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_info', 'session', 'session_info',
            'status', 'status_display', 'final_score', 'enrolled_at'
        ]
        read_only_fields = [
            'user', 'session', 'status', 'enrolled_at',
            'user_info', 'session_info', 'status_display'
        ]


# ----------------------------------------------------------------------

class EnrollmentScoreUpdateSerializer(serializers.ModelSerializer):


    class Meta:
        model = Enrollment
        fields = ['final_score', 'status']
        extra_kwargs = {
            'final_score': {'required': True}
        }

    def validate_final_score(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError("نمره نهایی باید بین ۰ تا ۱۰۰ باشد.")
        return value

    def update(self, instance, validated_data):
        final_score = validated_data.get('final_score', instance.final_score)
        user = instance.user

        if final_score >= 76:
            instance.status = EnrollmentStatus.ACTIVE
        elif 61 <= final_score <= 75:
            instance.status = EnrollmentStatus.CONDITIONAL_PASS
        else:  # final_score <= 60
            instance.status = EnrollmentStatus.FAILED

        instance = super().update(instance, {'final_score': final_score, 'status': instance.status})

        # ----------------------------------------------------------------------
        next_level_num = instance.session.level.level_number + 1

        reserved_enrollment = Enrollment.objects.filter(
            user=user,
            session__level__level_number=next_level_num,
            status=EnrollmentStatus.RESERVED
        ).first()

        if reserved_enrollment:
            if instance.status == EnrollmentStatus.ACTIVE:
                reserved_enrollment.status = EnrollmentStatus.ACTIVE
                reserved_enrollment.save()
            elif instance.status == EnrollmentStatus.FAILED:
                reserved_enrollment.status = EnrollmentStatus.FAILED
                reserved_enrollment.save()

        # ----------------------------------------------------------------------

        prereq_enrollment = Enrollment.objects.filter(
            user=user,
            session__level__level_number=instance.session.level.level_number - 1,
            status=EnrollmentStatus.CONDITIONAL_PASS
        ).first()

        if prereq_enrollment:
            if instance.final_score >= 76:
                prereq_enrollment.status = EnrollmentStatus.ACTIVE
                prereq_enrollment.save()
            else:
                prereq_enrollment.status = EnrollmentStatus.FAILED
                prereq_enrollment.save()
                instance.status = EnrollmentStatus.FAILED
                instance.save()
        return instance