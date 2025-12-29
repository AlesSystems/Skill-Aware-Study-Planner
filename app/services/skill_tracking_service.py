from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models.models import SkillHistory
from app.storage.database import Database, SkillHistoryDB, TopicDB


class SkillTrackingService:
    def __init__(self, db: Database):
        self.db = db
        self.max_skill_increase_per_day = 15.0
        self.self_assessment_weight = 0.5
        self.quiz_weight = 1.0
        self.decay_start_days = 7
        self.decay_rate_per_day = 0.5
    
    def record_skill_change(self, topic_id: int, new_skill: float, reason: str, previous_skill: Optional[float] = None) -> SkillHistory:
        session = self.db.get_session()
        try:
            topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if not topic:
                raise ValueError("Topic not found")
            
            if previous_skill is None:
                previous_skill = topic.skill_level
            
            if reason == "self-assessment":
                actual_change = (new_skill - previous_skill) * self.self_assessment_weight
                new_skill = min(100, max(0, previous_skill + actual_change))
            
            today_changes = session.query(SkillHistoryDB).filter(
                SkillHistoryDB.topic_id == topic_id,
                SkillHistoryDB.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ).all()
            
            total_increase_today = sum(
                h.new_skill - h.previous_skill for h in today_changes if h.new_skill > h.previous_skill
            )
            
            if new_skill > previous_skill:
                increase = new_skill - previous_skill
                if total_increase_today + increase > self.max_skill_increase_per_day:
                    allowed_increase = max(0, self.max_skill_increase_per_day - total_increase_today)
                    new_skill = previous_skill + allowed_increase
            
            new_skill = min(100, max(0, new_skill))
            
            db_history = SkillHistoryDB(
                topic_id=topic_id,
                timestamp=datetime.now(),
                previous_skill=previous_skill,
                new_skill=new_skill,
                reason=reason
            )
            session.add(db_history)
            
            topic.skill_level = new_skill
            
            session.commit()
            session.refresh(db_history)
            
            return SkillHistory(
                id=db_history.id,
                topic_id=db_history.topic_id,
                timestamp=db_history.timestamp,
                previous_skill=db_history.previous_skill,
                new_skill=db_history.new_skill,
                reason=db_history.reason
            )
        finally:
            session.close()
    
    def update_skill_from_quiz(self, topic_id: int, quiz_score: float):
        skill_change = (quiz_score - 50) * 0.3
        
        session = self.db.get_session()
        try:
            topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if topic:
                new_skill = min(100, max(0, topic.skill_level + skill_change))
                self.record_skill_change(topic_id, new_skill, "quiz")
        finally:
            session.close()
    
    def get_skill_history(self, topic_id: int, limit: Optional[int] = None) -> List[SkillHistory]:
        session = self.db.get_session()
        try:
            query = session.query(SkillHistoryDB).filter(
                SkillHistoryDB.topic_id == topic_id
            ).order_by(SkillHistoryDB.timestamp.desc())
            
            if limit:
                query = query.limit(limit)
            
            db_histories = query.all()
            
            return [
                SkillHistory(
                    id=h.id,
                    topic_id=h.topic_id,
                    timestamp=h.timestamp,
                    previous_skill=h.previous_skill,
                    new_skill=h.new_skill,
                    reason=h.reason
                ) for h in db_histories
            ]
        finally:
            session.close()
    
    def apply_skill_decay(self):
        from app.storage.database import StudySessionDB
        
        session = self.db.get_session()
        try:
            topics = session.query(TopicDB).all()
            cutoff_date = datetime.now() - timedelta(days=self.decay_start_days)
            
            for topic in topics:
                last_session = session.query(StudySessionDB).filter(
                    StudySessionDB.topic_id == topic.id,
                    StudySessionDB.end_time.isnot(None)
                ).order_by(StudySessionDB.end_time.desc()).first()
                
                if not last_session or last_session.end_time < cutoff_date:
                    days_inactive = (datetime.now() - last_session.end_time).days if last_session else 30
                    decay_days = max(0, days_inactive - self.decay_start_days)
                    
                    if decay_days > 0:
                        decay_amount = min(topic.skill_level * 0.3, decay_days * self.decay_rate_per_day)
                        new_skill = max(0, topic.skill_level - decay_amount)
                        
                        if abs(new_skill - topic.skill_level) > 0.1:
                            self.record_skill_change(topic.id, new_skill, "decay")
            
            session.commit()
        finally:
            session.close()
    
    def apply_decay_to_all(self) -> List[Dict]:
        """Apply skill decay and return results"""
        from app.storage.database import StudySessionDB
        
        session = self.db.get_session()
        results = []
        try:
            topics = session.query(TopicDB).all()
            cutoff_date = datetime.now() - timedelta(days=self.decay_start_days)
            
            for topic in topics:
                last_session = session.query(StudySessionDB).filter(
                    StudySessionDB.topic_id == topic.id,
                    StudySessionDB.end_time.isnot(None)
                ).order_by(StudySessionDB.end_time.desc()).first()
                
                if not last_session or last_session.end_time < cutoff_date:
                    days_inactive = (datetime.now() - last_session.end_time).days if last_session else 30
                    decay_days = max(0, days_inactive - self.decay_start_days)
                    
                    if decay_days > 0:
                        decay_amount = min(topic.skill_level * 0.3, decay_days * self.decay_rate_per_day)
                        new_skill = max(0, topic.skill_level - decay_amount)
                        
                        if abs(new_skill - topic.skill_level) > 0.1:
                            old_skill = topic.skill_level
                            self.record_skill_change(topic.id, new_skill, "decay", old_skill)
                            results.append({
                                "topic_id": topic.id,
                                "topic_name": topic.name,
                                "old_skill": old_skill,
                                "new_skill": new_skill,
                                "decay_amount": decay_amount
                            })
            
            session.commit()
            return results
        finally:
            session.close()
    
    def get_decay_eligible_topics(self) -> List[Dict]:
        """Get topics eligible for skill decay"""
        from app.storage.database import StudySessionDB
        
        session = self.db.get_session()
        try:
            topics = session.query(TopicDB).all()
            cutoff_date = datetime.now() - timedelta(days=self.decay_start_days)
            eligible = []
            
            for topic in topics:
                last_session = session.query(StudySessionDB).filter(
                    StudySessionDB.topic_id == topic.id,
                    StudySessionDB.end_time.isnot(None)
                ).order_by(StudySessionDB.end_time.desc()).first()
                
                days_inactive = (datetime.now() - last_session.end_time).days if last_session else 30
                
                if not last_session or last_session.end_time < cutoff_date:
                    eligible.append({
                        "topic_id": topic.id,
                        "topic_name": topic.name,
                        "current_skill": topic.skill_level,
                        "days_inactive": days_inactive,
                        "eligible_for_decay": days_inactive > self.decay_start_days
                    })
            
            return eligible
        finally:
            session.close()
