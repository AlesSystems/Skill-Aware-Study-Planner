from typing import List, Dict, Tuple, Optional
from datetime import datetime
from app.models.models import TopicPriority, Topic, Course
from app.services.dependency_service import DependencyService
from app.services.decision_service import DecisionService


class OptimizationEngine:
    def __init__(self, dependency_service: DependencyService, 
                 decision_service: Optional[DecisionService] = None):
        self.dependency_service = dependency_service
        self.decision_service = decision_service
    
    def adjust_priorities_for_dependencies(self, priorities: List[TopicPriority]) -> List[TopicPriority]:
        """Adjust topic priorities based on dependency constraints."""
        adjusted = []
        
        for priority in priorities:
            topic = priority.topic
            dep_status = self.dependency_service.check_dependencies_satisfied(topic.id)
            
            if not dep_status['all_satisfied']:
                blocking = dep_status['blocking_prerequisites']
                
                for prereq in blocking:
                    skill_gap = prereq['required_skill'] - prereq['current_skill']
                    if skill_gap > 30:
                        priority.priority_score *= 0.3
                        if self.decision_service:
                            self.decision_service.log_decision(
                                'dependency_block',
                                f"Topic '{topic.name}' priority reduced: prerequisite "
                                f"'{prereq['prerequisite_name']}' has skill gap of {skill_gap:.1f}%",
                                topic.id,
                                {'blocking_prerequisites': blocking}
                            )
                        break
                    elif skill_gap > 15:
                        priority.priority_score *= 0.6
                
                for prereq in blocking:
                    prereq_found = False
                    for p in adjusted:
                        if p.topic.id == prereq['prerequisite_id']:
                            p.priority_score *= 1.5
                            prereq_found = True
                            if self.decision_service:
                                self.decision_service.log_decision(
                                    'prerequisite_boost',
                                    f"Prerequisite '{prereq['prerequisite_name']}' boosted "
                                    f"to unlock '{topic.name}'",
                                    p.topic.id,
                                    {'dependent_topic': topic.name}
                                )
                            break
            
            adjusted.append(priority)
        
        adjusted.sort(key=lambda x: x.priority_score, reverse=True)
        return adjusted
    
    def optimize_time_allocation(self, priorities: List[TopicPriority], 
                                 available_hours: float,
                                 exam_proximity_weight: float = 1.0) -> List[Dict]:
        """
        Optimize study time allocation using a greedy algorithm.
        Returns topics with allocated time.
        """
        if available_hours <= 0:
            return []
        
        allocated = []
        remaining_time = available_hours
        
        for priority in priorities:
            if remaining_time <= 0:
                if self.decision_service:
                    self.decision_service.log_decision(
                        'topic_dropped',
                        f"Topic '{priority.topic.name}' dropped: no time remaining",
                        priority.topic.id,
                        {'available_hours': available_hours}
                    )
                continue
            
            skill_gap = 100 - priority.topic.skill_level
            estimated_time = (skill_gap / 100) * priority.topic.weight * 5
            estimated_time = max(0.5, min(estimated_time, 3.0))
            estimated_time *= priority.urgency_factor * exam_proximity_weight
            
            allocated_time = min(estimated_time, remaining_time)
            
            if allocated_time >= 0.25:
                allocated.append({
                    'topic': priority.topic,
                    'course': priority.course,
                    'priority_score': priority.priority_score,
                    'urgency_factor': priority.urgency_factor,
                    'allocated_hours': round(allocated_time, 2)
                })
                remaining_time -= allocated_time
                
                if self.decision_service:
                    self.decision_service.log_decision(
                        'time_allocated',
                        f"Allocated {allocated_time:.1f}h to '{priority.topic.name}': "
                        f"priority={priority.priority_score:.3f}, weight={priority.topic.weight:.2f}",
                        priority.topic.id,
                        {
                            'allocated_hours': allocated_time,
                            'skill_level': priority.topic.skill_level,
                            'weight': priority.topic.weight
                        }
                    )
        
        return allocated
    
    def calculate_expected_score(self, topics: List[Topic], courses: List[Course]) -> Dict:
        """Estimate expected exam score based on current skills and weights."""
        course_scores = {}
        
        for course in courses:
            course_topics = [t for t in topics if t.course_id == course.id]
            
            if not course_topics:
                continue
            
            weighted_sum = sum(t.skill_level * t.weight for t in course_topics)
            total_weight = sum(t.weight for t in course_topics)
            
            if total_weight > 0:
                base_score = (weighted_sum / total_weight)
            else:
                base_score = 0
            
            dependency_penalty = 0
            high_risk_topics = []
            
            for topic in course_topics:
                dep_status = self.dependency_service.check_dependencies_satisfied(topic.id)
                
                if not dep_status['all_satisfied']:
                    penalty = topic.weight * 10
                    dependency_penalty += penalty
                    high_risk_topics.append({
                        'topic': topic.name,
                        'weight': topic.weight,
                        'blocking_prerequisites': len(dep_status['blocking_prerequisites'])
                    })
                
                if topic.skill_level < 50 and topic.weight > 0.15:
                    high_risk_topics.append({
                        'topic': topic.name,
                        'weight': topic.weight,
                        'skill_level': topic.skill_level
                    })
            
            adjusted_score = max(0, base_score - dependency_penalty)
            uncertainty = 5 if total_weight >= 0.95 else 10
            
            course_scores[course.id] = {
                'course_name': course.name,
                'estimated_score': round(adjusted_score, 1),
                'score_range': (
                    round(max(0, adjusted_score - uncertainty), 1),
                    round(min(100, adjusted_score + uncertainty), 1)
                ),
                'dependency_penalty': round(dependency_penalty, 1),
                'high_risk_topics': high_risk_topics,
                'total_weight_coverage': round(total_weight, 2)
            }
        
        return course_scores
    
    def identify_risks(self, topics: List[Topic], courses: List[Course]) -> List[Dict]:
        """Identify risk factors that could threaten exam success."""
        risks = []
        
        for course in courses:
            days_until_exam = (course.exam_date - datetime.now()).days
            course_topics = [t for t in topics if t.course_id == course.id]
            
            if days_until_exam < 7:
                high_weight_weak = [t for t in course_topics 
                                   if t.weight > 0.2 and t.skill_level < 60]
                if high_weight_weak:
                    risks.append({
                        'severity': 'CRITICAL',
                        'type': 'time_pressure',
                        'course': course.name,
                        'description': f"Exam in {days_until_exam} days with "
                                     f"{len(high_weight_weak)} weak high-weight topics",
                        'affected_topics': [t.name for t in high_weight_weak]
                    })
            
            for topic in course_topics:
                dep_status = self.dependency_service.check_dependencies_satisfied(topic.id)
                
                if not dep_status['all_satisfied'] and topic.weight > 0.15:
                    risks.append({
                        'severity': 'HIGH',
                        'type': 'unmet_prerequisite',
                        'course': course.name,
                        'description': f"Important topic '{topic.name}' (weight={topic.weight:.2f}) "
                                     f"has {len(dep_status['blocking_prerequisites'])} unmet prerequisites",
                        'topic': topic.name,
                        'blocking_prerequisites': dep_status['blocking_prerequisites']
                    })
                
                if topic.skill_level < 40 and topic.weight > 0.25:
                    risks.append({
                        'severity': 'HIGH',
                        'type': 'critical_weakness',
                        'course': course.name,
                        'description': f"Critical topic '{topic.name}' has very low skill "
                                     f"({topic.skill_level:.1f}%) but high weight ({topic.weight:.2f})",
                        'topic': topic.name
                    })
        
        risks.sort(key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}[x['severity']])
        return risks
    
    def suggest_topics_to_skip(self, priorities: List[TopicPriority], 
                              available_hours: float) -> List[Dict]:
        """Suggest topics that can be skipped given time constraints."""
        suggestions = []
        
        total_estimated_time = sum(
            max(0.5, (100 - p.topic.skill_level) / 100 * p.topic.weight * 5)
            for p in priorities
        )
        
        if total_estimated_time <= available_hours * 1.2:
            return suggestions
        
        for priority in priorities:
            topic = priority.topic
            
            dependents = self.dependency_service.get_dependents(topic.id)
            has_important_dependents = any(
                d for d in dependents if d.get('required_skill', 70) > 60
            )
            
            if (topic.weight < 0.1 and 
                topic.skill_level > 60 and 
                not has_important_dependents):
                suggestions.append({
                    'topic': topic.name,
                    'reason': 'Low weight + adequate skill level + no critical dependents',
                    'weight': topic.weight,
                    'skill_level': topic.skill_level,
                    'priority_score': priority.priority_score,
                    'time_saved_estimate': 0.5
                })
            
            elif (topic.weight < 0.15 and 
                  topic.skill_level < 30 and 
                  available_hours < 10):
                suggestions.append({
                    'topic': topic.name,
                    'reason': 'Low weight + very low skill (high time cost) + limited time',
                    'weight': topic.weight,
                    'skill_level': topic.skill_level,
                    'priority_score': priority.priority_score,
                    'time_saved_estimate': 2.0
                })
        
        return suggestions
