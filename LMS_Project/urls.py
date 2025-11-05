from django.contrib import admin
from django.urls import path,include
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

#-----------------------------------------------

def custom_404_view(request, exception):
    return Response(
        {"detail": "آدرس مورد نظر پیدا نشد. لطفاً آدرس را بررسی کنید.", "code": "not_found"},
        status=status.HTTP_404_NOT_FOUND
    )

def custom_500_view(request):
    return Response(
        {"detail": "خطای داخلی سرور رخ داده است. لطفاً به پشتیبانی اطلاع دهید.", "code": "server_error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

handler404 = custom_404_view
handler500 = custom_500_view

#-------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),

    # مسیرهای jwt
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # سایر اپلیکیشن ها
    path('', include('courses.urls')),
    path('', include('placement.urls')),
    path('', include('wallet.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('enrollment.urls')),
    path('', include('dashboard.urls')),

    # مسیر داکیومنت
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger_ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
