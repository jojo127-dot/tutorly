import os
import sys
import django
import requests

# ✅ Ensure correct project path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # Adjust if needed
django.setup()

from django.contrib.auth.models import User
from tutorly.models import Interaction
from tutorly.views import recommend_courses

def evaluate_recommendation_accuracy(username, k=5):
    """Evaluate recommendation accuracy using Precision@K."""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ Error: User '{username}' not found.")
        return

    print(f"🛠 Debug: Running recommendation evaluation for {username}")

    # ✅ Fetch actual courses the user has interacted with
    actual_interactions = set(Interaction.objects.filter(user=user).values_list("course_id", flat=True))
    print(f"✅ Actual Interactions: {actual_interactions}")

    # ✅ Fetch recommendations from API
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQxNjkwNjY1LCJpYXQiOjE3NDE2ODcwNjUsImp0aSI6IjE1NjE5MzEzNGI2YzQxODFhZGE5OTRlMzgzZTY4ODljIiwidXNlcl9pZCI6MTB9.74AwVK00rQih_xqMrbb5_SsrJ9b6F6qg9KkGExRxG0k"  # ⚠️ Replace with an actual access token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://127.0.0.1:8000/api/recommend_courses/", headers=headers)

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return

    recommended_courses = response.json().get("recommended_courses", [])
    recommended_ids = [course["id"] for course in recommended_courses]

    print(f"✅ Recommended Course IDs: {recommended_ids}")

    # ✅ Compute Precision@K
    relevant_recommendations = len(set(recommended_ids[:k]) & actual_interactions)
    precision_at_k = relevant_recommendations / k

    print(f"🎯 Precision@{k}: {precision_at_k:.2f}")

# ✅ Run evaluation for a test user
evaluate_recommendation_accuracy("testuser", k=5)
