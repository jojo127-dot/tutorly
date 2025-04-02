from django.contrib import admin
from django.contrib.auth.models import User
from .models import Course, Interaction, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category',"instructor")  # Removed 'created_at'
    search_fields = ('title', 'category')
    list_filter = ("category",)

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'feedback')
    search_fields = ('user__username', 'course__title')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('course',)