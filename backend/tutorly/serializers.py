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
    resources = serializers.SerializerMethodField()  # Custom method to handle conversion

    class Meta:
        model = Course
        fields = '__all__'
    
    def get_resources(self, obj):
        
        return obj.get_resources_list()

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
