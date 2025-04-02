from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    syllabus = models.TextField(blank=True, null=True)
    instructor = models.CharField(max_length=255, default="Unknown Instructor")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    duration = models.CharField(max_length=50, blank=True, null=True)
    resources = models.TextField(blank=True, null=True)
    def get_resources_list(self):
        """Convert stored newline-separated resources into a clean list."""
        if self.resources:
            # Remove surrounding quotes and split by `\n`
            cleaned_resources = self.resources.strip().strip('"')
            return [resource.strip() for resource in cleaned_resources.split("\\n") if resource.strip()]
        return []



    # 🆕 New Field: Category
    CATEGORY_CHOICES = [
        ("Programming", "Programming"),
        ("Data Science", "Data Science"),
        ("Design", "Design"),

    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Programming')

    def __str__(self):
        return self.title



class Interaction(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='interactions')
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Course: {self.course.title}, User: {self.user.username}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_topics = models.JSONField(default=list)
    class Meta:
        unique_together = ('user', 'course')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.user.username} - {self.course.title} (Completed: {len(self.completed_topics)})"