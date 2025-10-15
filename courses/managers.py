from django.db import models
from django.db.models import Max
from .models import EnrollmentStatus

# وضعیت ثبت‌نام و نمره پیش‌نیاز کاربران
class EnrollmentManager(models.Manager):

    def get_user_latest_score(self, user, level_number):
        try:
            return self.filter(
                user=user,
                session__level__level_number=level_number,
                final_score__isnull=False,
                status__in=[EnrollmentStatus.ACTIVE, EnrollmentStatus.CONDITIONAL_PASS]
            ).latest('enrolled_at').final_score
        except self.model.DoesNotExist:
            return None

    def get_user_prerequisite_status(self, user, required_level_number):
        prerequisite_level_num = required_level_number - 1

        if prerequisite_level_num < 1:
            return {'status': 'eligible', 'score': 100, 'level': 0}

        latest_score = self.get_user_latest_score(user, prerequisite_level_num)

        if latest_score is None:
            return {'status': 'ineligible', 'reason': f'نمره لول {prerequisite_level_num} ثبت نشده است.'}

        if latest_score >= 76:
            return {'status': 'pass', 'score': latest_score, 'level': prerequisite_level_num}
        elif 61 <= latest_score <= 75:
            return {'status': 'conditional', 'score': latest_score, 'level': prerequisite_level_num}
        else:
            return {'status': 'fail', 'score': latest_score, 'level': prerequisite_level_num}