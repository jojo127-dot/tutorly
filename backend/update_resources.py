import django
import os

# ✅ Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # Update if project name differs
django.setup()

from tutorly.models import Course

# ✅ Define course resources
course_resources = {
    "Python for Beginners": [
        "https://www.youtube.com/watch?v=rfscVS0vtbw",
        "https://docs.python.org/3/tutorial/index.html",
        "https://www.w3schools.com/python/",
    ],
    "Django Web Development": [
        "https://www.youtube.com/watch?v=F5mRW0jo-U4",
        "https://docs.djangoproject.com/en/stable/",
        "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django",
    ],
    "Natural Language Processing Essentials": [
        "https://www.youtube.com/watch?v=fH7L76y9pD8",
        "https://www.nltk.org/",
        "https://huggingface.co/course/chapter1",
    ],
    "AI for Business Leaders": [
        "https://www.youtube.com/watch?v=2ePf9rue1Ao",
        "https://www.coursera.org/learn/ai-for-everyone",
        "https://mitsloan.mit.edu/LearningEdge/CaseDocs/AI_Strategy_Guide.pdf",
    ],
    "Reinforcement Learning": [
        "https://www.youtube.com/watch?v=vm-rm1ko88g",
        "https://spinningup.openai.com/en/latest/",
        "https://www.packtpub.com/product/deep-reinforcement-learning-hands-on-second-edition/9781838826994",
    ],
    "AI and IoT: Smart Systems Integration": [
        "https://www.youtube.com/watch?v=yS1ibDImAYU",
        "https://arxiv.org/abs/2103.10296",
        "https://developer.ibm.com/technologies/iot/articles/iot-ai-integration/",
    ],
    "Machine Learning Fundamentals": [
        "https://www.youtube.com/watch?v=Gv9_4yMHFhI",
        "https://developers.google.com/machine-learning/crash-course",
        "https://microsoft.github.io/ML-For-Beginners/",
    ],
}

# ✅ Update resources in the database
updated_count = 0
for course in Course.objects.all():
    if course.title in course_resources:
        course.resources = "\n".join(course_resources[course.title])  # Store links as newline-separated text
        course.save()
        updated_count += 1
        print(f"✅ Updated resources for {course.title}")

print(f"\n🎉 Successfully updated {updated_count} courses!")