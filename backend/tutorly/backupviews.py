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

    # ✅ 1. Get user's past interactions (rating & feedback)
    user_ratings = Interaction.objects.filter(user=user).values("course", "rating")
    print(f"User {user.username} ratings:", user_ratings)

    # ✅ 2. Remove courses the user rated poorly (1 or 2 stars)
    bad_rated_courses = [entry["course"] for entry in user_ratings if entry["rating"] <= 2]
    print(f"Bad rated courses:", bad_rated_courses)

    # ✅ 3. Exclude bad courses
    available_courses_queryset = Course.objects.exclude(id__in=bad_rated_courses)
    available_courses_queryset = list(available_courses_queryset)  # Ensure it's a list
    print(f"Available courses after filter:", available_courses_queryset)

    if not available_courses_queryset:
        return Response({"recommended_courses": []})  # No good courses left

    # ✅ 4. Prioritize courses the user rated highly (4 or 5 stars)
    high_rated_courses = [entry["course"] for entry in user_ratings if entry["rating"] >= 4]
    prioritized_courses = [course for course in available_courses_queryset if course.id in high_rated_courses]
    print(f"Prioritized (high-rated) courses:", prioritized_courses)

    # ✅ 5. Use collaborative filtering for unreviewed courses
    collaborative_courses = user_based_recommendation(user)

    # 🔥 **NEW FIX: Remove bad-rated courses from collaborative recommendations**
    collaborative_courses = [course for course in collaborative_courses if course.id not in bad_rated_courses]
    print(f"Filtered Collaborative courses:", collaborative_courses)

    # ✅ 6. Final Recommendations (User Priority → Collaborative → Content-Based)
    recommended_courses = prioritized_courses + collaborative_courses

    # ✅ 7. Remove duplicates while keeping order
    seen = set()
    final_recommendations = []
    for course in recommended_courses:
        if course.id not in seen:
            final_recommendations.append(course)
            seen.add(course.id)

    print(f"Final Recommendations:", final_recommendations)

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
        refresh = RefreshToken.for_user(user)
        response.data["access_token"] = str(refresh.access_token)
        response.data["refresh_token"] = str(refresh)
        return response

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

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
    return Response({"message": "Password changed successfully!"})

# ✅ Enrollment API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, id):
    user = request.user
    try:
        course = Course.objects.get(id=id)
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)

        if created:
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


@api_view(["GET", "POST"])  # ✅ Allow both GET and POST
@permission_classes([IsAuthenticated])
def update_progress(request, course_id):
    user = request.user

    try:
        enrollment, created = Enrollment.objects.get_or_create(user=user, course_id=course_id)

        if request.method == "GET":
            return Response({"completed_topics": enrollment.completed_topics})  # ✅ Return saved progress

        elif request.method == "POST":
            completed_topics = request.data.get("completed_topics", [])

            if not isinstance(completed_topics, list):
                return Response({"error": "Invalid data format"}, status=400)

            enrollment.completed_topics = completed_topics
            enrollment.save()
            return Response({"message": "Progress updated successfully!", "completed_topics": completed_topics})

    except Enrollment.DoesNotExist:
        return Response({"error": "Enrollment not found"}, status=404)



from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Interaction

# ✅ User Serializer (Allows Profile Update)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Password only for registration

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', "")
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user profile (username & email only)."""
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance

# ✅ Course Serializer
class CourseSerializer(serializers.ModelSerializer):

    avg_rating = serializers.FloatField(read_only=True)  # ✅ Include average rating
    resources = serializers.ListField(child=serializers.URLField(), required=False)  # ✅ Ensure URLs are valid
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'price', 'duration', 'syllabus',"category","avg_rating","resources"]

# ✅ Interaction Serializer (Ensures rating can be written)
class InteractionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Show username instead of ID
    course = serializers.StringRelatedField()
    
    class Meta:
        model = Interaction
        fields = ['id', 'user', 'course', 'rating', 'feedback']
        extra_kwargs = {
            'rating': {'required': True},  # ✅ Ensure rating is required
            'feedback': {'required': False},  # ✅ Allow empty feedback
        }
