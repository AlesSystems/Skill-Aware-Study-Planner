from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from app.storage.database import Database, TopicDB, StudySessionDB, SkillHistoryDB, QuizAttemptDB, QuizDB
from sqlalchemy import func


class HonestyService:
    """
    Phase 4: Honesty & Reality Check System
    Detects self-deception, fake productivity, avoidance patterns, and overconfidence.
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.fake_productivity_threshold = 120.0
        self.min_quiz_improvement = 5.0
        self.avoidance_postponement_threshold = 3
        self.overconfidence_gap_threshold = 20.0
        self.brutal_honesty_mode = False
    
    def toggle_brutal_honesty_mode(self) -> bool:
        """TICKET-404: Toggle brutal honesty mode"""
        self.brutal_honesty_mode = not self.brutal_honesty_mode
        return self.brutal_honesty_mode
    
    def detect_fake_productivity(self, topic_id: int, days: int = 14) -> Dict:
        """
        TICKET-401: Fake Productivity Detection
        Detect when study time doesn't result in measurable improvement.
        
        Signals:
        - High time logged + no quiz improvement
        - Repeated study sessions without skill change
        - Avoidance of quizzes after long study time
        """
        session = self.db.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get total study time
            study_sessions = session.query(StudySessionDB).filter(
                StudySessionDB.topic_id == topic_id,
                StudySessionDB.start_time >= cutoff_date,
                StudySessionDB.end_time.isnot(None)
            ).all()
            
            total_time = sum(s.duration_minutes for s in study_sessions)
            
            # Get skill changes
            skill_changes = session.query(SkillHistoryDB).filter(
                SkillHistoryDB.topic_id == topic_id,
                SkillHistoryDB.timestamp >= cutoff_date
            ).order_by(SkillHistoryDB.timestamp).all()
            
            net_skill_change = 0
            if skill_changes:
                net_skill_change = skill_changes[-1].new_skill - skill_changes[0].previous_skill
            
            # Get quiz attempts
            quizzes = session.query(QuizDB).filter(QuizDB.topic_id == topic_id).all()
            quiz_ids = [q.id for q in quizzes]
            
            quiz_attempts = session.query(QuizAttemptDB).filter(
                QuizAttemptDB.quiz_id.in_(quiz_ids) if quiz_ids else False,
                QuizAttemptDB.attempted_at >= cutoff_date
            ).order_by(QuizAttemptDB.attempted_at).all()
            
            quiz_improvement = 0
            if len(quiz_attempts) >= 2:
                quiz_improvement = quiz_attempts[-1].score - quiz_attempts[0].score
            
            # Calculate fake productivity score
            fake_score = 0
            suspicious = False
            reasons = []
            
            if total_time > self.fake_productivity_threshold:
                if abs(net_skill_change) < 5:
                    fake_score += 30
                    reasons.append(f"{total_time:.0f} minutes studied with only {net_skill_change:.1f}% skill change")
                    suspicious = True
                
                if not quiz_attempts:
                    fake_score += 40
                    reasons.append("No quizzes taken despite extensive study time")
                    suspicious = True
                elif quiz_improvement < self.min_quiz_improvement:
                    fake_score += 25
                    reasons.append(f"Quiz scores improved by only {quiz_improvement:.1f}%")
                    suspicious = True
            
            # Repeated sessions without skill change
            session_count = len(study_sessions)
            if session_count >= 5 and abs(net_skill_change) < 3:
                fake_score += 20
                reasons.append(f"{session_count} study sessions with minimal skill change")
                suspicious = True
            
            return {
                'topic_id': topic_id,
                'fake_productivity_score': min(100, fake_score),
                'suspicious': suspicious,
                'total_study_time': total_time,
                'net_skill_change': net_skill_change,
                'quiz_attempts': len(quiz_attempts),
                'quiz_improvement': quiz_improvement,
                'reasons': reasons,
                'days_analyzed': days
            }
        finally:
            session.close()
    
    def detect_avoidance_patterns(self, topic_id: int, days: int = 21) -> Dict:
        """
        TICKET-402: Avoidance Pattern Detection
        Detect consistent avoidance of difficult or high-priority topics.
        
        Patterns:
        - Repeated postponement
        - Studying low-priority topics instead
        - Ignoring planner recommendations
        """
        session = self.db.get_session()
        try:
            topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if not topic:
                return {'error': 'Topic not found'}
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get study sessions for this topic
            topic_sessions = session.query(StudySessionDB).filter(
                StudySessionDB.topic_id == topic_id,
                StudySessionDB.start_time >= cutoff_date,
                StudySessionDB.end_time.isnot(None)
            ).all()
            
            # Get all sessions for the course
            all_topics = session.query(TopicDB).filter(
                TopicDB.course_id == topic.course_id
            ).all()
            topic_ids = [t.id for t in all_topics]
            
            all_sessions = session.query(StudySessionDB).filter(
                StudySessionDB.topic_id.in_(topic_ids),
                StudySessionDB.start_time >= cutoff_date,
                StudySessionDB.end_time.isnot(None)
            ).all()
            
            total_study_time = sum(s.duration_minutes for s in all_sessions)
            topic_study_time = sum(s.duration_minutes for s in topic_sessions)
            
            # Calculate skill gap (how much improvement needed)
            skill_gap = 100 - topic.skill_level
            
            # Calculate expected vs actual time proportion
            expected_proportion = (topic.weight * skill_gap) / 100
            actual_proportion = topic_study_time / total_study_time if total_study_time > 0 else 0
            
            avoidance_severity = 0
            avoided = False
            reasons = []
            
            # High priority but low study time
            if topic.weight > 0.3 and skill_gap > 30:
                if actual_proportion < expected_proportion * 0.5:
                    avoidance_severity += 40
                    reasons.append(f"High-priority topic ({topic.weight*100:.0f}% weight) severely understudied")
                    avoided = True
            
            # Low skill but no recent activity
            if skill_gap > 50:
                if len(topic_sessions) == 0:
                    avoidance_severity += 50
                    reasons.append(f"Skill level only {topic.skill_level:.0f}% but no study sessions")
                    avoided = True
                elif len(topic_sessions) < 2:
                    avoidance_severity += 30
                    reasons.append(f"Critically low skill ({topic.skill_level:.0f}%) with minimal effort")
                    avoided = True
            
            # Check for recent quiz avoidance
            last_session = topic_sessions[-1] if topic_sessions else None
            if last_session:
                quizzes = session.query(QuizDB).filter(QuizDB.topic_id == topic_id).all()
                quiz_ids = [q.id for q in quizzes]
                
                quiz_attempts = session.query(QuizAttemptDB).filter(
                    QuizAttemptDB.quiz_id.in_(quiz_ids) if quiz_ids else False,
                    QuizAttemptDB.attempted_at >= last_session.end_time
                ).all()
                
                if topic_study_time > 60 and not quiz_attempts:
                    avoidance_severity += 20
                    reasons.append("Studied for over 1 hour but avoided taking any quiz")
            
            return {
                'topic_id': topic_id,
                'topic_name': topic.name,
                'avoidance_severity': min(100, avoidance_severity),
                'avoided': avoided,
                'skill_level': topic.skill_level,
                'skill_gap': skill_gap,
                'weight': topic.weight,
                'study_time_minutes': topic_study_time,
                'expected_proportion': expected_proportion,
                'actual_proportion': actual_proportion,
                'reasons': reasons,
                'days_analyzed': days
            }
        finally:
            session.close()
    
    def detect_overconfidence(self, topic_id: int) -> Dict:
        """
        TICKET-403: Overconfidence Detection
        Detect mismatch between self-assessment and objective performance.
        
        Rules:
        - High self-rating + low quiz score
        - Skill increases without evidence
        """
        session = self.db.get_session()
        try:
            topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if not topic:
                return {'error': 'Topic not found'}
            
            # Get recent self-assessments
            self_assessments = session.query(SkillHistoryDB).filter(
                SkillHistoryDB.topic_id == topic_id,
                SkillHistoryDB.reason == 'self-assessment'
            ).order_by(SkillHistoryDB.timestamp.desc()).limit(5).all()
            
            # Get quiz performance
            quizzes = session.query(QuizDB).filter(QuizDB.topic_id == topic_id).all()
            quiz_ids = [q.id for q in quizzes]
            
            quiz_attempts = session.query(QuizAttemptDB).filter(
                QuizAttemptDB.quiz_id.in_(quiz_ids) if quiz_ids else False
            ).order_by(QuizAttemptDB.attempted_at.desc()).limit(3).all()
            
            overconfidence_score = 0
            overconfident = False
            reasons = []
            
            # Compare current skill level to quiz performance
            if quiz_attempts:
                avg_quiz_score = sum(q.score for q in quiz_attempts) / len(quiz_attempts)
                skill_quiz_gap = topic.skill_level - avg_quiz_score
                
                if skill_quiz_gap > self.overconfidence_gap_threshold:
                    overconfidence_score += 50
                    reasons.append(f"Self-assessed skill ({topic.skill_level:.0f}%) much higher than quiz average ({avg_quiz_score:.0f}%)")
                    overconfident = True
            
            # Check for unsupported skill increases
            if self_assessments:
                for assessment in self_assessments:
                    increase = assessment.new_skill - assessment.previous_skill
                    if increase > 15:
                        # Check if there was quiz evidence around that time
                        nearby_quizzes = session.query(QuizAttemptDB).filter(
                            QuizAttemptDB.quiz_id.in_(quiz_ids) if quiz_ids else False,
                            QuizAttemptDB.attempted_at >= assessment.timestamp - timedelta(days=1),
                            QuizAttemptDB.attempted_at <= assessment.timestamp + timedelta(days=1)
                        ).all()
                        
                        if not nearby_quizzes:
                            overconfidence_score += 30
                            reasons.append(f"Self-assessed {increase:.0f}% increase without quiz verification")
                            overconfident = True
                            break
            
            # High skill but never tested
            if topic.skill_level > 70 and not quiz_attempts:
                overconfidence_score += 40
                reasons.append(f"Claims {topic.skill_level:.0f}% skill but never taken a quiz")
                overconfident = True
            
            return {
                'topic_id': topic_id,
                'topic_name': topic.name,
                'overconfidence_score': min(100, overconfidence_score),
                'overconfident': overconfident,
                'current_skill': topic.skill_level,
                'avg_quiz_score': sum(q.score for q in quiz_attempts) / len(quiz_attempts) if quiz_attempts else None,
                'quiz_count': len(quiz_attempts),
                'reasons': reasons
            }
        finally:
            session.close()
    
    def analyze_all_topics_honesty(self, course_id: Optional[int] = None) -> Dict:
        """Analyze all topics for honesty issues"""
        session = self.db.get_session()
        try:
            query = session.query(TopicDB)
            if course_id:
                query = query.filter(TopicDB.course_id == course_id)
            
            topics = query.all()
            
            results = {
                'fake_productivity': [],
                'avoidance': [],
                'overconfidence': []
            }
            
            for topic in topics:
                fake = self.detect_fake_productivity(topic.id)
                if fake['suspicious']:
                    results['fake_productivity'].append(fake)
                
                avoidance = self.detect_avoidance_patterns(topic.id)
                if avoidance.get('avoided'):
                    results['avoidance'].append(avoidance)
                
                overconf = self.detect_overconfidence(topic.id)
                if overconf.get('overconfident'):
                    results['overconfidence'].append(overconf)
            
            return results
        finally:
            session.close()
    
    def get_honesty_warnings(self, course_id: Optional[int] = None) -> List[str]:
        """Get all honesty warnings for display"""
        analysis = self.analyze_all_topics_honesty(course_id)
        warnings = []
        
        prefix = "⚠️  WARNING: " if not self.brutal_honesty_mode else "🚨 BRUTAL TRUTH: "
        
        for fake in analysis['fake_productivity']:
            topic_id = fake['topic_id']
            if self.brutal_honesty_mode:
                warnings.append(f"{prefix}Topic {topic_id}: You're wasting time. {fake['total_study_time']:.0f} minutes logged with almost no progress.")
            else:
                warnings.append(f"{prefix}Topic {topic_id}: Study time not translating to improvement. Consider changing study methods.")
        
        for avoid in analysis['avoidance']:
            if self.brutal_honesty_mode:
                warnings.append(f"{prefix}{avoid['topic_name']}: Stop avoiding this. Skill at {avoid['skill_level']:.0f}% - this will fail you.")
            else:
                warnings.append(f"{prefix}{avoid['topic_name']}: High priority topic needs more attention (skill: {avoid['skill_level']:.0f}%)")
        
        for overconf in analysis['overconfidence']:
            if self.brutal_honesty_mode:
                warnings.append(f"{prefix}{overconf['topic_name']}: Your confidence is delusional. Quiz says {overconf['avg_quiz_score']:.0f}%, not {overconf['current_skill']:.0f}%.")
            else:
                warnings.append(f"{prefix}{overconf['topic_name']}: Performance gap detected. Quiz average lower than self-assessment.")
        
        return warnings
