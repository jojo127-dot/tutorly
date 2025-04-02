from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from .models import Course, Interaction, Enrollment
from .serializers import UserSerializer, CourseSerializer, InteractionSerializer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.core.mail import send_mail
from django.conf import settings

# ✅ Content-Based Recommendation
def content_based_recommendation(courses):
    if not courses:
        return Response({"recommended_courses": []})

    course_texts = [f"{course.title} {course.syllabus}" for course in courses]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(course_texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    ranked_indices = np.argsort(similarity_matrix.sum(axis=0))[::-1]
    courses_list = list(courses)
    recommended_courses = [courses_list[int(i)] for i in ranked_indices[:5]]

    serializer = CourseSerializer(recommended_courses, many=True)
    return Response({"recommended_courses": serializer.data})

# ✅ User-Based Collaborative Filtering
def user_based_recommendation(user):
    user_interactions = Interaction.objects.filter(user=user).exclude(rating=None)

    if not user_interactions.exists():
        return []

    similar_users = Interaction.objects.filter(
        course__in=user_interactions.values_list('course', flat=True)
    ).exclude(user=user).values_list('user', flat=True)

    recommended_courses = Interaction.objects.filter(
        user__in=similar_users
    ).values("course").annotate(avg_rating=Avg("rating")).order_by("-avg_rating")[:5]

    return [Course.objects.get(id=entry["course"]) for entry in recommended_courses]

# ✅ Hybrid Recommendation System
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_courses(request):
    user = request.user
    all_courses = Course.objects.all()

    # ✅ Check user interactions
    user_ratings = Interaction.objects.filter(user=user).values("course", "rating")
    
    if not user_ratings.exists():
        print(f"🔹 New user detected: {user.username}. Using content-based recommendations.")
        return content_based_recommendation(all_courses)  # ✅ Fallback for new users

    # ✅ Remove poorly rated courses
    bad_rated_courses = [entry["course"] for entry in user_ratings if entry["rating"] <= 2]
    available_courses = Course.objects.exclude(id__in=bad_rated_courses)

    if not available_courses:
        return Response({"recommended_courses": []})  # No good courses left

    # ✅ Prioritize high-rated courses
    high_rated_courses = [entry["course"] for entry in user_ratings if entry["rating"] >= 4]
    prioritized_courses = [course for course in available_courses if course.id in high_rated_courses]

    # ✅ Use collaborative filtering (only if user has interactions)
    collaborative_courses = user_based_recommendation(user) if user_ratings else []

    # ✅ Ensure collaborative courses don’t include bad-rated ones
    collaborative_courses = [course for course in collaborative_courses if course.id not in bad_rated_courses]

    # ✅ Final recommendations
    recommended_courses = prioritized_courses + collaborative_courses

    # ✅ Remove duplicates & maintain order
    seen = set()
    final_recommendations = []
    for course in recommended_courses:
        if course.id not in seen:
            final_recommendations.append(course)
            seen.add(course.id)

    # ✅ If no user-based recommendations, use content-based
    if not final_recommendations:
        print("🔹 No user-based recommendations found. Using content-based fallback.")
        return content_based_recommendation(all_courses)

    serializer = CourseSerializer(final_recommendations, many=True)
    return Response({"recommended_courses": serializer.data})




# ✅ API to Fetch Data for Training the Model
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendation_data(request):
    courses = Course.objects.all()
    interactions = Interaction.objects.all()

    course_data = CourseSerializer(courses, many=True).data
    interaction_data = InteractionSerializer(interactions, many=True).data

    return Response({"courses": course_data, "interactions": interaction_data})

# ✅ Authentication & User Management
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])

        # ✅ Send Welcome Email
        send_mail(
            "Welcome to Tutorly!",
            f"Hello {user.username},\n\nThank you for registering at Tutorly! Start exploring courses today.\n\nBest,\nTutorly Team",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        refresh = RefreshToken.for_user(user)
        response.data["access_token"] = str(refresh.access_token)
        response.data["refresh_token"] = str(refresh)
        return response

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

from django.db.models import Avg  # ✅ Ensure this is imported

class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.annotate(avg_rating=Avg("interactions__rating"))

    def list(self, request):
        search_query = request.GET.get("search", "")
        min_rating = request.GET.get("min_rating", "")

        courses = Course.objects.annotate(avg_rating=Avg("interactions__rating"))

        if search_query:
            courses = courses.filter(title__icontains=search_query)

        if min_rating:
            courses = courses.filter(avg_rating__gte=min_rating)

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)




