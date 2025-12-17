from typing import Dict, List
from datetime import datetime, timedelta
from app.storage.database import Database, SkillHistoryDB, StudySessionDB, TopicDB
from app.storage.storage_service import StorageService


class ProgressVisualizationService:
    def __init__(self, storage: StorageService):
        self.storage = storage
        self.db = storage.db
    
    def get_skill_over_time(self, topic_id: int, days: int = 30) -> List[Dict]:
        session = self.db.get_session()
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            history = session.query(SkillHistoryDB).filter(
                SkillHistoryDB.topic_id == topic_id,
                SkillHistoryDB.timestamp >= cutoff
            ).order_by(SkillHistoryDB.timestamp).all()
            
            data = []
            for h in history:
                data.append({
                    'date': h.timestamp.strftime('%Y-%m-%d'),
                    'time': h.timestamp.strftime('%H:%M'),
                    'skill': h.new_skill,
                    'reason': h.reason
                })
            
            return data
        finally:
            session.close()
    
    def get_weakest_topics_summary(self, limit: int = 5) -> List[Dict]:
        session = self.db.get_session()
        try:
            topics = session.query(TopicDB).all()
            
            weak_topics = []
            for topic in topics:
                course = self.storage.get_course(topic.course_id)
                
                weakness_score = (100 - topic.skill_level) * topic.weight
                
                weak_topics.append({
                    'topic_name': topic.name,
                    'course_name': course.name,
                    'skill_level': topic.skill_level,
                    'weight': topic.weight,
                    'weakness_score': weakness_score
                })
            
            weak_topics.sort(key=lambda x: x['weakness_score'], reverse=True)
            return weak_topics[:limit]
        finally:
            session.close()
    
    def get_daily_study_time_chart(self, days: int = 7) -> Dict[str, float]:
        session = self.db.get_session()
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            sessions = session.query(StudySessionDB).filter(
                StudySessionDB.start_time >= cutoff,
                StudySessionDB.end_time.isnot(None)
            ).all()
            
            daily_totals = {}
            
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_totals[date] = 0
            
            for s in sessions:
                date_key = s.start_time.strftime('%Y-%m-%d')
                if date_key in daily_totals:
                    daily_totals[date_key] += s.duration_minutes
            
            return daily_totals
        finally:
            session.close()
    
    def print_skill_progress_chart(self, topic_id: int, days: int = 14):
        topic = self.storage.get_topic(topic_id)
        course = self.storage.get_course(topic.course_id)
        data = self.get_skill_over_time(topic_id, days)
        
        if not data:
            print(f"\nNo skill history available for {topic.name}")
            return
        
        print(f"\n{'='*60}")
        print(f"  Skill Progress: {topic.name} ({course.name})")
        print(f"{'='*60}\n")
        
        max_skill = 100
        chart_width = 40
        
        for entry in data[-10:]:
            bar_length = int((entry['skill'] / max_skill) * chart_width)
            bar = '█' * bar_length
            
            print(f"{entry['date']} {entry['time']:>5} │ {bar} {entry['skill']:.1f}% ({entry['reason']})")
        
        print()
    
    def print_weakest_topics_table(self):
        weak_topics = self.get_weakest_topics_summary(5)
        
        if not weak_topics:
            print("\nNo topics available.")
            return
        
        print(f"\n{'='*70}")
        print(f"  Weakest Topics Summary")
        print(f"{'='*70}\n")
        
        print(f"{'Topic':<25} {'Course':<15} {'Skill':>7} {'Weight':>7} {'Score':>7}")
        print("-" * 70)
        
        for item in weak_topics:
            print(f"{item['topic_name']:<25} {item['course_name']:<15} "
                  f"{item['skill_level']:>6.1f}% {item['weight']:>7.2f} {item['weakness_score']:>7.1f}")
        
        print()
    
    def print_study_time_chart(self, days: int = 7):
        daily_totals = self.get_daily_study_time_chart(days)
        
        print(f"\n{'='*60}")
        print(f"  Daily Study Time (Last {days} Days)")
        print(f"{'='*60}\n")
        
        max_minutes = max(daily_totals.values()) if daily_totals.values() else 60
        chart_width = 40
        
        for date in sorted(daily_totals.keys()):
            minutes = daily_totals[date]
            hours = minutes / 60
            
            if max_minutes > 0:
                bar_length = int((minutes / max_minutes) * chart_width)
            else:
                bar_length = 0
            
            bar = '█' * bar_length
            
            print(f"{date} │ {bar} {hours:.1f}h ({minutes:.0f}m)")
        
        print()
