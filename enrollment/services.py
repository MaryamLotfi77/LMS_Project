from django.db import transaction
from django.db.models import Q
from .models import Enrollment, EnrollmentStatus
from wallet.services import WalletService
from rest_framework.exceptions import ValidationError


class EnrollmentService:
    @staticmethod
    def _handle_refund(enrollment_obj, amount):
        try:
            WalletService.refund_enrollment(enrollment_obj, amount)
        except Exception as e:
            print(f"Error during refund for enrollment {enrollment_obj.id}: {e}")

    @staticmethod
    @transaction.atomic
    def create_new_enrollment(user, session, course_price, prereq_status_data):

        if Enrollment.objects.filter(user=user, session=session).exists():
            raise ValidationError("شما قبلاً در این کلاس ثبت‌نام کرده‌اید.")
        if session.is_full:
            raise ValidationError("ظرفیت این کلاس پر شده است.")

        prereq_status = prereq_status_data.get('status')

        if prereq_status == 'ineligible':
            raise ValidationError({
                "detail": f"شما واجد شرایط ثبت‌نام در این سطح نیستید. {prereq_status_data.get('reason')}"
            })


        if prereq_status == 'pass' or prereq_status == 'eligible':
            initial_status = EnrollmentStatus.ACTIVE
        else:
            initial_status = EnrollmentStatus.RESERVED
        enrollment_obj = Enrollment.objects.create(
            user=user,
            session=session,
            status=initial_status,
        )

        try:
            WalletService.pay_for_enrollment(
                user=user,
                amount=course_price,
                enrollment_obj=enrollment_obj
            )
            return enrollment_obj

        except ValueError as e:
            enrollment_obj.delete()
            raise ValidationError({"detail": str(e)})
        except Exception as e:
            enrollment_obj.delete()
            raise ValidationError({"detail": f"خطا در عملیات پرداخت: {e}"})



#----------------------------------------

@staticmethod
@transaction.atomic
def finalize_score(enrollment_instance, final_score):
    reserved_enrollment = enrollment_instance
    current_level_num = enrollment_instance.session.level.level_number
    user = enrollment_instance.user

    if final_score < 61:
        new_status = EnrollmentStatus.FAILED
    elif 61 <= final_score <= 75:
        new_status = EnrollmentStatus.CONDITIONAL_PASS
    else:  # final_score >= 76
        new_status = EnrollmentStatus.ACTIVE

    # =========================================================

    # مدیریت وضعیت ثبت‌نام فعلی
    if reserved_enrollment:
        if new_status in [EnrollmentStatus.ACTIVE, EnrollmentStatus.CONDITIONAL_PASS]:
            reserved_enrollment.status = EnrollmentStatus.ACTIVE
            reserved_enrollment.save()
        elif new_status == EnrollmentStatus.FAILED:

            reserved_enrollment.status = EnrollmentStatus.FAILED
            reserved_enrollment.save()

            EnrollmentService._handle_refund(reserved_enrollment, reserved_enrollment.session.price)

    # =========================================================

    from courses.models import Level

    try:
        prereq_level = enrollment_instance.session.level.prereq_level

        if prereq_level:
            prereq_enrollment = Enrollment.objects.filter(
                user=user,
                session__level=prereq_level,
                status=EnrollmentStatus.CONDITIONAL_PASS
            ).first()

        else:
            prereq_enrollment = None

    except Level.DoesNotExist:
        prereq_enrollment = None

    if prereq_enrollment:
        if final_score >= 76:
            prereq_enrollment.status = EnrollmentStatus.ACTIVE
            prereq_enrollment.save()
        else:
            prereq_enrollment.status = EnrollmentStatus.FAILED
            prereq_enrollment.save()

            enrollment_instance.status = EnrollmentStatus.FAILED
            enrollment_instance.save()

            EnrollmentService._handle_refund(enrollment_instance, enrollment_instance.session.price)
            EnrollmentService._handle_refund(prereq_enrollment, prereq_enrollment.session.price)

    enrollment_instance.final_score = final_score
    enrollment_instance.save()

    return enrollment_instance