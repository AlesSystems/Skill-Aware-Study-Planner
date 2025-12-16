from typing import List, Dict
from app.models.models import TopicPriority


class StudyPlan:
    def __init__(self, daily_hours: float):
        self.daily_hours = daily_hours
        self.allocated_topics: List[Dict] = []
    
    def add_topic(self, topic_priority: TopicPriority, hours: float):
        self.allocated_topics.append({
            'topic': topic_priority.topic,
            'course': topic_priority.course,
            'priority_score': topic_priority.priority_score,
            'urgency_factor': topic_priority.urgency_factor,
            'allocated_hours': hours
        })
    
    def get_total_allocated_hours(self) -> float:
        return sum(item['allocated_hours'] for item in self.allocated_topics)


class StudyPlanGenerator:
    @staticmethod
    def generate_daily_plan(priorities: List[TopicPriority], available_hours: float) -> StudyPlan:
        """
        Generate a daily study plan based on priorities and available time.
        
        Strategy:
        - Allocate time proportionally to priority scores
        - Ensure total time doesn't exceed available hours
        - Minimum allocation is 0.5 hours per topic
        """
        plan = StudyPlan(available_hours)
        
        if not priorities or available_hours <= 0:
            return plan
        
        total_priority = sum(p.priority_score for p in priorities)
        
        if total_priority == 0:
            return plan
        
        min_hours_per_topic = 0.5
        remaining_hours = available_hours
        allocated_topics = []
        
        for priority in priorities:
            if remaining_hours < min_hours_per_topic:
                break
            
            proportion = priority.priority_score / total_priority
            allocated_time = max(min_hours_per_topic, proportion * available_hours)
            
            if allocated_time > remaining_hours:
                allocated_time = remaining_hours
            
            plan.add_topic(priority, allocated_time)
            remaining_hours -= allocated_time
            
            if remaining_hours <= 0:
                break
        
        return plan
    
    @staticmethod
    def optimize_plan(priorities: List[TopicPriority], available_hours: float) -> StudyPlan:
        """
        Generate an optimized study plan with better distribution.
        
        Takes top priority topics and distributes time more intelligently.
        """
        plan = StudyPlan(available_hours)
        
        if not priorities or available_hours <= 0:
            return plan
        
        total_priority = sum(p.priority_score for p in priorities)
        
        if total_priority == 0:
            return plan
        
        for priority in priorities:
            proportion = priority.priority_score / total_priority
            allocated_time = proportion * available_hours
            
            if allocated_time >= 0.25:
                plan.add_topic(priority, round(allocated_time, 2))
        
        return plan
