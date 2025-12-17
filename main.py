import sys
from datetime import datetime
from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService
from app.services.quiz_service import QuizService
from app.services.skill_tracking_service import SkillTrackingService
from app.services.study_session_service import StudySessionService
from app.services.progress_service import ProgressVisualizationService
from app.models.models import Course, Topic, Quiz, QuizQuestion


class CLI:
    def __init__(self):
        self.storage = StorageService()
        self.planner = PlannerService(self.storage)
        self.quiz_service = QuizService(self.storage.db)
        self.skill_tracking = SkillTrackingService(self.storage.db)
        self.study_session = StudySessionService(self.storage.db)
        self.progress_viz = ProgressVisualizationService(self.storage)
    
    def display_menu(self):
        print("\n" + "="*50)
        print("  SKILL-AWARE STUDY PLANNER")
        print("="*50)
        print("\n--- Course & Topic Management ---")
        print("1. Add Course")
        print("2. Add Topic to Course")
        print("3. View All Courses")
        print("4. View Topics for Course")
        print("\n--- Study Planning ---")
        print("5. Generate Daily Study Plan")
        print("6. View Weak Topics")
        print("\n--- Study Sessions ---")
        print("7. Start Study Session")
        print("8. End Study Session")
        print("9. View Study Time Statistics")
        print("\n--- Skill Tracking ---")
        print("10. Manual Skill Self-Assessment")
        print("11. View Skill History")
        print("\n--- Quizzes ---")
        print("12. Create Quiz for Topic")
        print("13. Take Quiz")
        print("14. View Quiz Results")
        print("\n--- Progress & Analytics ---")
        print("15. View Progress Charts")
        print("16. View Weakest Topics Summary")
        print("\n--- System ---")
        print("17. Apply Skill Decay")
        print("18. Exit")
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
        
        use_adaptive = input("Use adaptive planning? (y/n): ").strip().lower() == 'y'
        
        plan = self.planner.generate_daily_plan(hours, adaptive=use_adaptive)
        
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
    
    def view_weak_topics(self):
        print("\n--- Weak Topics Requiring Attention ---")
        weak_topics = self.planner.detect_weak_topics()
        
        if not weak_topics:
            print("\n✓ No weak topics detected. Keep up the good work!")
            return
        
        print(f"\nFound {len(weak_topics)} topics that need attention:\n")
        for i, item in enumerate(weak_topics[:10], 1):
            print(f"{i}. {item['topic'].name} ({item['course'].name})")
            print(f"   Skill Level: {item['topic'].skill_level}%")
            print(f"   Weight: {item['topic'].weight}")
            print(f"   Days Inactive: {item['days_inactive']}")
            print(f"   Urgency Score: {item['urgency_score']:.1f}")
            print()
    
    def start_study_session(self):
        print("\n--- Start Study Session ---")
        
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("No topics available.")
            return
        
        active = self.study_session.get_active_session()
        if active:
            print(f"\n⚠ You already have an active session (ID: {active.id})")
            print(f"   Started at: {active.start_time.strftime('%H:%M:%S')}")
            return
        
        print("\nAvailable Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name})")
        
        while True:
            try:
                topic_id = int(input("\nSelect topic ID: "))
                if any(t.id == topic_id for t in all_topics):
                    break
                print("Invalid topic ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        session = self.study_session.start_session(topic_id)
        print(f"\n✓ Study session started! (ID: {session.id})")
        print(f"   Start time: {session.start_time.strftime('%H:%M:%S')}")
    
    def end_study_session(self):
        print("\n--- End Study Session ---")
        
        active = self.study_session.get_active_session()
        if not active:
            print("\n⚠ No active study session found.")
            return
        
        topic = self.storage.get_topic(active.topic_id)
        course = self.storage.get_course(topic.course_id)
        
        print(f"\nActive Session:")
        print(f"  Topic: {topic.name} ({course.name})")
        print(f"  Started: {active.start_time.strftime('%H:%M:%S')}")
        
        confirm = input("\nEnd this session? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        session = self.study_session.end_session(active.id)
        print(f"\n✓ Session ended!")
        print(f"   Duration: {session.duration_minutes:.1f} minutes")
    
    def view_study_statistics(self):
        print("\n--- Study Time Statistics ---")
        
        print("\n1. Daily Breakdown (Last 7 days)")
        print("2. Total Time Per Topic")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            breakdown = self.study_session.get_daily_time_breakdown(7)
            if not breakdown:
                print("\nNo study sessions recorded yet.")
                return
            
            print("\n--- Daily Study Time (minutes) ---")
            for date in sorted(breakdown.keys(), reverse=True):
                print(f"\n{date}:")
                for topic_id, minutes in breakdown[date].items():
                    topic = self.storage.get_topic(topic_id)
                    print(f"  {topic.name}: {minutes:.1f} min ({minutes/60:.1f} hrs)")
        
        elif choice == '2':
            totals = self.study_session.get_total_time_per_topic()
            if not totals:
                print("\nNo study sessions recorded yet.")
                return
            
            print("\n--- Total Study Time Per Topic ---")
            sorted_topics = sorted(totals.items(), key=lambda x: x[1], reverse=True)
            for topic_id, minutes in sorted_topics:
                topic = self.storage.get_topic(topic_id)
                course = self.storage.get_course(topic.course_id)
                print(f"{topic.name} ({course.name}): {minutes:.1f} min ({minutes/60:.1f} hrs)")
    
    def manual_self_assessment(self):
        print("\n--- Manual Skill Self-Assessment ---")
        
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
        
        topic = self.storage.get_topic(topic_id)
        print(f"\nCurrent skill level: {topic.skill_level}%")
        
        while True:
            try:
                new_skill = float(input("Your assessed skill level (0-100): "))
                if 0 <= new_skill <= 100:
                    break
                print("Skill level must be between 0 and 100!")
            except ValueError:
                print("Please enter a valid number!")
        
        if abs(new_skill - topic.skill_level) > 20:
            print(f"\n⚠ Large change detected ({abs(new_skill - topic.skill_level):.1f} points)")
            confirm = input("Are you sure? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return
        
        history = self.skill_tracking.record_skill_change(topic_id, new_skill, "self-assessment")
        print(f"\n✓ Skill assessment recorded!")
        print(f"   Previous: {history.previous_skill:.1f}%")
        print(f"   New: {history.new_skill:.1f}%")
        print(f"   (Note: Self-assessments have reduced weight)")
    
    def view_skill_history(self):
        print("\n--- Skill History ---")
        
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("No topics available.")
            return
        
        print("\nAll Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name})")
        
        while True:
            try:
                topic_id = int(input("\nSelect topic ID: "))
                if any(t.id == topic_id for t in all_topics):
                    break
                print("Invalid topic ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        history = self.skill_tracking.get_skill_history(topic_id, limit=10)
        
        if not history:
            print("\nNo skill history recorded for this topic.")
            return
        
        topic = self.storage.get_topic(topic_id)
        print(f"\n--- Skill History: {topic.name} ---")
        print(f"Current Skill: {topic.skill_level}%\n")
        
        for h in history:
            change = h.new_skill - h.previous_skill
            symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
            print(f"{h.timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"  {h.previous_skill:.1f}% {symbol} {h.new_skill:.1f}% ({change:+.1f})")
            print(f"  Reason: {h.reason}")
            print()
    
    def create_quiz(self):
        print("\n--- Create Quiz ---")
        
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("No topics available.")
            return
        
        print("\nAvailable Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name})")
        
        while True:
            try:
                topic_id = int(input("\nSelect topic ID: "))
                if any(t.id == topic_id for t in all_topics):
                    break
                print("Invalid topic ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        title = input("Quiz title: ").strip()
        
        while True:
            try:
                num_questions = int(input("Number of questions (5-10): "))
                if 5 <= num_questions <= 10:
                    break
                print("Must be between 5 and 10 questions!")
            except ValueError:
                print("Please enter a valid number!")
        
        questions = []
        for i in range(num_questions):
            print(f"\n--- Question {i+1} ---")
            q_text = input("Question: ").strip()
            opt_a = input("A) ").strip()
            opt_b = input("B) ").strip()
            opt_c = input("C) ").strip()
            opt_d = input("D) ").strip()
            
            while True:
                correct = input("Correct answer (A/B/C/D): ").strip().upper()
                if correct in ['A', 'B', 'C', 'D']:
                    break
                print("Must be A, B, C, or D!")
            
            questions.append(QuizQuestion(
                question_text=q_text,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_answer=correct
            ))
        
        quiz = Quiz(
            topic_id=topic_id,
            title=title,
            created_at=datetime.now(),
            questions=questions
        )
        
        created_quiz = self.quiz_service.create_quiz(quiz)
        print(f"\n✓ Quiz created successfully! (ID: {created_quiz.id})")
    
    def take_quiz(self):
        print("\n--- Take Quiz ---")
        
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("No topics available.")
            return
        
        print("\nAvailable Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            quizzes = self.quiz_service.get_quizzes_by_topic(topic.id)
            print(f"  {topic.id}. {topic.name} ({course.name}) - {len(quizzes)} quiz(zes)")
        
        while True:
            try:
                topic_id = int(input("\nSelect topic ID: "))
                if any(t.id == topic_id for t in all_topics):
                    break
                print("Invalid topic ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        quizzes = self.quiz_service.get_quizzes_by_topic(topic_id)
        
        if not quizzes:
            print("\nNo quizzes available for this topic. Create one first!")
            return
        
        print("\nAvailable Quizzes:")
        for quiz in quizzes:
            print(f"  {quiz.id}. {quiz.title} ({len(quiz.questions)} questions)")
        
        while True:
            try:
                quiz_id = int(input("\nSelect quiz ID: "))
                if any(q.id == quiz_id for q in quizzes):
                    break
                print("Invalid quiz ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        quiz = self.quiz_service.get_quiz(quiz_id)
        
        print(f"\n{'='*70}")
        print(f"  {quiz.title}")
        print(f"{'='*70}\n")
        
        answers = {}
        for i, question in enumerate(quiz.questions, 1):
            print(f"Question {i}: {question.question_text}")
            print(f"  A) {question.option_a}")
            print(f"  B) {question.option_b}")
            print(f"  C) {question.option_c}")
            print(f"  D) {question.option_d}")
            
            while True:
                answer = input("Your answer (A/B/C/D): ").strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    break
                print("Must be A, B, C, or D!")
            
            answers[question.id] = answer
            print()
        
        attempt = self.quiz_service.submit_quiz_attempt(quiz_id, answers)
        
        print(f"\n{'='*70}")
        print(f"  QUIZ RESULTS")
        print(f"{'='*70}")
        print(f"\nScore: {attempt.score:.1f}%")
        print(f"Correct: {int(attempt.score * attempt.total_questions / 100)}/{attempt.total_questions}")
        
        self.skill_tracking.update_skill_from_quiz(quiz.topic_id, attempt.score)
        print(f"\n✓ Your skill level has been updated based on quiz performance!")
    
    def view_quiz_results(self):
        print("\n--- Quiz Results ---")
        
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("No topics available.")
            return
        
        print("\nTopics with Quizzes:")
        topics_with_quizzes = []
        for topic in all_topics:
            quizzes = self.quiz_service.get_quizzes_by_topic(topic.id)
            if quizzes:
                course = self.storage.get_course(topic.course_id)
                topics_with_quizzes.append(topic)
                print(f"  {topic.id}. {topic.name} ({course.name})")
        
        if not topics_with_quizzes:
            print("\nNo quizzes have been created yet.")
            return
        
        while True:
            try:
                topic_id = int(input("\nSelect topic ID: "))
                if any(t.id == topic_id for t in topics_with_quizzes):
                    break
                print("Invalid topic ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        quizzes = self.quiz_service.get_quizzes_by_topic(topic_id)
        
        print("\nAvailable Quizzes:")
        for quiz in quizzes:
            attempts = self.quiz_service.get_quiz_attempts(quiz.id)
            print(f"  {quiz.id}. {quiz.title} ({len(attempts)} attempt(s))")
        
        while True:
            try:
                quiz_id = int(input("\nSelect quiz ID: "))
                if any(q.id == quiz_id for q in quizzes):
                    break
                print("Invalid quiz ID!")
            except ValueError:
                print("Please enter a valid number!")
        
        attempts = self.quiz_service.get_quiz_attempts(quiz_id)
        
        if not attempts:
            print("\nNo attempts recorded for this quiz.")
            return
        
        print(f"\n--- Quiz Attempt History ---")
        for att in attempts:
            print(f"\n{att.attempted_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Score: {att.score:.1f}%")
            print(f"  Correct: {int(att.score * att.total_questions / 100)}/{att.total_questions}")
    
    def view_progress_charts(self):
        print("\n--- Progress Charts ---")
        print("\n1. Skill Progress Over Time")
        print("2. Daily Study Time Chart")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            all_topics = self.storage.get_all_topics()
            if not all_topics:
                print("No topics available.")
                return
            
            print("\nAvailable Topics:")
            for topic in all_topics:
                course = self.storage.get_course(topic.course_id)
                print(f"  {topic.id}. {topic.name} ({course.name})")
            
            while True:
                try:
                    topic_id = int(input("\nSelect topic ID: "))
                    if any(t.id == topic_id for t in all_topics):
                        break
                    print("Invalid topic ID!")
                except ValueError:
                    print("Please enter a valid number!")
            
            self.progress_viz.print_skill_progress_chart(topic_id, days=14)
        
        elif choice == '2':
            self.progress_viz.print_study_time_chart(days=7)
    
    def view_weakest_topics_summary(self):
        print("\n--- Weakest Topics Summary ---")
        self.progress_viz.print_weakest_topics_table()
    
    def apply_skill_decay(self):
        print("\n--- Apply Skill Decay ---")
        print("\nThis will reduce skill levels for topics that haven't been studied recently.")
        
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        self.skill_tracking.apply_skill_decay()
        print("\n✓ Skill decay applied successfully!")
        print("   Check skill history to see changes.")
    
    def update_skill(self):
        print("\n⚠ This feature has been replaced by:")
        print("   - Option 10: Manual Skill Self-Assessment")
        print("   - Option 13: Take Quiz (auto-updates skill)")
        print("\nPlease use those options instead.")
    
    def run(self):
        print("\n🎓 Welcome to the Skill-Aware Study Planner!")
        
        while True:
            self.display_menu()
            choice = input("Select an option (1-18): ").strip()
            
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
                self.view_weak_topics()
            elif choice == '7':
                self.start_study_session()
            elif choice == '8':
                self.end_study_session()
            elif choice == '9':
                self.view_study_statistics()
            elif choice == '10':
                self.manual_self_assessment()
            elif choice == '11':
                self.view_skill_history()
            elif choice == '12':
                self.create_quiz()
            elif choice == '13':
                self.take_quiz()
            elif choice == '14':
                self.view_quiz_results()
            elif choice == '15':
                self.view_progress_charts()
            elif choice == '16':
                self.view_weakest_topics_summary()
            elif choice == '17':
                self.apply_skill_decay()
            elif choice == '18':
                print("\n👋 Goodbye! Happy studying!")
                sys.exit(0)
            else:
                print("\n✗ Invalid option. Please try again.")


if __name__ == "__main__":
    cli = CLI()
    cli.run()
