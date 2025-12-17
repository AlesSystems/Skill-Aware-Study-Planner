from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class Course(BaseModel):
    id: Optional[int] = None
    name: str
    exam_date: datetime
    
    @field_validator('exam_date')
    @classmethod
    def exam_date_must_be_future(cls, v):
        if v < datetime.now():
            raise ValueError('Exam date must be in the future')
        return v


class Topic(BaseModel):
    id: Optional[int] = None
    course_id: int
    name: str
    weight: float = Field(ge=0, le=1)
    skill_level: float = Field(ge=0, le=100)
    
    @field_validator('weight')
    @classmethod
    def weight_must_be_valid(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Weight must be between 0 and 1')
        return v
    
    @field_validator('skill_level')
    @classmethod
    def skill_level_must_be_valid(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Skill level must be between 0 and 100')
        return v


class TopicPriority(BaseModel):
    topic: Topic
    course: Course
    priority_score: float
    urgency_factor: float


class SkillHistory(BaseModel):
    id: Optional[int] = None
    topic_id: int
    timestamp: datetime
    previous_skill: float
    new_skill: float
    reason: str


class StudySession(BaseModel):
    id: Optional[int] = None
    topic_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None


class QuizQuestion(BaseModel):
    id: Optional[int] = None
    quiz_id: Optional[int] = None
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    
    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v):
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('Correct answer must be A, B, C, or D')
        return v


class Quiz(BaseModel):
    id: Optional[int] = None
    topic_id: int
    title: str
    created_at: datetime
    questions: List[QuizQuestion] = []


class QuizAttempt(BaseModel):
    id: Optional[int] = None
    quiz_id: int
    attempted_at: datetime
    score: float
    total_questions: int
