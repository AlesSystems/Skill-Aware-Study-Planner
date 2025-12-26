from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.storage.database import Database, TopicDB, CourseDB
from app.services.honesty_service import HonestyService
from app.services.exam_simulation_service import ExamSimulationService


class ForcedReprioritizationEngine:
    """
    Phase 4: TICKET-405 - Forced Re-Prioritization Engine
    Override user preferences when risk is too high.
    
    Triggers:
    - Imminent exam
    - Critical prerequisites missing
    - Repeated avoidance
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.honesty_service = HonestyService(db)
        self.exam_sim_service = ExamSimulationService(db)
        self.imminent_exam_days = 7
        self.critical_skill_threshold = 40.0
        self.critical_weight_threshold = 0.25
    
    def check_forced_reprioritization(self, course_id: int) -> Dict:
        """
        Check if forced re-prioritization is needed.
        Returns override decisions and explanations.
        """
        session = self.db.get_session()
        try:
            course = session.query(CourseDB).filter(CourseDB.id == course_id).first()
            if not course:
                return {'error': 'Course not found'}
            
            days_until_exam = (course.exam_date - datetime.now()).days
            topics = session.query(TopicDB).filter(TopicDB.course_id == course_id).all()
            
            overrides = []
            forced = False
            risk_level = "NORMAL"
            
            # Trigger 1: Imminent exam
            if days_until_exam <= self.imminent_exam_days:
                exam_sim = self.exam_sim_service.simulate_exam_today(course_id)
                
                if not exam_sim.get('will_pass'):
                    forced = True
                    risk_level = "CRITICAL"
                    overrides.append({
                        'trigger': 'imminent_exam',
                        'severity': 'CRITICAL',
                        'message': f"⚠️ EXAM IN {days_until_exam} DAYS - Estimated score: {exam_sim['estimated_score']:.0f}% (Failing)",
                        'action': 'Force focus on critical gaps',
                        'locked_topics': self._get_low_priority_topics(topics),
                        'mandatory_topics': [g['name'] for g in exam_sim.get('critical_gaps', [])]
                    })
            
            # Trigger 2: Critical prerequisites missing
            critical_missing = []
            for topic in topics:
                if topic.weight > self.critical_weight_threshold and topic.skill_level < self.critical_skill_threshold:
                    critical_missing.append(topic)
            
            if critical_missing:
                forced = True
                risk_level = "HIGH" if risk_level == "NORMAL" else risk_level
                overrides.append({
                    'trigger': 'critical_prerequisites',
                    'severity': 'HIGH',
                    'message': f"🚨 {len(critical_missing)} critical topics below {self.critical_skill_threshold}%",
                    'action': 'Block low-priority topics until critical topics reach 60%',
                    'mandatory_topics': [t.name for t in critical_missing],
                    'locked_topics': self._get_low_priority_topics(topics)
                })
            
            # Trigger 3: Repeated avoidance detected
            avoidance_analysis = self.honesty_service.analyze_all_topics_honesty(course_id)
            avoided_topics = avoidance_analysis.get('avoidance', [])
            
            high_severity_avoidance = [a for a in avoided_topics if a['avoidance_severity'] > 50]
            
            if high_severity_avoidance:
                forced = True
                risk_level = "HIGH" if risk_level == "NORMAL" else risk_level
                overrides.append({
                    'trigger': 'repeated_avoidance',
                    'severity': 'HIGH',
                    'message': f"⚠️ Persistent avoidance of {len(high_severity_avoidance)} critical topics",
                    'action': 'Mandatory quiz required before accessing other topics',
                    'mandatory_topics': [a['topic_name'] for a in high_severity_avoidance],
                    'required_action': 'take_quiz'
                })
            
            # Trigger 4: Fake productivity detected
            fake_productivity = avoidance_analysis.get('fake_productivity', [])
            high_fake = [f for f in fake_productivity if f['fake_productivity_score'] > 60]
            
            if high_fake:
                forced = True
                overrides.append({
                    'trigger': 'fake_productivity',
                    'severity': 'MEDIUM',
                    'message': f"⚠️ {len(high_fake)} topics showing fake productivity patterns",
                    'action': 'Mandatory quiz or study method change required',
                    'affected_topics': [self._get_topic_name(f['topic_id']) for f in high_fake],
                    'required_action': 'take_quiz_or_change_method'
                })
            
            return {
                'course_id': course_id,
                'forced_reprioritization': forced,
                'risk_level': risk_level,
                'days_until_exam': days_until_exam,
                'overrides': overrides,
                'can_ignore': False if risk_level == "CRITICAL" else True,
                'explanation': self._generate_explanation(overrides)
            }
        finally:
            session.close()
    
    def _get_topic_name(self, topic_id: int) -> str:
        """Get topic name by ID"""
        session = self.db.get_session()
        try:
            topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            return topic.name if topic else f"Topic {topic_id}"
        finally:
            session.close()
    
    def _get_low_priority_topics(self, topics: List) -> List[str]:
        """Identify low-priority topics that should be locked"""
        low_priority = []
        for topic in topics:
            # Low priority = low weight or already high skill
            if topic.weight < 0.15 or topic.skill_level > 80:
                low_priority.append(topic.name)
        return low_priority
    
    def _generate_explanation(self, overrides: List[Dict]) -> str:
        """Generate clear explanation for overrides"""
        if not overrides:
            return "No forced re-prioritization needed. You have control."
        
        explanation = "FORCED RE-PRIORITIZATION ACTIVE:\n\n"
        
        for override in overrides:
            explanation += f"• {override['message']}\n"
            explanation += f"  Action: {override['action']}\n\n"
        
        explanation += "These overrides are based on objective data to protect your exam outcome."
        
        return explanation
    
    def apply_priority_overrides(self, course_id: int, priorities: List) -> List:
        """
        Apply forced re-prioritization to a list of topic priorities.
        Modifies priority scores based on overrides.
        """
        check = self.check_forced_reprioritization(course_id)
        
        if not check['forced_reprioritization']:
            return priorities
        
        # Extract mandatory and locked topics
        mandatory_topics = set()
        locked_topics = set()
        
        for override in check['overrides']:
            if 'mandatory_topics' in override:
                mandatory_topics.update(override['mandatory_topics'])
            if 'locked_topics' in override:
                locked_topics.update(override['locked_topics'])
        
        # Apply overrides
        modified_priorities = []
        for priority in priorities:
            topic_name = priority.topic.name
            
            if topic_name in mandatory_topics:
                # Boost priority massively
                priority.priority_score *= 10
                priority.urgency_factor = 5.0
            elif topic_name in locked_topics:
                # Reduce priority to near zero
                priority.priority_score *= 0.01
            
            modified_priorities.append(priority)
        
        # Re-sort
        modified_priorities.sort(key=lambda x: x.priority_score, reverse=True)
        
        return modified_priorities


class ConsequenceEngine:
    """
    Phase 4: TICKET-408 - Hard Warnings & Lockouts
    Introduce consequences for continued avoidance.
    
    Examples:
    - Lock easy topics
    - Force quizzes
    - Block plan generation temporarily
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.honesty_service = HonestyService(db)
        self.reprioritization = ForcedReprioritizationEngine(db)
    
    def check_lockouts(self, course_id: int, user_action: str) -> Dict:
        """
        Check if user action should be locked/blocked.
        
        Args:
            course_id: Course ID
            user_action: Action user is trying to take (e.g., 'study_low_priority', 'skip_quiz', 'generate_plan')
        
        Returns:
            Dict with 'allowed' boolean and 'reason' if blocked
        """
        check = self.reprioritization.check_forced_reprioritization(course_id)
        
        if not check['forced_reprioritization']:
            return {'allowed': True}
        
        # Parse overrides for lockout rules
        for override in check['overrides']:
            if override['trigger'] == 'imminent_exam' and override['severity'] == 'CRITICAL':
                # Block low-priority study
                if user_action == 'study_low_priority':
                    return {
                        'allowed': False,
                        'reason': f"🚨 EXAM IN {check['days_until_exam']} DAYS - Low-priority topics are LOCKED. Focus on critical gaps.",
                        'mandatory_topics': override.get('mandatory_topics', [])
                    }
            
            if override['trigger'] == 'repeated_avoidance':
                # Force quiz before other actions
                if user_action in ['study_other_topic', 'generate_plan']:
                    return {
                        'allowed': False,
                        'reason': f"⚠️ You must take a quiz on avoided topics first: {', '.join(override['mandatory_topics'][:3])}",
                        'required_action': 'take_quiz',
                        'mandatory_topics': override['mandatory_topics']
                    }
            
            if override['trigger'] == 'critical_prerequisites':
                # Block easy topics
                if user_action == 'study_easy_topic':
                    return {
                        'allowed': False,
                        'reason': "🚨 Critical topics below acceptable level. Easy topics are temporarily LOCKED.",
                        'mandatory_topics': override['mandatory_topics']
                    }
        
        return {'allowed': True}
    
    def get_active_consequences(self, course_id: int) -> List[str]:
        """Get list of active consequences/lockouts"""
        check = self.reprioritization.check_forced_reprioritization(course_id)
        
        consequences = []
        
        if check['forced_reprioritization']:
            for override in check['overrides']:
                if 'locked_topics' in override and override['locked_topics']:
                    consequences.append(f"🔒 Locked topics: {', '.join(override['locked_topics'][:3])} {'...' if len(override['locked_topics']) > 3 else ''}")
                
                if 'required_action' in override:
                    consequences.append(f"⚠️ Mandatory: {override['required_action'].replace('_', ' ').title()}")
        
        return consequences
