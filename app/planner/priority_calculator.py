from datetime import datetime
from typing import List
from app.models.models import Course, Topic, TopicPriority


class PriorityCalculator:
    @staticmethod
    def calculate_urgency(exam_date: datetime) -> float:
        """
        Calculate urgency factor based on days until exam.
        
        Rules:
        - >30 days: Low urgency (1.0x)
        - 7-30 days: Medium urgency (2.0x)
        - <7 days: High urgency (3.0x)
        """
        days_until_exam = (exam_date - datetime.now()).days
        
        if days_until_exam > 30:
            return 1.0
        elif days_until_exam >= 7:
            return 2.0
        else:
            return 3.0
    
    @staticmethod
    def calculate_priority(topic: Topic, course: Course) -> TopicPriority:
        """
        Calculate priority score for a topic.
        
        Formula: priority = topic_weight × (1 - skill_level / 100) × urgency
        """
        urgency = PriorityCalculator.calculate_urgency(course.exam_date)
        skill_gap = 1 - (topic.skill_level / 100)
        priority_score = topic.weight * skill_gap * urgency
        
        return TopicPriority(
            topic=topic,
            course=course,
            priority_score=priority_score,
            urgency_factor=urgency
        )
    
    @staticmethod
    def sort_by_priority(priorities: List[TopicPriority]) -> List[TopicPriority]:
        """Sort topics by priority score in descending order."""
        return sorted(priorities, key=lambda x: x.priority_score, reverse=True)
