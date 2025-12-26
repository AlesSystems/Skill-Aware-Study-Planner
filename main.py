import sys
from datetime import datetime
from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService
from app.services.quiz_service import QuizService
from app.services.skill_tracking_service import SkillTrackingService
from app.services.study_session_service import StudySessionService
from app.services.progress_service import ProgressVisualizationService
from app.services.honesty_service import HonestyService
from app.services.exam_simulation_service import ExamSimulationService
from app.services.reprioritization_service import ForcedReprioritizationEngine, ConsequenceEngine
from app.models.models import Course, Topic, Quiz, QuizQuestion


class CLI:
    def __init__(self):
        self.storage = StorageService()
        self.planner = PlannerService(self.storage)
        self.quiz_service = QuizService(self.storage.db)
        self.skill_tracking = SkillTrackingService(self.storage.db)
        self.study_session = StudySessionService(self.storage.db)
        self.progress_viz = ProgressVisualizationService(self.storage)
        # Phase 4: Honesty & Reality Check System
        self.honesty_service = HonestyService(self.storage.db)
        self.exam_sim_service = ExamSimulationService(self.storage.db)
        self.reprioritization = ForcedReprioritizationEngine(self.storage.db)
        self.consequence_engine = ConsequenceEngine(self.storage.db)
    
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
        print("\n--- Intelligence & Decision Layer (Phase 3) ---")
        print("17. Manage Topic Dependencies")
        print("18. View Expected Exam Scores")
        print("19. Risk Analysis")
        print("20. What-If Scenario Simulator")
        print("21. Compare Study Strategies")
        print("22. Get Skip Topic Suggestions")
        print("23. View Decision Log")
        print("\n--- Honesty & Reality Check (Phase 4) ---")
        print("26. Simulate Exam Today")
        print("27. Motivation vs Reality Dashboard")
        print("28. Detect Fake Productivity")
        print("29. Check Avoidance Patterns")
        print("30. Detect Overconfidence")
        print("31. View All Honesty Warnings")
        print("32. Toggle Brutal Honesty Mode")
        print("33. Check Forced Re-Prioritization")
        print("\n--- System ---")
        print("24. Apply Skill Decay")
        print("25. Exit")
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
    
    def manage_dependencies(self):
        print("\n--- Manage Topic Dependencies ---")
        print("\n1. Add Dependency")
        print("2. View Dependencies for Topic")
        print("3. View Dependency Graph")
        print("4. Get Learning Path to Topic")
        print("5. Remove Dependency")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._add_dependency()
        elif choice == '2':
            self._view_dependencies()
        elif choice == '3':
            self._view_dependency_graph()
        elif choice == '4':
            self._get_learning_path()
        elif choice == '5':
            self._remove_dependency()
    
    def _add_dependency(self):
        all_topics = self.storage.get_all_topics()
        if len(all_topics) < 2:
            print("\nNeed at least 2 topics to create dependencies.")
            return
        
        print("\nAvailable Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name})")
        
        try:
            prereq_id = int(input("\nPrerequisite topic ID: "))
            dependent_id = int(input("Dependent topic ID (requires prerequisite): "))
            threshold = float(input("Minimum skill threshold (default 70): ") or "70")
            
            self.planner.dependency_service.add_dependency(
                prereq_id, dependent_id, threshold
            )
            
            prereq = self.storage.get_topic(prereq_id)
            dependent = self.storage.get_topic(dependent_id)
            print(f"\n✓ Dependency added: '{prereq.name}' → '{dependent.name}' (threshold: {threshold}%)")
        except ValueError as e:
            print(f"\n✗ Error: {e}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def _view_dependencies(self):
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("\nNo topics available.")
            return
        
        print("\nAvailable Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name})")
        
        try:
            topic_id = int(input("\nSelect topic ID: "))
            topic = self.storage.get_topic(topic_id)
            
            print(f"\n--- Dependencies for '{topic.name}' ---\n")
            
            prereqs = self.planner.dependency_service.get_prerequisites(topic_id)
            if prereqs:
                print("Prerequisites:")
                for p in prereqs:
                    status = "✓" if p['is_satisfied'] else "✗"
                    print(f"  {status} {p['prerequisite_name']}: {p['current_skill']:.1f}% / {p['required_skill']:.1f}%")
            else:
                print("No prerequisites")
            
            print()
            dependents = self.planner.dependency_service.get_dependents(topic_id)
            if dependents:
                print("Unlocks:")
                for d in dependents:
                    print(f"  → {d['dependent_name']} (requires {d['required_skill']:.1f}%)")
            else:
                print("No dependent topics")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def _view_dependency_graph(self):
        graph = self.planner.dependency_service.get_dependency_graph()
        
        print("\n--- Dependency Graph ---\n")
        print(f"Total Topics: {len(graph['nodes'])}")
        print(f"Total Dependencies: {len(graph['edges'])}\n")
        
        if graph['edges']:
            print("Dependencies:")
            for edge in graph['edges']:
                from_node = next(n for n in graph['nodes'] if n['id'] == edge['from'])
                to_node = next(n for n in graph['nodes'] if n['id'] == edge['to'])
                print(f"  {from_node['name']} → {to_node['name']} (threshold: {edge['threshold']}%)")
        else:
            print("No dependencies defined yet.")
    
    def _get_learning_path(self):
        all_topics = self.storage.get_all_topics()
        if not all_topics:
            print("\nNo topics available.")
            return
        
        print("\nAvailable Topics:")
        for topic in all_topics:
            course = self.storage.get_course(topic.course_id)
            print(f"  {topic.id}. {topic.name} ({course.name})")
        
        try:
            topic_id = int(input("\nTarget topic ID: "))
            path = self.planner.dependency_service.get_learning_path(topic_id)
            
            print("\n--- Recommended Learning Path ---\n")
            for i, tid in enumerate(path, 1):
                t = self.storage.get_topic(tid)
                print(f"{i}. {t.name} (skill: {t.skill_level:.1f}%)")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def _remove_dependency(self):
        graph = self.planner.dependency_service.get_dependency_graph()
        
        if not graph['edges']:
            print("\nNo dependencies to remove.")
            return
        
        print("\nExisting Dependencies:")
        for i, edge in enumerate(graph['edges'], 1):
            from_node = next(n for n in graph['nodes'] if n['id'] == edge['from'])
            to_node = next(n for n in graph['nodes'] if n['id'] == edge['to'])
            print(f"  {i}. {from_node['name']} → {to_node['name']}")
        
        try:
            choice = int(input("\nSelect dependency number to remove: "))
            if 1 <= choice <= len(graph['edges']):
                edge = graph['edges'][choice - 1]
                
                session = self.storage.db.get_session()
                from app.storage.database import TopicDependencyDB
                dep = session.query(TopicDependencyDB).filter(
                    TopicDependencyDB.prerequisite_topic_id == edge['from'],
                    TopicDependencyDB.dependent_topic_id == edge['to']
                ).first()
                
                if dep:
                    self.planner.dependency_service.remove_dependency(dep.id)
                    print("\n✓ Dependency removed.")
                session.close()
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def view_expected_scores(self):
        print("\n--- Expected Exam Scores ---\n")
        scores = self.planner.get_expected_scores()
        
        if not scores:
            print("No courses with topics found.")
            return
        
        for course_id, data in scores.items():
            print(f"Course: {data['course_name']}")
            print(f"  Expected Score: {data['estimated_score']:.1f}%")
            print(f"  Score Range: {data['score_range'][0]:.1f}% - {data['score_range'][1]:.1f}%")
            print(f"  Weight Coverage: {data['total_weight_coverage']:.2f}")
            
            if data['dependency_penalty'] > 0:
                print(f"  ⚠ Dependency Penalty: -{data['dependency_penalty']:.1f}%")
            
            if data['high_risk_topics']:
                print(f"  🔴 High-Risk Topics ({len(data['high_risk_topics'])}):")
                for risk in data['high_risk_topics'][:3]:
                    print(f"     - {risk['topic']} (weight: {risk['weight']:.2f})")
            print()
    
    def view_risk_analysis(self):
        print("\n--- Risk Analysis ---\n")
        risks = self.planner.identify_risks()
        
        if not risks:
            print("✓ No significant risks detected. Keep up the good work!")
            return
        
        print(f"Found {len(risks)} risk factors:\n")
        
        for i, risk in enumerate(risks[:10], 1):
            severity_color = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            
            print(f"{i}. {severity_color.get(risk['severity'], '⚪')} [{risk['severity']}] {risk['type'].upper()}")
            print(f"   Course: {risk['course']}")
            print(f"   {risk['description']}")
            print()
    
    def simulate_scenario(self):
        print("\n--- What-If Scenario Simulator ---")
        print("\n1. Change Daily Study Hours")
        print("2. Ignore Low-Weight Topics")
        print("3. Move Exam Date")
        
        choice = input("\nSelect scenario: ").strip()
        
        try:
            if choice == '1':
                current = float(input("Current daily hours: "))
                new = float(input("Simulated daily hours: "))
                result = self.planner.simulate_scenario(
                    'hours_change', 
                    current_hours=current, 
                    new_hours=new
                )
                self._display_scenario_result(result)
            
            elif choice == '2':
                hours = float(input("Available hours: "))
                threshold = float(input("Weight threshold (default 0.1): ") or "0.1")
                result = self.planner.simulate_scenario(
                    'ignore_low_weight',
                    available_hours=hours,
                    weight_threshold=threshold
                )
                self._display_scenario_result(result)
            
            elif choice == '3':
                courses = self.storage.get_all_courses()
                print("\nCourses:")
                for c in courses:
                    print(f"  {c.id}. {c.name}")
                
                course_id = int(input("\nSelect course ID: "))
                days = int(input("Days to shift (negative = earlier, positive = later): "))
                result = self.planner.simulate_scenario(
                    'exam_date_change',
                    course_id=course_id,
                    days_shift=days
                )
                self._display_scenario_result(result)
        
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def _display_scenario_result(self, result):
        print(f"\n--- Simulation Results: {result['scenario']} ---\n")
        
        for key, value in result.items():
            if key == 'scenario':
                continue
            elif isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            elif isinstance(value, list):
                print(f"{key}: {len(value)} items")
            else:
                print(f"{key}: {value}")
        print()
    
    def compare_strategies(self):
        print("\n--- Compare Study Strategies ---\n")
        
        try:
            hours = float(input("Available daily hours: "))
            result = self.planner.simulate_scenario('compare_strategies', available_hours=hours)
            
            print("\n--- Strategy Comparison ---\n")
            
            for strategy_id, strategy in result['strategies'].items():
                print(f"{strategy['name']}:")
                print(f"  {strategy['description']}")
                print(f"  Topics Covered: {strategy['topics_covered']}")
                
                total_score = sum(
                    s['estimated_score'] 
                    for s in strategy['expected_scores'].values()
                )
                print(f"  Total Expected Score: {total_score:.1f}")
                print()
            
            print(f"🏆 Best Strategy: {result['best_strategy_name']}")
            print(f"   Reason: {result['reason']}")
        
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def view_skip_suggestions(self):
        print("\n--- Skip Topic Suggestions ---\n")
        
        try:
            hours = float(input("Available daily hours: "))
            suggestions = self.planner.suggest_skip_topics(hours)
            
            if not suggestions:
                print("✓ No topics recommended to skip. You have adequate time!")
                return
            
            print(f"Found {len(suggestions)} topics you might consider skipping:\n")
            
            for i, s in enumerate(suggestions, 1):
                print(f"{i}. {s['topic']}")
                print(f"   Reason: {s['reason']}")
                print(f"   Weight: {s['weight']:.2f}, Skill: {s['skill_level']:.1f}%")
                print(f"   Est. Time Saved: {s['time_saved_estimate']:.1f}h")
                print()
        
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def view_decision_log(self):
        print("\n--- Decision Log ---\n")
        decisions = self.planner.decision_service.get_recent_decisions(limit=15)
        
        if not decisions:
            print("No decisions logged yet.")
            return
        
        for d in decisions:
            print(f"[{d['timestamp'].strftime('%Y-%m-%d %H:%M')}] {d['decision_type'].upper()}")
            print(f"  {d['explanation']}")
            print()
    
    def update_skill(self):
        print("\n⚠ This feature has been replaced by:")
        print("   - Option 10: Manual Skill Self-Assessment")
        print("   - Option 13: Take Quiz (auto-updates skill)")
        print("\nPlease use those options instead.")
    
    # ===== PHASE 4: HONESTY & REALITY CHECK METHODS =====
    
    def simulate_exam_today(self):
        """TICKET-406: Simulate exam outcome if exam were today"""
        print("\n--- Exam Day Simulation ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses available.")
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  {course.id}. {course.name}")
        
        try:
            course_id = int(input("\nSelect course ID: "))
        except ValueError:
            print("Invalid course ID!")
            return
        
        simulation = self.exam_sim_service.simulate_exam_today(course_id)
        
        if 'error' in simulation:
            print(f"\n✗ Error: {simulation['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"  EXAM SIMULATION: {simulation['course_name']}")
        print(f"{'='*60}")
        print(f"\n📅 Exam Date: {simulation['exam_date']}")
        print(f"⏰ Days Remaining: {simulation['days_remaining']}")
        print(f"\n📊 ESTIMATED SCORE: {simulation['estimated_score']:.1f}%")
        print(f"🎯 Passing Threshold: {simulation['passing_threshold']:.1f}%")
        print(f"📈 Pass Probability: {simulation['pass_probability']}%")
        
        if simulation['will_pass']:
            print(f"\n✅ PROJECTION: PASS")
        else:
            print(f"\n🚨 PROJECTION: FAIL")
        
        print(f"\n⚠️  Risk Level: {simulation['risk_level']}")
        
        if simulation['weakest_topics']:
            print(f"\n🔴 Weakest Topics (Immediate Attention Needed):")
            for i, topic in enumerate(simulation['weakest_topics'], 1):
                print(f"  {i}. {topic['name']}: {topic['score']:.1f}% (Weight: {topic['weight']*100:.0f}%, Impact: {topic['impact']:.1f})")
        
        if simulation['critical_gaps']:
            print(f"\n🚨 Critical Gaps (High Weight, Low Score):")
            for gap in simulation['critical_gaps']:
                print(f"  • {gap['name']}: {gap['score']:.1f}% (Need {gap['gap']:.1f}% improvement)")
    
    def show_reality_dashboard(self):
        """TICKET-407: Motivation vs Reality Dashboard"""
        print("\n--- Motivation vs Reality Dashboard ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses available.")
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  {course.id}. {course.name}")
        
        try:
            course_id = int(input("\nSelect course ID: "))
            days = int(input("Analyze last N days (default 30): ") or "30")
        except ValueError:
            print("Invalid input!")
            return
        
        dashboard = self.exam_sim_service.get_motivation_vs_reality_dashboard(course_id, days)
        
        if 'error' in dashboard:
            print(f"\n✗ Error: {dashboard['error']}")
            return
        
        print(f"\n{'='*70}")
        print(f"  REALITY CHECK: {dashboard['course_name']}")
        print(f"{'='*70}")
        print(f"\n📊 Analysis Period: Last {dashboard['days_analyzed']} days")
        print(f"⏱️  Total Time Invested: {dashboard['total_time_hours']:.1f} hours")
        print(f"📈 Total Skill Gained: {dashboard['total_skill_gain']:.1f}%")
        print(f"⚡ Average Efficiency: {dashboard['average_efficiency']:.2f} skill points per hour")
        
        print(f"\n{dashboard['summary']}")
        
        print(f"\n{'─'*70}")
        print(f"{'Topic':<30} {'Time':<10} {'Gain':<8} {'Quiz':<8} {'Gap':<8} {'Trend':<15}")
        print(f"{'─'*70}")
        
        for topic in dashboard['topics'][:10]:
            quiz_str = f"{topic['avg_quiz_score']:.0f}%" if topic['avg_quiz_score'] else "N/A"
            gap_str = f"{topic['reality_gap']:+.0f}%" if topic['reality_gap'] else "N/A"
            print(f"{topic['topic_name']:<30} {topic['time_spent_hours']:>6.1f}h  {topic['skill_gain']:>6.1f}% {quiz_str:>7} {gap_str:>7} {topic['trend']:<15}")
            print(f"  → {topic['honest_assessment']}")
    
    def detect_fake_productivity_ui(self):
        """TICKET-401: Fake Productivity Detection UI"""
        print("\n--- Fake Productivity Detection ---")
        
        try:
            topic_id = int(input("Enter topic ID to analyze: "))
            days = int(input("Analyze last N days (default 14): ") or "14")
        except ValueError:
            print("Invalid input!")
            return
        
        result = self.honesty_service.detect_fake_productivity(topic_id, days)
        
        print(f"\n{'='*60}")
        print(f"  FAKE PRODUCTIVITY ANALYSIS")
        print(f"{'='*60}")
        print(f"\n📊 Analysis Period: {result['days_analyzed']} days")
        print(f"⏱️  Total Study Time: {result['total_study_time']:.0f} minutes")
        print(f"📈 Net Skill Change: {result['net_skill_change']:+.1f}%")
        print(f"📝 Quiz Attempts: {result['quiz_attempts']}")
        print(f"📊 Quiz Improvement: {result['quiz_improvement']:+.1f}%")
        
        print(f"\n🎯 Fake Productivity Score: {result['fake_productivity_score']:.0f}/100")
        
        if result['suspicious']:
            print(f"\n🚨 STATUS: SUSPICIOUS - Fake Productivity Detected!")
            print(f"\n⚠️  Issues Found:")
            for reason in result['reasons']:
                print(f"  • {reason}")
            
            print(f"\n💡 Recommendations:")
            print(f"  1. Change your study method - current approach isn't working")
            print(f"  2. Take a quiz to verify actual understanding")
            print(f"  3. Focus on active learning instead of passive reading")
        else:
            print(f"\n✅ STATUS: Legitimate productivity detected")
    
    def check_avoidance_patterns_ui(self):
        """TICKET-402: Avoidance Pattern Detection UI"""
        print("\n--- Avoidance Pattern Detection ---")
        
        try:
            topic_id = int(input("Enter topic ID to analyze: "))
            days = int(input("Analyze last N days (default 21): ") or "21")
        except ValueError:
            print("Invalid input!")
            return
        
        result = self.honesty_service.detect_avoidance_patterns(topic_id, days)
        
        if 'error' in result:
            print(f"\n✗ Error: {result['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"  AVOIDANCE ANALYSIS: {result['topic_name']}")
        print(f"{'='*60}")
        print(f"\n📊 Topic Weight: {result['weight']*100:.0f}% (importance in course)")
        print(f"📈 Current Skill: {result['skill_level']:.0f}%")
        print(f"🎯 Skill Gap: {result['skill_gap']:.0f}% (room for improvement)")
        print(f"⏱️  Study Time: {result['study_time_minutes']:.0f} minutes")
        print(f"📊 Expected Proportion: {result['expected_proportion']*100:.1f}%")
        print(f"📊 Actual Proportion: {result['actual_proportion']*100:.1f}%")
        
        print(f"\n🎯 Avoidance Severity: {result['avoidance_severity']:.0f}/100")
        
        if result['avoided']:
            print(f"\n🚨 STATUS: AVOIDANCE DETECTED!")
            print(f"\n⚠️  Patterns Found:")
            for reason in result['reasons']:
                print(f"  • {reason}")
            
            print(f"\n💡 Action Required:")
            print(f"  1. This topic needs immediate attention")
            print(f"  2. Allocate more study time proportional to its weight")
            print(f"  3. Take a quiz to break the avoidance pattern")
        else:
            print(f"\n✅ STATUS: No significant avoidance detected")
    
    def detect_overconfidence_ui(self):
        """TICKET-403: Overconfidence Detection UI"""
        print("\n--- Overconfidence Detection ---")
        
        try:
            topic_id = int(input("Enter topic ID to analyze: "))
        except ValueError:
            print("Invalid input!")
            return
        
        result = self.honesty_service.detect_overconfidence(topic_id)
        
        if 'error' in result:
            print(f"\n✗ Error: {result['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"  OVERCONFIDENCE ANALYSIS: {result['topic_name']}")
        print(f"{'='*60}")
        print(f"\n📊 Self-Assessed Skill: {result['current_skill']:.0f}%")
        
        if result['avg_quiz_score'] is not None:
            print(f"📝 Average Quiz Score: {result['avg_quiz_score']:.0f}%")
            gap = result['current_skill'] - result['avg_quiz_score']
            print(f"⚠️  Reality Gap: {gap:+.0f}%")
        else:
            print(f"📝 Quiz Attempts: {result['quiz_count']} (No data)")
        
        print(f"\n🎯 Overconfidence Score: {result['overconfidence_score']:.0f}/100")
        
        if result['overconfident']:
            print(f"\n🚨 STATUS: OVERCONFIDENCE DETECTED!")
            print(f"\n⚠️  Issues Found:")
            for reason in result['reasons']:
                print(f"  • {reason}")
            
            print(f"\n💡 Reality Check:")
            print(f"  1. Your self-assessment doesn't match objective performance")
            print(f"  2. Take quizzes regularly to verify actual understanding")
            print(f"  3. Be honest about what you don't know")
        else:
            print(f"\n✅ STATUS: Realistic self-assessment")
    
    def view_all_honesty_warnings(self):
        """View all honesty warnings for a course"""
        print("\n--- All Honesty Warnings ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses available.")
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  {course.id}. {course.name}")
        
        try:
            course_id = int(input("\nSelect course ID (or 0 for all): "))
            if course_id == 0:
                course_id = None
        except ValueError:
            print("Invalid input!")
            return
        
        warnings = self.honesty_service.get_honesty_warnings(course_id)
        
        if not warnings:
            print("\n✅ No honesty warnings - all clear!")
            return
        
        print(f"\n{'='*70}")
        print(f"  HONESTY WARNINGS")
        print(f"{'='*70}\n")
        
        for warning in warnings:
            print(warning)
            print()
    
    def toggle_brutal_honesty(self):
        """TICKET-404: Toggle brutal honesty mode"""
        current = self.honesty_service.toggle_brutal_honesty_mode()
        
        if current:
            print("\n🚨 BRUTAL HONESTY MODE: ACTIVATED")
            print("All feedback will be direct and unfiltered.")
            print("Sugar-coating removed. Reality enforced.")
        else:
            print("\n✓ Brutal Honesty Mode: Deactivated")
            print("Feedback will be constructive and polite.")
    
    def check_forced_reprioritization_ui(self):
        """TICKET-405: Check forced re-prioritization status"""
        print("\n--- Forced Re-Prioritization Check ---")
        courses = self.storage.get_all_courses()
        
        if not courses:
            print("No courses available.")
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  {course.id}. {course.name}")
        
        try:
            course_id = int(input("\nSelect course ID: "))
        except ValueError:
            print("Invalid input!")
            return
        
        check = self.reprioritization.check_forced_reprioritization(course_id)
        
        if 'error' in check:
            print(f"\n✗ Error: {check['error']}")
            return
        
        print(f"\n{'='*70}")
        print(f"  FORCED RE-PRIORITIZATION STATUS")
        print(f"{'='*70}")
        print(f"\n⏰ Days Until Exam: {check['days_until_exam']}")
        print(f"⚠️  Risk Level: {check['risk_level']}")
        print(f"🔒 Forced Override: {'YES' if check['forced_reprioritization'] else 'NO'}")
        print(f"🎛️  Can Ignore: {'YES' if check['can_ignore'] else 'NO'}")
        
        if check['forced_reprioritization']:
            print(f"\n{check['explanation']}")
            
            # Show active consequences
            consequences = self.consequence_engine.get_active_consequences(course_id)
            if consequences:
                print(f"\n{'='*70}")
                print(f"  ACTIVE CONSEQUENCES")
                print(f"{'='*70}\n")
                for consequence in consequences:
                    print(consequence)
        else:
            print(f"\n✅ No forced re-prioritization needed.")
            print(f"You have full control over your study plan.")
    
    def run(self):
        print("\n🎓 Welcome to the Skill-Aware Study Planner!")
        
        while True:
            self.display_menu()
            choice = input("Select an option (1-33): ").strip()
            
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
                self.manage_dependencies()
            elif choice == '18':
                self.view_expected_scores()
            elif choice == '19':
                self.view_risk_analysis()
            elif choice == '20':
                self.simulate_scenario()
            elif choice == '21':
                self.compare_strategies()
            elif choice == '22':
                self.view_skip_suggestions()
            elif choice == '23':
                self.view_decision_log()
            elif choice == '24':
                self.apply_skill_decay()
            elif choice == '25':
                print("\n👋 Goodbye! Happy studying!")
                sys.exit(0)
            elif choice == '26':
                self.simulate_exam_today()
            elif choice == '27':
                self.show_reality_dashboard()
            elif choice == '28':
                self.detect_fake_productivity_ui()
            elif choice == '29':
                self.check_avoidance_patterns_ui()
            elif choice == '30':
                self.detect_overconfidence_ui()
            elif choice == '31':
                self.view_all_honesty_warnings()
            elif choice == '32':
                self.toggle_brutal_honesty()
            elif choice == '33':
                self.check_forced_reprioritization_ui()
            else:
                print("\n✗ Invalid option. Please try again.")


if __name__ == "__main__":
    cli = CLI()
    cli.run()
