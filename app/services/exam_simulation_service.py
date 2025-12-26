from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.storage.database import Database, TopicDB, CourseDB, QuizAttemptDB, QuizDB
from sqlalchemy import func


class ExamSimulationService:
    """
    Phase 4: Exam-Day Simulation & Reality Dashboard
    TICKET-406: Simulate exam outcome if exam were today
    TICKET-407: Compare perceived effort vs actual progress
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.passing_threshold = 60.0
    
    def simulate_exam_today(self, course_id: int) -> Dict:
        """
        TICKET-406: Simulate exam outcome if exam were today.
        
        Output:
        - Estimated score
        - Fail/pass probability
        - Weakest blocking topics
        """
        session = self.db.get_session()
        try:
            course = session.query(CourseDB).filter(CourseDB.id == course_id).first()
            if not course:
                return {'error': 'Course not found'}
            
            topics = session.query(TopicDB).filter(TopicDB.course_id == course_id).all()
            
            if not topics:
                return {
                    'course_id': course_id,
                    'course_name': course.name,
                    'estimated_score': 0,
                    'pass_probability': 0,
                    'will_pass': False,
                    'topics_analyzed': 0,
                    'error': 'No topics found'
                }
            
            # Calculate weighted score
            total_weight = sum(t.weight for t in topics)
            weighted_score = 0
            weak_topics = []
            critical_gaps = []
            
            for topic in topics:
                # Use quiz performance if available, otherwise skill level
                quizzes = session.query(QuizDB).filter(QuizDB.topic_id == topic.id).all()
                quiz_ids = [q.id for q in quizzes]
                
                recent_attempts = session.query(QuizAttemptDB).filter(
                    QuizAttemptDB.quiz_id.in_(quiz_ids) if quiz_ids else False
                ).order_by(QuizAttemptDB.attempted_at.desc()).limit(3).all()
                
                if recent_attempts:
                    avg_quiz = sum(a.score for a in recent_attempts) / len(recent_attempts)
                    # Weight quiz performance higher than self-assessment
                    topic_score = (avg_quiz * 0.7 + topic.skill_level * 0.3)
                else:
                    # Penalize if no quiz taken
                    topic_score = topic.skill_level * 0.6
                
                weighted_score += topic_score * (topic.weight / total_weight)
                
                # Identify weak topics
                if topic_score < 50:
                    weak_topics.append({
                        'name': topic.name,
                        'score': topic_score,
                        'weight': topic.weight,
                        'impact': topic.weight * (50 - topic_score)
                    })
                
                # Critical gaps (high weight, low score)
                if topic.weight > 0.2 and topic_score < 60:
                    critical_gaps.append({
                        'name': topic.name,
                        'score': topic_score,
                        'weight': topic.weight,
                        'gap': 60 - topic_score
                    })
            
            # Sort by impact
            weak_topics.sort(key=lambda x: x['impact'], reverse=True)
            critical_gaps.sort(key=lambda x: x['gap'] * x['weight'], reverse=True)
            
            # Calculate pass probability based on distance from threshold
            distance_from_pass = weighted_score - self.passing_threshold
            if distance_from_pass >= 20:
                pass_probability = 95
            elif distance_from_pass >= 10:
                pass_probability = 85
            elif distance_from_pass >= 5:
                pass_probability = 70
            elif distance_from_pass >= 0:
                pass_probability = 55
            elif distance_from_pass >= -5:
                pass_probability = 35
            elif distance_from_pass >= -10:
                pass_probability = 15
            else:
                pass_probability = 5
            
            days_until_exam = (course.exam_date - datetime.now()).days
            
            return {
                'course_id': course_id,
                'course_name': course.name,
                'exam_date': course.exam_date.isoformat(),
                'days_remaining': days_until_exam,
                'estimated_score': round(weighted_score, 2),
                'passing_threshold': self.passing_threshold,
                'pass_probability': pass_probability,
                'will_pass': weighted_score >= self.passing_threshold,
                'topics_analyzed': len(topics),
                'weakest_topics': weak_topics[:5],
                'critical_gaps': critical_gaps[:3],
                'risk_level': self._calculate_risk_level(weighted_score, days_until_exam)
            }
        finally:
            session.close()
    
    def _calculate_risk_level(self, score: float, days_remaining: int) -> str:
        """Calculate overall risk level"""
        if score >= 75:
            return "LOW"
        elif score >= 60 and days_remaining > 7:
            return "MODERATE"
        elif score >= 50 and days_remaining > 14:
            return "MODERATE"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def get_motivation_vs_reality_dashboard(self, course_id: int, days: int = 30) -> Dict:
        """
        TICKET-407: Motivation vs Reality Dashboard
        Compare perceived effort vs actual progress.
        
        Views:
        - Time spent vs skill gained
        - Honest score per topic
        - Trend indicators
        """
        session = self.db.get_session()
        try:
            from app.storage.database import StudySessionDB, SkillHistoryDB
            
            course = session.query(CourseDB).filter(CourseDB.id == course_id).first()
            if not course:
                return {'error': 'Course not found'}
            
            topics = session.query(TopicDB).filter(TopicDB.course_id == course_id).all()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            topic_analysis = []
            total_time = 0
            total_skill_gain = 0
            
            for topic in topics:
                # Get study time
                sessions = session.query(StudySessionDB).filter(
                    StudySessionDB.topic_id == topic.id,
                    StudySessionDB.start_time >= cutoff_date,
                    StudySessionDB.end_time.isnot(None)
                ).all()
                
                time_spent = sum(s.duration_minutes for s in sessions)
                total_time += time_spent
                
                # Get skill changes
                skill_changes = session.query(SkillHistoryDB).filter(
                    SkillHistoryDB.topic_id == topic.id,
                    SkillHistoryDB.timestamp >= cutoff_date
                ).order_by(SkillHistoryDB.timestamp).all()
                
                skill_gain = 0
                if skill_changes:
                    skill_gain = skill_changes[-1].new_skill - skill_changes[0].previous_skill
                    total_skill_gain += skill_gain
                
                # Calculate efficiency
                efficiency = skill_gain / (time_spent / 60) if time_spent > 0 else 0
                
                # Get quiz reality check
                quizzes = session.query(QuizDB).filter(QuizDB.topic_id == topic.id).all()
                quiz_ids = [q.id for q in quizzes]
                
                quiz_attempts = session.query(QuizAttemptDB).filter(
                    QuizAttemptDB.quiz_id.in_(quiz_ids) if quiz_ids else False,
                    QuizAttemptDB.attempted_at >= cutoff_date
                ).all()
                
                avg_quiz = None
                if quiz_attempts:
                    avg_quiz = sum(a.score for a in quiz_attempts) / len(quiz_attempts)
                
                # Determine trend
                if skill_gain > 10:
                    trend = "📈 Improving"
                elif skill_gain > 0:
                    trend = "➡️  Slow Progress"
                elif skill_gain == 0:
                    trend = "⏸️  Stagnant"
                else:
                    trend = "📉 Declining"
                
                # Reality check
                reality_gap = None
                if avg_quiz is not None:
                    reality_gap = topic.skill_level - avg_quiz
                
                topic_analysis.append({
                    'topic_name': topic.name,
                    'weight': topic.weight,
                    'time_spent_hours': round(time_spent / 60, 2),
                    'skill_gain': round(skill_gain, 2),
                    'current_skill': topic.skill_level,
                    'avg_quiz_score': round(avg_quiz, 2) if avg_quiz else None,
                    'reality_gap': round(reality_gap, 2) if reality_gap else None,
                    'efficiency': round(efficiency, 2),
                    'trend': trend,
                    'honest_assessment': self._get_honest_assessment(time_spent, skill_gain, avg_quiz, topic.skill_level)
                })
            
            # Sort by efficiency (or lack thereof)
            topic_analysis.sort(key=lambda x: x['efficiency'])
            
            # Overall metrics
            avg_efficiency = total_skill_gain / (total_time / 60) if total_time > 0 else 0
            
            return {
                'course_id': course_id,
                'course_name': course.name,
                'days_analyzed': days,
                'total_time_hours': round(total_time / 60, 2),
                'total_skill_gain': round(total_skill_gain, 2),
                'average_efficiency': round(avg_efficiency, 2),
                'topics': topic_analysis,
                'summary': self._generate_reality_summary(total_time, total_skill_gain, topic_analysis)
            }
        finally:
            session.close()
    
    def _get_honest_assessment(self, time_spent: float, skill_gain: float, avg_quiz: Optional[float], current_skill: float) -> str:
        """Generate honest assessment of topic performance"""
        if time_spent > 120 and skill_gain < 5:
            return "⚠️ Time wasted - no progress"
        elif time_spent > 60 and skill_gain < 0:
            return "🚨 Declining despite effort"
        elif avg_quiz and (current_skill - avg_quiz > 20):
            return "⚠️ Overconfident - quiz reveals truth"
        elif skill_gain > 15 and avg_quiz and avg_quiz > 70:
            return "✅ Real, verified progress"
        elif skill_gain > 10:
            return "✓ Good progress (needs quiz verification)"
        elif time_spent < 30 and skill_gain == 0:
            return "⏸️ Needs attention"
        else:
            return "➡️  Marginal progress"
    
    def _generate_reality_summary(self, total_time: float, total_skill_gain: float, topics: List[Dict]) -> str:
        """Generate overall reality check summary"""
        hours = total_time / 60
        
        if hours < 5:
            return "⚠️ Very low effort - exam prep not started seriously"
        elif total_skill_gain < 10 and hours > 20:
            return "🚨 High time investment, minimal return - strategy needs revision"
        elif total_skill_gain > 50:
            return "✅ Strong progress - keep momentum"
        elif total_skill_gain > 20:
            return "✓ Decent progress - stay consistent"
        else:
            return "⚠️ Progress below expectations - needs acceleration"
