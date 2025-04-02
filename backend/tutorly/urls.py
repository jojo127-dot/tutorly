from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # Import views from the current app
from .views import user_profile, enroll_course,change_password,update_progress

# ✅ Initialize the DRF Router
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'interactions', views.InteractionViewSet, basename='interaction')

# ✅ Define urlpatterns
urlpatterns = [
    # Include the DRF router endpoints
    path('', include(router.urls)),
    
    # Individual endpoints
    path('welcome/', views.welcome_view, name='welcome_view'),  # Welcome message
    path('courses/', views.course_list, name='course_list'),  # List all courses
    path('courses/<int:id>/', views.course_detail, name='course_detail'),  # Course details
    path('courses/<int:id>/rate/', views.rate_course, name='rate_course'),  # Rate a course
    path('courses/<int:id>/feedback/', views.course_feedback, name='course_feedback'),  # View course feedback
    
    # ✅ FIXED: Updated enrollment URL to match frontend
    path('courses/<int:id>/enroll/', enroll_course, name='enroll-course'),

    # User-related endpoints
    path('register/', views.RegisterUserView.as_view(), name='register_user'),  # User registration
    path('login/', views.login_user, name='login_user'),  # User login
    path('recommendation_data/', views.recommendation_data, name='recommendation_data'),
    path('recommend_courses/', views.recommend_courses, name='recommend_courses'),
    path("user/profile/", user_profile, name="user-profile"),
    path("user/change-password/", change_password, name="change-password"),
    path("courses/<int:course_id>/progress/", update_progress, name="update-progress"),
]
