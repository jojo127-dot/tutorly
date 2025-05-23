"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tutorly.views import (
    UserViewSet, CourseViewSet, InteractionViewSet, 
    RegisterUserView, login_user, welcome_view, course_list
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Initialize API Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'interactions', InteractionViewSet, basename='interaction')

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # API Routes
    path('api/', include(router.urls)),

    # Authentication Endpoints
    path('api/register/', RegisterUserView.as_view(), name='register'),
    path('api/login/', login_user, name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Additional Endpoints
    path('', welcome_view, name='welcome'),
    path('api/course-list/', course_list, name='course_list'),
     path('api/', include('tutorly.urls')), 
]
