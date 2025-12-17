from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models.models import StudySession
from app.storage.database import Database, StudySessionDB


class StudySessionService:
    def __init__(self, db: Database):
        self.db = db
    
    def start_session(self, topic_id: int) -> StudySession:
        session = self.db.get_session()
        try:
            db_session = StudySessionDB(
                topic_id=topic_id,
                start_time=datetime.now(),
                end_time=None,
                duration_minutes=None
            )
            session.add(db_session)
            session.commit()
            session.refresh(db_session)
            
            return StudySession(
                id=db_session.id,
                topic_id=db_session.topic_id,
                start_time=db_session.start_time,
                end_time=db_session.end_time,
                duration_minutes=db_session.duration_minutes
            )
        finally:
            session.close()
    
    def end_session(self, session_id: int) -> StudySession:
        session = self.db.get_session()
        try:
            db_session = session.query(StudySessionDB).filter(
                StudySessionDB.id == session_id
            ).first()
            
            if not db_session:
                raise ValueError("Study session not found")
            
            if db_session.end_time is not None:
                raise ValueError("Session already ended")
            
            end_time = datetime.now()
            duration = (end_time - db_session.start_time).total_seconds() / 60
            
            db_session.end_time = end_time
            db_session.duration_minutes = duration
            
            session.commit()
            session.refresh(db_session)
            
            return StudySession(
                id=db_session.id,
                topic_id=db_session.topic_id,
                start_time=db_session.start_time,
                end_time=db_session.end_time,
                duration_minutes=db_session.duration_minutes
            )
        finally:
            session.close()
    
    def get_active_session(self, topic_id: Optional[int] = None) -> Optional[StudySession]:
        session = self.db.get_session()
        try:
            query = session.query(StudySessionDB).filter(
                StudySessionDB.end_time.is_(None)
            )
            
            if topic_id is not None:
                query = query.filter(StudySessionDB.topic_id == topic_id)
            
            db_session = query.first()
            
            if not db_session:
                return None
            
            return StudySession(
                id=db_session.id,
                topic_id=db_session.topic_id,
                start_time=db_session.start_time,
                end_time=db_session.end_time,
                duration_minutes=db_session.duration_minutes
            )
        finally:
            session.close()
    
    def get_topic_sessions(self, topic_id: int) -> List[StudySession]:
        session = self.db.get_session()
        try:
            db_sessions = session.query(StudySessionDB).filter(
                StudySessionDB.topic_id == topic_id,
                StudySessionDB.end_time.isnot(None)
            ).order_by(StudySessionDB.start_time.desc()).all()
            
            return [
                StudySession(
                    id=s.id,
                    topic_id=s.topic_id,
                    start_time=s.start_time,
                    end_time=s.end_time,
                    duration_minutes=s.duration_minutes
                ) for s in db_sessions
            ]
        finally:
            session.close()
    
    def get_daily_time_breakdown(self, days: int = 7) -> Dict[str, Dict[int, float]]:
        session = self.db.get_session()
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            db_sessions = session.query(StudySessionDB).filter(
                StudySessionDB.start_time >= start_date,
                StudySessionDB.end_time.isnot(None)
            ).all()
            
            breakdown = {}
            
            for db_session in db_sessions:
                date_key = db_session.start_time.strftime('%Y-%m-%d')
                if date_key not in breakdown:
                    breakdown[date_key] = {}
                
                topic_id = db_session.topic_id
                if topic_id not in breakdown[date_key]:
                    breakdown[date_key][topic_id] = 0
                
                breakdown[date_key][topic_id] += db_session.duration_minutes
            
            return breakdown
        finally:
            session.close()
    
    def get_total_time_per_topic(self) -> Dict[int, float]:
        session = self.db.get_session()
        try:
            db_sessions = session.query(StudySessionDB).filter(
                StudySessionDB.end_time.isnot(None)
            ).all()
            
            totals = {}
            for db_session in db_sessions:
                topic_id = db_session.topic_id
                if topic_id not in totals:
                    totals[topic_id] = 0
                totals[topic_id] += db_session.duration_minutes
            
            return totals
        finally:
            session.close()
