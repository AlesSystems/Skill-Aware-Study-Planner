from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

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
    skill_history = relationship("SkillHistoryDB", back_populates="topic", cascade="all, delete-orphan")
    study_sessions = relationship("StudySessionDB", back_populates="topic", cascade="all, delete-orphan")
    quizzes = relationship("QuizDB", back_populates="topic", cascade="all, delete-orphan")


class SkillHistoryDB(Base):
    __tablename__ = 'skill_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    previous_skill = Column(Float, nullable=False)
    new_skill = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    
    topic = relationship("TopicDB", back_populates="skill_history")


class StudySessionDB(Base):
    __tablename__ = 'study_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    
    topic = relationship("TopicDB", back_populates="study_sessions")


class QuizDB(Base):
    __tablename__ = 'quizzes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    topic = relationship("TopicDB", back_populates="quizzes")
    questions = relationship("QuizQuestionDB", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttemptDB", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestionDB(Base):
    __tablename__ = 'quiz_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    
    quiz = relationship("QuizDB", back_populates="questions")


class QuizAttemptDB(Base):
    __tablename__ = 'quiz_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    attempted_at = Column(DateTime, nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    
    quiz = relationship("QuizDB", back_populates="attempts")


class TopicDependencyDB(Base):
    __tablename__ = 'topic_dependencies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prerequisite_topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    dependent_topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    min_skill_threshold = Column(Float, default=70.0)


class DecisionLogDB(Base):
    __tablename__ = 'decision_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    decision_type = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=True)
    explanation = Column(Text, nullable=False)
    meta_data = Column(Text, nullable=True)


class Database:
    def __init__(self, db_path: str = "study_planner.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
