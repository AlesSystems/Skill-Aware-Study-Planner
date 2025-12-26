from typing import List, Dict, Optional
from datetime import datetime, timedelta
from copy import deepcopy
from app.models.models import Topic, Course, TopicPriority
from app.services.optimization_service import OptimizationEngine


class ScenarioSimulator:
    def __init__(self, optimization_engine: OptimizationEngine):
        self.optimization_engine = optimization_engine
    
    def simulate_study_hours_change(self, 
                                    current_topics: List[Topic],
                                    current_courses: List[Course],
                                    priorities: List[TopicPriority],
                                    current_hours: float,
                                    new_hours: float) -> Dict:
        """Simulate what happens if daily study hours change."""
        current_allocation = self.optimization_engine.optimize_time_allocation(
            priorities, current_hours
        )
        
        new_allocation = self.optimization_engine.optimize_time_allocation(
            priorities, new_hours
        )
        
        current_topics_covered = {item['topic'].id for item in current_allocation}
        new_topics_covered = {item['topic'].id for item in new_allocation}
        
        topics_gained = new_topics_covered - current_topics_covered
        topics_lost = current_topics_covered - new_topics_covered
        
        current_score = self.optimization_engine.calculate_expected_score(
            current_topics, current_courses
        )
        
        simulated_topics = self._apply_allocation_to_topics(
            deepcopy(current_topics), new_allocation
        )
        simulated_score = self.optimization_engine.calculate_expected_score(
            simulated_topics, current_courses
        )
        
        return {
            'scenario': 'study_hours_change',
            'current_hours': current_hours,
            'new_hours': new_hours,
            'current_topics_covered': len(current_topics_covered),
            'new_topics_covered': len(new_topics_covered),
            'topics_gained': len(topics_gained),
            'topics_lost': len(topics_lost),
            'current_expected_scores': current_score,
            'simulated_expected_scores': simulated_score,
            'recommendation': 'increase_hours' if new_hours > current_hours 
                            and len(topics_gained) > 0 else 'maintain_hours'
        }
    
    def simulate_ignore_low_weight(self,
                                   current_topics: List[Topic],
                                   current_courses: List[Course],
                                   priorities: List[TopicPriority],
                                   available_hours: float,
                                   weight_threshold: float = 0.1) -> Dict:
        """Simulate ignoring topics below a certain weight threshold."""
        filtered_priorities = [
            p for p in priorities if p.topic.weight >= weight_threshold
        ]
        
        original_allocation = self.optimization_engine.optimize_time_allocation(
            priorities, available_hours
        )
        
        filtered_allocation = self.optimization_engine.optimize_time_allocation(
            filtered_priorities, available_hours
        )
        
        ignored_topics = [
            p.topic.name for p in priorities if p.topic.weight < weight_threshold
        ]
        
        time_saved = sum(
            item['allocated_hours'] 
            for item in original_allocation 
            if item['topic'].weight < weight_threshold
        )
        
        original_score = self.optimization_engine.calculate_expected_score(
            current_topics, current_courses
        )
        
        simulated_topics = self._apply_allocation_to_topics(
            deepcopy(current_topics), filtered_allocation
        )
        simulated_score = self.optimization_engine.calculate_expected_score(
            simulated_topics, current_courses
        )
        
        return {
            'scenario': 'ignore_low_weight',
            'weight_threshold': weight_threshold,
            'ignored_topics_count': len(ignored_topics),
            'ignored_topics': ignored_topics,
            'time_saved_hours': round(time_saved, 2),
            'original_expected_scores': original_score,
            'simulated_expected_scores': simulated_score,
            'recommendation': 'focus_strategy' if time_saved > 1.0 else 'cover_all'
        }
    
    def simulate_exam_date_change(self,
                                  current_topics: List[Topic],
                                  current_courses: List[Course],
                                  priorities: List[TopicPriority],
                                  course_id: int,
                                  days_shift: int) -> Dict:
        """Simulate moving exam date earlier or later."""
        simulated_courses = deepcopy(current_courses)
        
        for course in simulated_courses:
            if course.id == course_id:
                course.exam_date = course.exam_date + timedelta(days=days_shift)
                break
        
        current_risks = self.optimization_engine.identify_risks(
            current_topics, current_courses
        )
        
        simulated_risks = self.optimization_engine.identify_risks(
            current_topics, simulated_courses
        )
        
        current_score = self.optimization_engine.calculate_expected_score(
            current_topics, current_courses
        )
        simulated_score = self.optimization_engine.calculate_expected_score(
            current_topics, simulated_courses
        )
        
        return {
            'scenario': 'exam_date_change',
            'course_id': course_id,
            'days_shift': days_shift,
            'direction': 'earlier' if days_shift < 0 else 'later',
            'current_risks_count': len(current_risks),
            'simulated_risks_count': len(simulated_risks),
            'current_critical_risks': len([r for r in current_risks if r['severity'] == 'CRITICAL']),
            'simulated_critical_risks': len([r for r in simulated_risks if r['severity'] == 'CRITICAL']),
            'current_expected_scores': current_score,
            'simulated_expected_scores': simulated_score
        }
    
    def compare_strategies(self,
                          current_topics: List[Topic],
                          current_courses: List[Course],
                          priorities: List[TopicPriority],
                          available_hours: float) -> Dict:
        """Compare different study strategies."""
        strategies = {}
        
        # Strategy 1: Balanced revision (normal priority)
        balanced_allocation = self.optimization_engine.optimize_time_allocation(
            priorities, available_hours
        )
        balanced_topics = self._apply_allocation_to_topics(
            deepcopy(current_topics), balanced_allocation
        )
        balanced_score = self.optimization_engine.calculate_expected_score(
            balanced_topics, current_courses
        )
        
        strategies['balanced'] = {
            'name': 'Balanced Revision',
            'description': 'Study all topics based on normal priority',
            'topics_covered': len(balanced_allocation),
            'expected_scores': balanced_score,
            'total_time': available_hours
        }
        
        # Strategy 2: High-weight focus
        high_weight_priorities = sorted(
            priorities, 
            key=lambda p: p.topic.weight * (100 - p.topic.skill_level), 
            reverse=True
        )
        high_weight_allocation = self.optimization_engine.optimize_time_allocation(
            high_weight_priorities, available_hours
        )
        high_weight_topics = self._apply_allocation_to_topics(
            deepcopy(current_topics), high_weight_allocation
        )
        high_weight_score = self.optimization_engine.calculate_expected_score(
            high_weight_topics, current_courses
        )
        
        strategies['high_weight_focus'] = {
            'name': 'High-Weight Focus',
            'description': 'Prioritize topics with highest weights',
            'topics_covered': len(high_weight_allocation),
            'expected_scores': high_weight_score,
            'total_time': available_hours
        }
        
        # Strategy 3: Weak-topic focus
        weak_priorities = sorted(
            priorities,
            key=lambda p: p.topic.skill_level,
            reverse=False
        )
        weak_allocation = self.optimization_engine.optimize_time_allocation(
            weak_priorities, available_hours
        )
        weak_topics = self._apply_allocation_to_topics(
            deepcopy(current_topics), weak_allocation
        )
        weak_score = self.optimization_engine.calculate_expected_score(
            weak_topics, current_courses
        )
        
        strategies['weak_focus'] = {
            'name': 'Weak Topics Focus',
            'description': 'Focus on improving weakest topics first',
            'topics_covered': len(weak_allocation),
            'expected_scores': weak_score,
            'total_time': available_hours
        }
        
        best_strategy = max(
            strategies.items(),
            key=lambda x: sum(
                s['estimated_score'] 
                for s in x[1]['expected_scores'].values()
            )
        )
        
        return {
            'strategies': strategies,
            'best_strategy': best_strategy[0],
            'best_strategy_name': best_strategy[1]['name'],
            'reason': f"Highest projected total score across all courses"
        }
    
    def _apply_allocation_to_topics(self, topics: List[Topic], 
                                   allocation: List[Dict]) -> List[Topic]:
        """Simulate skill improvement based on time allocation."""
        for item in allocation:
            for topic in topics:
                if topic.id == item['topic'].id:
                    hours = item['allocated_hours']
                    skill_gain = min(hours * 8, 100 - topic.skill_level)
                    topic.skill_level = min(100, topic.skill_level + skill_gain)
                    break
        
        return topics
