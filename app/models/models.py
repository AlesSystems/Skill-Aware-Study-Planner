from datetime import datetime
from typing import Optional
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
