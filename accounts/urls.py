from django.urls import path
from .views import UserProfileUpdateView, RegisterView, LogoutView
urlpatterns = [
    path('profile/', UserProfileUpdateView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]



