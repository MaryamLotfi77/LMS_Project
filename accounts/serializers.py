from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import APIException
from django.utils import timezone
from .models import UserProfile
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

User = get_user_model()



# ----------------------------------------------------------------------

class ConcurrencyConflict(APIException):
    status_code = 409
    default_detail = 'اطلاعات پروفایل شما توسط سشن دیگری به‌روزرسانی شده است. لطفاً صفحه را رفرش کنید.'
    default_code = 'concurrency_conflict'


# ----------------------------------------------------------------------

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    last_update_time = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'last_update_time']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = instance.user

        client_update_timestamp = request.META.get('HTTP_X_LAST_UPDATE_TIME')

        if client_update_timestamp:
            try:
                client_update_time = timezone.datetime.fromtimestamp(float(client_update_timestamp), tz=timezone.utc)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"detail": "فرمت زمان 'X-Last-Update-Time' اشتباه است."})

            db_last_update = instance.updated_at.replace(microsecond=0)


            if client_update_time < db_last_update:
                raise ConcurrencyConflict()

        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()


        return super().update(instance, validated_data)

#---------------------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user

#--------------------------------------------------

class LogoutSerializer(serializers.Serializer):
    """
    سریالایزر برای باطل کردن توکن Refresh.
    """
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception:

            pass