from django.db import models
from django.db.models import Max


# وضعیت ثبت‌نام و نمره پیش‌نیاز کاربران
class EnrollmentManager(models.Manager):

    def get_user_latest_score(self, user, level_number):

        from .models import EnrollmentStatus

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

        from courses.models import Level

        try:
            current_level = Level.objects.select_related('prereq_level').get(level_number=required_level_number)
        except Level.DoesNotExist:
            return {'status': 'eligible', 'score': 100, 'level': 0, 'reason': 'Level یافت نشد/بدون پیش‌نیاز'}

        prereq_level_obj = current_level.prereq_level

        if prereq_level_obj is None:
            return {'status': 'eligible', 'score': 100, 'level': 0, 'reason': 'بدون پیش‌نیاز'}

        prerequisite_level_num = prereq_level_obj.level_number

        latest_score = self.get_user_latest_score(user, prerequisite_level_num)

        if latest_score is None:
            return {'status': 'ineligible', 'reason': f'نمره لول پیش‌نیاز ({prereq_level_obj.title}) ثبت نشده است.'}

        if latest_score >= 76:
            return {'status': 'pass', 'score': latest_score, 'level': prerequisite_level_num}
        elif 61 <= latest_score <= 75:
            return {'status': 'conditional', 'score': latest_score, 'level': prerequisite_level_num}
        else:  # latest_score < 61
            return {'status': 'fail', 'score': latest_score, 'level': prerequisite_level_num}