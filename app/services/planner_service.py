from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app.storage.storage_service import StorageService
from app.planner.priority_calculator import PriorityCalculator
from app.planner.study_plan_generator import StudyPlanGenerator, StudyPlan
from app.models.models import Course, Topic, TopicPriority
from app.services.dependency_service import DependencyService
from app.services.decision_service import DecisionService
from app.services.optimization_service import OptimizationEngine
from app.services.scenario_service import ScenarioSimulator


class PlannerService:
    def __init__(self, storage_service: StorageService):
        self.storage = storage_service
        self.priority_calculator = PriorityCalculator()
        self.dependency_service = DependencyService(storage_service.db)
        self.decision_service = DecisionService(storage_service.db)
        self.optimization_engine = OptimizationEngine(
            self.dependency_service, 
            self.decision_service
        )
        self.scenario_simulator = ScenarioSimulator(self.optimization_engine)
    
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
        
        priorities = self.optimization_engine.adjust_priorities_for_dependencies(priorities)
        
        if optimize:
            allocated = self.optimization_engine.optimize_time_allocation(
                priorities, available_hours
            )
            
            plan = StudyPlan(daily_hours=available_hours)
            plan.allocated_topics = allocated
            return plan
        else:
            return StudyPlanGenerator.generate_daily_plan(priorities, available_hours)
    
    def get_expected_scores(self) -> Dict:
        """Get expected exam scores for all courses."""
        topics = self.storage.get_all_topics()
        courses = self.storage.get_all_courses()
        return self.optimization_engine.calculate_expected_score(topics, courses)
    
    def identify_risks(self) -> List[Dict]:
        """Identify risk factors across all courses."""
        topics = self.storage.get_all_topics()
        courses = self.storage.get_all_courses()
        return self.optimization_engine.identify_risks(topics, courses)
    
    def suggest_skip_topics(self, available_hours: float) -> List[Dict]:
        """Get suggestions for topics that can be skipped."""
        priorities = self.calculate_adaptive_priorities()
        return self.optimization_engine.suggest_topics_to_skip(priorities, available_hours)
    
    def simulate_scenario(self, scenario_type: str, **kwargs) -> Dict:
        """Run a what-if scenario simulation."""
        topics = self.storage.get_all_topics()
        courses = self.storage.get_all_courses()
        priorities = self.calculate_adaptive_priorities()
        
        if scenario_type == 'hours_change':
            return self.scenario_simulator.simulate_study_hours_change(
                topics, courses, priorities, 
                kwargs['current_hours'], kwargs['new_hours']
            )
        elif scenario_type == 'ignore_low_weight':
            return self.scenario_simulator.simulate_ignore_low_weight(
                topics, courses, priorities,
                kwargs['available_hours'], kwargs.get('weight_threshold', 0.1)
            )
        elif scenario_type == 'exam_date_change':
            return self.scenario_simulator.simulate_exam_date_change(
                topics, courses, priorities,
                kwargs['course_id'], kwargs['days_shift']
            )
        elif scenario_type == 'compare_strategies':
            return self.scenario_simulator.compare_strategies(
                topics, courses, priorities, kwargs['available_hours']
            )
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
    
    def validate_course_topics(self, course_id: int) -> dict:
        """Validate that topic weights sum to approximately 1.0 for a course."""
        topics = self.storage.get_topics_by_course(course_id)
        total_weight = sum(topic.weight for topic in topics)
        
        return {
            'valid': 0.95 <= total_weight <= 1.05,
            'total_weight': total_weight,
            'topic_count': len(topics)
        }
