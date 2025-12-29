from typing import List, Optional
from datetime import datetime
from app.storage.database import Database, CourseDB, TopicDB
from app.models.models import Course, Topic


class StorageService:
    def __init__(self, db_path: str = "study_planner.db"):
        self.db = Database(db_path)
    
    def create_course(self, course: Course) -> Course:
        session = self.db.get_session()
        try:
            db_course = CourseDB(
                name=course.name,
                exam_date=course.exam_date
            )
            session.add(db_course)
            session.commit()
            session.refresh(db_course)
            course.id = db_course.id
            return course
        finally:
            session.close()
    
    def get_course(self, course_id: int) -> Optional[Course]:
        session = self.db.get_session()
        try:
            db_course = session.query(CourseDB).filter(CourseDB.id == course_id).first()
            if db_course:
                return Course(
                    id=db_course.id,
                    name=db_course.name,
                    exam_date=db_course.exam_date
                )
            return None
        finally:
            session.close()
    
    def get_all_courses(self) -> List[Course]:
        session = self.db.get_session()
        try:
            db_courses = session.query(CourseDB).all()
            return [
                Course(
                    id=db_course.id,
                    name=db_course.name,
                    exam_date=db_course.exam_date
                ) for db_course in db_courses
            ]
        finally:
            session.close()
    
    def create_topic(self, topic: Topic) -> Topic:
        session = self.db.get_session()
        try:
            db_topic = TopicDB(
                course_id=topic.course_id,
                name=topic.name,
                weight=topic.weight,
                skill_level=topic.skill_level
            )
            session.add(db_topic)
            session.commit()
            session.refresh(db_topic)
            topic.id = db_topic.id
            return topic
        finally:
            session.close()
    
    def get_topic(self, topic_id: int) -> Optional[Topic]:
        session = self.db.get_session()
        try:
            db_topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if db_topic:
                return Topic(
                    id=db_topic.id,
                    course_id=db_topic.course_id,
                    name=db_topic.name,
                    weight=db_topic.weight,
                    skill_level=db_topic.skill_level
                )
            return None
        finally:
            session.close()
    
    def get_topics_by_course(self, course_id: int) -> List[Topic]:
        session = self.db.get_session()
        try:
            db_topics = session.query(TopicDB).filter(TopicDB.course_id == course_id).all()
            return [
                Topic(
                    id=db_topic.id,
                    course_id=db_topic.course_id,
                    name=db_topic.name,
                    weight=db_topic.weight,
                    skill_level=db_topic.skill_level
                ) for db_topic in db_topics
            ]
        finally:
            session.close()
    
    def get_all_topics(self) -> List[Topic]:
        session = self.db.get_session()
        try:
            db_topics = session.query(TopicDB).all()
            return [
                Topic(
                    id=db_topic.id,
                    course_id=db_topic.course_id,
                    name=db_topic.name,
                    weight=db_topic.weight,
                    skill_level=db_topic.skill_level
                ) for db_topic in db_topics
            ]
        finally:
            session.close()
    
    def update_topic_skill(self, topic_id: int, new_skill_level: float) -> bool:
        session = self.db.get_session()
        try:
            db_topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if db_topic:
                db_topic.skill_level = new_skill_level
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def update_course(self, course: Course) -> Course:
        session = self.db.get_session()
        try:
            db_course = session.query(CourseDB).filter(CourseDB.id == course.id).first()
            if db_course:
                db_course.name = course.name
                db_course.exam_date = course.exam_date
                session.commit()
                session.refresh(db_course)
                return Course(
                    id=db_course.id,
                    name=db_course.name,
                    exam_date=db_course.exam_date
                )
            raise ValueError("Course not found")
        finally:
            session.close()
    
    def update_topic(self, topic: Topic) -> Topic:
        session = self.db.get_session()
        try:
            db_topic = session.query(TopicDB).filter(TopicDB.id == topic.id).first()
            if db_topic:
                db_topic.course_id = topic.course_id
                db_topic.name = topic.name
                db_topic.weight = topic.weight
                db_topic.skill_level = topic.skill_level
                session.commit()
                session.refresh(db_topic)
                return Topic(
                    id=db_topic.id,
                    course_id=db_topic.course_id,
                    name=db_topic.name,
                    weight=db_topic.weight,
                    skill_level=db_topic.skill_level
                )
            raise ValueError("Topic not found")
        finally:
            session.close()
    
    def delete_topic(self, topic_id: int) -> bool:
        session = self.db.get_session()
        try:
            db_topic = session.query(TopicDB).filter(TopicDB.id == topic_id).first()
            if db_topic:
                session.delete(db_topic)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def delete_course(self, course_id: int) -> bool:
        session = self.db.get_session()
        try:
            db_course = session.query(CourseDB).filter(CourseDB.id == course_id).first()
            if db_course:
                session.delete(db_course)
                session.commit()
                return True
            return False
        finally:
            session.close()
