import sys
from datetime import datetime
from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService
from app.models.models import Course, Topic


class CLI:
    def __init__(self):
        self.storage = StorageService()
        self.planner = PlannerService(self.storage)
    
    def display_menu(self):
        print("\n" + "="*50)
        print("  SKILL-AWARE STUDY PLANNER")
        print("="*50)
        print("\n1. Add Course")
        print("2. Add Topic to Course")
        print("3. View All Courses")
        print("4. View Topics for Course")
        print("5. Generate Daily Study Plan")
        print("6. Update Topic Skill Level")
        print("7. Exit")
        print("\n" + "-"*50)
    
    def add_course(self):
        print("\n--- Add New Course ---")
        name = input("Course name: ").strip()
        
        while True:
            exam_date_str = input("Exam date (YYYY-MM-DD): ").strip()
            try:
                exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
                if exam_date < datetime.now():
                    print("Error: Exam date must be in the future!")
                    continue
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
        
        try:
            course = Course(name=name, exam_date=exam_date)
            created_course = self.storage.create_course(course)
            print(f"\n✓ Course created successfully! (ID: {created_course.id})")
        except Exception as e:
            print(f"\n✗ Error creating course: {e}")
    
    def add_topic(self):
        print("\n--- Add Topic to Course ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses available. Please add a course first.")
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  {course.id}. {course.name} (Exam: {course.exam_date.strftime('%Y-%m-%d')})")
        
        while True:
            try:
                course_id = int(input("\nSelect course ID: "))
                if any(c.id == course_id for c in courses):
                    break
                print("Invalid course ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        name = input("Topic name: ").strip()
        
        while True:
            try:
                weight = float(input("Topic weight (0-1): "))
                if 0 <= weight <= 1:
                    break
                print("Weight must be between 0 and 1!")
            except ValueError:
                print("Please enter a valid number!")
        
        while True:
            try:
                skill_level = float(input("Current skill level (0-100): "))
                if 0 <= skill_level <= 100:
                    break
                print("Skill level must be between 0 and 100!")
            except ValueError:
                print("Please enter a valid number!")
        
        try:
            topic = Topic(
                course_id=course_id,
                name=name,
                weight=weight,
                skill_level=skill_level
            )
            created_topic = self.storage.create_topic(topic)
            print(f"\n✓ Topic created successfully! (ID: {created_topic.id})")
            
            validation = self.planner.validate_course_topics(course_id)
            if not validation['valid']:
                print(f"\n⚠ Warning: Total weight for this course is {validation['total_weight']:.2f}")
                print("  (Recommended: weights should sum to 1.0)")
        except Exception as e:
            print(f"\n✗ Error creating topic: {e}")
    
    def view_courses(self):
        print("\n--- All Courses ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses found.")
            return
        
        for course in courses:
            days_until = (course.exam_date - datetime.now()).days
            print(f"\nID: {course.id}")
            print(f"  Name: {course.name}")
            print(f"  Exam Date: {course.exam_date.strftime('%Y-%m-%d')}")
            print(f"  Days Until Exam: {days_until}")
            
            topics = self.storage.get_topics_by_course(course.id)
            print(f"  Topics: {len(topics)}")
    
    def view_topics(self):
        print("\n--- View Topics ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses available.")
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  {course.id}. {course.name}")
        
        while True:
            try:
                course_id = int(input("\nSelect course ID: "))
                if any(c.id == course_id for c in courses):
                    break
                print("Invalid course ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        topics = self.storage.get_topics_by_course(course_id)
        
        if not topics:
            print("\nNo topics found for this course.")
            return
        
        print(f"\n--- Topics for Course ID {course_id} ---")
        for topic in topics:
            print(f"\nID: {topic.id}")
            print(f"  Name: {topic.name}")
            print(f"  Weight: {topic.weight}")
            print(f"  Skill Level: {topic.skill_level}%")
    
    def generate_plan(self):
        print("\n--- Generate Daily Study Plan ---")
        
        while True:
            try:
                hours = float(input("Available study hours today: "))
                if hours > 0:
                    break
                print("Hours must be greater than 0!")
            except ValueError:
                print("Please enter a valid number!")
        
        plan = self.planner.generate_daily_plan(hours)
        
        if not plan.allocated_topics:
            print("\n⚠ No topics to study. Add courses and topics first!")
            return
        
        print("\n" + "="*70)
        print("  📚 YOUR DAILY STUDY PLAN")
        print("="*70)
        print(f"\nTotal Available Hours: {plan.daily_hours:.1f}h")
        print(f"Total Allocated Hours: {plan.get_total_allocated_hours():.1f}h\n")
        
        for i, item in enumerate(plan.allocated_topics, 1):
            print(f"{i}. {item['topic'].name} ({item['course'].name})")
            print(f"   Priority Score: {item['priority_score']:.3f}")
            print(f"   Urgency Factor: {item['urgency_factor']:.1f}x")
            print(f"   Current Skill: {item['topic'].skill_level}%")
            print(f"   ⏱ Study Time: {item['allocated_hours']:.1f} hours")
            print()
    
    def update_skill(self):
        print("\n--- Update Topic Skill Level ---")
        
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("No topics available.")
            return
        
        print("\nAll Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name}) - Current: {topic.skill_level}%")
        
        while True:
            try:
                topic_id = int(input("\nSelect topic ID: "))
                if any(t.id == topic_id for t in all_topics):
                    break
                print("Invalid topic ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        while True:
            try:
                new_skill = float(input("New skill level (0-100): "))
                if 0 <= new_skill <= 100:
                    break
                print("Skill level must be between 0 and 100!")
            except ValueError:
                print("Please enter a valid number!")
        
        if self.storage.update_topic_skill(topic_id, new_skill):
            print(f"\n✓ Skill level updated successfully!")
        else:
            print(f"\n✗ Error updating skill level.")
    
    def run(self):
        print("\n🎓 Welcome to the Skill-Aware Study Planner!")
        
        while True:
            self.display_menu()
            choice = input("Select an option (1-7): ").strip()
            
            if choice == '1':
                self.add_course()
            elif choice == '2':
                self.add_topic()
            elif choice == '3':
                self.view_courses()
            elif choice == '4':
                self.view_topics()
            elif choice == '5':
                self.generate_plan()
            elif choice == '6':
                self.update_skill()
            elif choice == '7':
                print("\n👋 Goodbye! Happy studying!")
                sys.exit(0)
            else:
                print("\n✗ Invalid option. Please try again.")


if __name__ == "__main__":
    cli = CLI()
    cli.run()
