from typing import Optional, List, Dict
from datetime import datetime
import json
from app.storage.database import DecisionLogDB


class DecisionService:
    def __init__(self, db):
        self.db = db
    
    def log_decision(self, decision_type: str, explanation: str, 
                    topic_id: Optional[int] = None, metadata: Optional[Dict] = None):
        """Log a planning decision with explanation."""
        session = self.db.get_session()
        try:
            log = DecisionLogDB(
                timestamp=datetime.now(),
                decision_type=decision_type,
                topic_id=topic_id,
                explanation=explanation,
                metadata=json.dumps(metadata) if metadata else None
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
        finally:
            session.close()
    
    def get_recent_decisions(self, limit: int = 20) -> List[Dict]:
        """Get recent planning decisions."""
        session = self.db.get_session()
        try:
            logs = session.query(DecisionLogDB).order_by(
                DecisionLogDB.timestamp.desc()
            ).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp,
                    'decision_type': log.decision_type,
                    'topic_id': log.topic_id,
                    'explanation': log.explanation,
                    'metadata': json.loads(log.metadata) if log.metadata else None
                })
            
            return result
        finally:
            session.close()
    
    def get_decisions_by_type(self, decision_type: str, limit: int = 10) -> List[Dict]:
        """Get decisions of a specific type."""
        session = self.db.get_session()
        try:
            logs = session.query(DecisionLogDB).filter(
                DecisionLogDB.decision_type == decision_type
            ).order_by(DecisionLogDB.timestamp.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp,
                    'topic_id': log.topic_id,
                    'explanation': log.explanation,
                    'metadata': json.loads(log.metadata) if log.metadata else None
                })
            
            return result
        finally:
            session.close()
    
    def get_decisions_for_topic(self, topic_id: int, limit: int = 10) -> List[Dict]:
        """Get all decisions related to a specific topic."""
        session = self.db.get_session()
        try:
            logs = session.query(DecisionLogDB).filter(
                DecisionLogDB.topic_id == topic_id
            ).order_by(DecisionLogDB.timestamp.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp,
                    'decision_type': log.decision_type,
                    'explanation': log.explanation,
                    'metadata': json.loads(log.metadata) if log.metadata else None
                })
            
            return result
        finally:
            session.close()
