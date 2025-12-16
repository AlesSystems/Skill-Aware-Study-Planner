from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class CourseDB(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    exam_date = Column(DateTime, nullable=False)
    
    topics = relationship("TopicDB", back_populates="course", cascade="all, delete-orphan")


class TopicDB(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    skill_level = Column(Float, nullable=False)
    
    course = relationship("CourseDB", back_populates="topics")


class Database:
    def __init__(self, db_path: str = "study_planner.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
