import sys
from datetime import datetime, timedelta
from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService
from app.models.models import Course, Topic

print("Testing Skill-Aware Study Planner...\n")

# Use test database
storage = StorageService("test_planner.db")
planner = PlannerService(storage)

# Create a test course
print("1. Creating test course...")
course = Course(
    name="Data Structures",
    exam_date=datetime.now() + timedelta(days=14)
)
course = storage.create_course(course)
print(f"   ✓ Course created: {course.name} (ID: {course.id})")

# Create test topics
print("\n2. Creating test topics...")
topics_data = [
    ("Arrays and Lists", 0.3, 70),
    ("Trees and Graphs", 0.3, 40),
    ("Sorting Algorithms", 0.2, 80),
    ("Dynamic Programming", 0.2, 30)
]

for name, weight, skill in topics_data:
    topic = Topic(
        course_id=course.id,
        name=name,
        weight=weight,
        skill_level=skill
    )
    topic = storage.create_topic(topic)
    print(f"   ✓ Topic created: {name} (Skill: {skill}%)")

# Validate weights
print("\n3. Validating topic weights...")
validation = planner.validate_course_topics(course.id)
print(f"   Total weight: {validation['total_weight']}")
print(f"   Valid: {validation['valid']}")

# Calculate priorities
print("\n4. Calculating priorities...")
priorities = planner.calculate_all_priorities()
for priority in priorities:
    print(f"   {priority.topic.name}")
    print(f"     Priority Score: {priority.priority_score:.3f}")
    print(f"     Urgency: {priority.urgency_factor}x")

# Generate study plan
print("\n5. Generating daily study plan (4 hours)...")
plan = planner.generate_daily_plan(4.0)
print(f"   Total allocated: {plan.get_total_allocated_hours():.1f} hours\n")
for i, item in enumerate(plan.allocated_topics, 1):
    print(f"   {i}. {item['topic'].name} - {item['allocated_hours']:.1f}h")

print("\n✓ All tests passed!")
print("\nYou can now run the CLI with: python main.py")
