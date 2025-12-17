from typing import List, Dict, Tuple
from datetime import datetime, timedelta
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
    
    def calculate_adaptive_priorities(self) -> List[TopicPriority]:
        """Calculate adaptive priorities considering skill trends and study time."""
        from app.storage.database import SkillHistoryDB, StudySessionDB
        
        priorities = []
        courses = self.storage.get_all_courses()
        db = self.storage.db
        session = db.get_session()
        
        try:
            for course in courses:
                topics = self.storage.get_topics_by_course(course.id)
                for topic in topics:
                    skill_trend = self._get_skill_trend(session, topic.id)
                    time_spent = self._get_recent_study_time(session, topic.id)
                    
                    base_priority = self.priority_calculator.calculate_priority(topic, course)
                    
                    if skill_trend < -5:
                        base_priority.priority_score *= 1.3
                    elif skill_trend < 0:
                        base_priority.priority_score *= 1.1
                    elif skill_trend > 10:
                        base_priority.priority_score *= 0.8
                    
                    if time_spent > 300:
                        base_priority.priority_score *= 0.9
                    elif time_spent < 60:
                        base_priority.priority_score *= 1.2
                    
                    priorities.append(base_priority)
            
            return self.priority_calculator.sort_by_priority(priorities)
        finally:
            session.close()
    
    def _get_skill_trend(self, session, topic_id: int) -> float:
        from app.storage.database import SkillHistoryDB
        
        history = session.query(SkillHistoryDB).filter(
            SkillHistoryDB.topic_id == topic_id
        ).order_by(SkillHistoryDB.timestamp.desc()).limit(5).all()
        
        if len(history) < 2:
            return 0
        
        trend = history[0].new_skill - history[-1].previous_skill
        return trend
    
    def _get_recent_study_time(self, session, topic_id: int, days: int = 7) -> float:
        from app.storage.database import StudySessionDB
        
        cutoff = datetime.now() - timedelta(days=days)
        sessions = session.query(StudySessionDB).filter(
            StudySessionDB.topic_id == topic_id,
            StudySessionDB.start_time >= cutoff,
            StudySessionDB.end_time.isnot(None)
        ).all()
        
        return sum(s.duration_minutes for s in sessions)
    
    def detect_weak_topics(self) -> List[Dict]:
        """Identify weakest topics based on skill level, weight, and inactivity."""
        from app.storage.database import StudySessionDB
        
        weak_topics = []
        courses = self.storage.get_all_courses()
        db = self.storage.db
        session = db.get_session()
        
        try:
            for course in courses:
                topics = self.storage.get_topics_by_course(course.id)
                
                for topic in topics:
                    last_session = session.query(StudySessionDB).filter(
                        StudySessionDB.topic_id == topic.id,
                        StudySessionDB.end_time.isnot(None)
                    ).order_by(StudySessionDB.end_time.desc()).first()
                    
                    days_inactive = 0
                    if last_session:
                        days_inactive = (datetime.now() - last_session.end_time).days
                    else:
                        days_inactive = 999
                    
                    urgency_score = (
                        (100 - topic.skill_level) * topic.weight * 2 +
                        min(days_inactive, 30) * 0.5
                    )
                    
                    if urgency_score > 30:
                        weak_topics.append({
                            'topic': topic,
                            'course': course,
                            'urgency_score': urgency_score,
                            'days_inactive': days_inactive
                        })
            
            weak_topics.sort(key=lambda x: x['urgency_score'], reverse=True)
            return weak_topics
        finally:
            session.close()
    
    def generate_daily_plan(self, available_hours: float, optimize: bool = True, adaptive: bool = True) -> StudyPlan:
        """Generate a daily study plan based on current priorities."""
        if adaptive:
            priorities = self.calculate_adaptive_priorities()
        else:
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
