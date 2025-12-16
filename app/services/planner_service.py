from typing import List
from datetime import datetime
from app.storage.storage_service import StorageService
from app.planner.priority_calculator import PriorityCalculator
from app.planner.study_plan_generator import StudyPlanGenerator, StudyPlan
from app.models.models import Course, Topic, TopicPriority


class PlannerService:
    def __init__(self, storage_service: StorageService):
        self.storage = storage_service
        self.priority_calculator = PriorityCalculator()
    
    def calculate_all_priorities(self) -> List[TopicPriority]:
        """Calculate priorities for all topics across all courses."""
        priorities = []
        courses = self.storage.get_all_courses()
        
        for course in courses:
            topics = self.storage.get_topics_by_course(course.id)
            for topic in topics:
                priority = self.priority_calculator.calculate_priority(topic, course)
                priorities.append(priority)
        
        return self.priority_calculator.sort_by_priority(priorities)
    
    def generate_daily_plan(self, available_hours: float, optimize: bool = True) -> StudyPlan:
        """Generate a daily study plan based on current priorities."""
        priorities = self.calculate_all_priorities()
        
        if optimize:
            return StudyPlanGenerator.optimize_plan(priorities, available_hours)
        else:
            return StudyPlanGenerator.generate_daily_plan(priorities, available_hours)
    
    def validate_course_topics(self, course_id: int) -> dict:
        """Validate that topic weights sum to approximately 1.0 for a course."""
        topics = self.storage.get_topics_by_course(course_id)
        total_weight = sum(topic.weight for topic in topics)
        
        return {
            'valid': 0.95 <= total_weight <= 1.05,
            'total_weight': total_weight,
            'topic_count': len(topics)
        }