class InteractionViewSet(ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=400)

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": f"Welcome back, {username}!",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })

    return Response({"error": "Invalid credentials"}, status=401)

# ✅ Profile & Password Management
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    
    if request.method == "PUT":
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully!", "user": serializer.data})
        return Response(serializer.errors, status=400)
    
    enrolled_courses = Enrollment.objects.filter(user=user).values_list("course__title", flat=True)

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "enrolled_courses": list(enrolled_courses),
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect"}, status=400)

    user.set_password(new_password)
    user.save()

    # ✅ Send Password Change Notification
    send_mail(
        "Password Change Alert",
        f"Hello {user.username},\n\nYour password was successfully changed. If this wasn't you, please reset your password immediately.\n\nBest,\nTutorly Security Team",
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

    return Response({"message": "Password changed successfully!"})

# ✅ Enrollment API
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enroll_course(request, id):
    user = request.user
    try:
        course = Course.objects.get(id=id)
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)

        if created:
            # ✅ Send Enrollment Confirmation Email
            send_mail(
                "Enrollment Confirmation",
                f"Hello {user.username},\n\nYou have successfully enrolled in '{course.title}'. Happy learning!\n\nBest,\nTutorly Team",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "Enrolled successfully!"}, status=201)
        else:
            return Response({"message": "Already enrolled!"}, status=200)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


# ✅ Course Endpoints
@api_view(['GET'])
def welcome_view(request):
    return Response({"message": "Welcome to Tutorly!"})

@api_view(['GET'])
def course_list(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_detail(request, id):
    try:
        course = Course.objects.get(id=id)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_feedback(request, id):
    try:
        course = Course.objects.get(id=id)
        
        # ✅ Print debug info
        feedbacks = Interaction.objects.filter(course=course).exclude(feedback="")  # This filters out empty feedback
        print(f"All feedbacks for {course.title}:", feedbacks)

        serializer = InteractionSerializer(feedbacks, many=True)
        return Response(serializer.data)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_course(request, id):
    try:
        user = request.user
        course = Course.objects.get(id=id)
        rating = request.data.get("rating")
        feedback = request.data.get("feedback", "").strip()  # Ensure it's not just spaces

        if not rating or not (1 <= int(rating) <= 5):
            return Response({"error": "Rating must be between 1 and 5."}, status=400)

        # ✅ Ensure rating is saved, even if feedback is empty
        interaction, created = Interaction.objects.update_or_create(
            user=user, course=course,
            defaults={"rating": rating, "feedback": feedback if feedback else "No feedback"}
        )

        return Response({"message": f"Rated {course.title} with {rating} stars!"})

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def update_progress(request, course_id):
    user = request.user
    enrollment, created = Enrollment.objects.get_or_create(user=user, course_id=course_id)

    if request.method == "GET":
        print(f"Checking progress for user {user.username} in course {course_id}: {enrollment.completed_topics}")
        return Response({"completed_topics": enrollment.completed_topics})

    elif request.method == "POST":
        completed_topics = request.data.get("completed_topics", [])

        if not isinstance(completed_topics, list):
            return Response({"error": "Invalid data format"}, status=400)

        print(f"Updating progress for user {user.username} in course {course_id}: {completed_topics}")
        enrollment.completed_topics = completed_topics
        enrollment.save()

        # ✅ Double-check if progress is saved correctly
        saved_enrollment = Enrollment.objects.get(user=user, course_id=course_id)
        print("Saved Topics:", saved_enrollment.completed_topics)

        return Response({"message": "Progress updated successfully!", "completed_topics": saved_enrollment.completed_topics})
