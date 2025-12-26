from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService
from app.services.skill_tracking_service import SkillTrackingService
from app.models.models import Course, Topic, StudySession, TopicPriority, SkillHistory
from pydantic import BaseModel

app = FastAPI(title="Skill-Aware Study Planner API")

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
storage = StorageService()
planner = PlannerService(storage)
skill_tracking = SkillTrackingService(storage.db)

# --- Response Models ---
class AllocatedTopic(BaseModel):
    topic: Topic
    course: Course
    priority_score: float
    urgency_factor: float
    allocated_hours: float

class StudyPlanResponse(BaseModel):
    daily_hours: float
    allocated_topics: List[AllocatedTopic]

class WeakTopic(BaseModel):
    topic: Topic
    course: Course
    days_inactive: int
    urgency_score: float

# --- Endpoints ---

@app.get("/courses", response_model=List[Course])
def get_courses():
    return storage.get_all_courses()

@app.post("/courses", response_model=Course)
def create_course(course: Course):
    try:
        return storage.create_course(course)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/courses/{course_id}/topics", response_model=List[Topic])
def get_course_topics(course_id: int):
    return storage.get_topics_by_course(course_id)

@app.post("/topics", response_model=Topic)
def create_topic(topic: Topic):
    try:
        # Validate course exists
        if not storage.get_course(topic.course_id):
             raise HTTPException(status_code=404, detail="Course not found")
        
        created_topic = storage.create_topic(topic)
        return created_topic
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/topics/{topic_id}", response_model=Topic)
def get_topic(topic_id: int):
    topic = storage.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@app.get("/topics/{topic_id}/history", response_model=List[SkillHistory])
def get_topic_history(topic_id: int):
    return skill_tracking.get_skill_history(topic_id, limit=30)

@app.post("/plan", response_model=StudyPlanResponse)
def generate_plan(hours: float = Body(..., embed=True), adaptive: bool = Body(False, embed=True)):
    try:
        plan = planner.generate_daily_plan(hours, adaptive=adaptive)
        return {
            "daily_hours": plan.daily_hours,
            "allocated_topics": plan.allocated_topics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics/weak-topics", response_model=List[WeakTopic])
def get_weak_topics():
    weak_topics = planner.detect_weak_topics()
    result = []
    for item in weak_topics:
        result.append({
            "topic": item['topic'],
            "course": item['course'],
            "days_inactive": item['days_inactive'],
            "urgency_score": item['urgency_score']
        })
    return result

@app.get("/analytics/expected-scores")
def get_expected_scores():
    return planner.get_expected_scores()

@app.get("/analytics/risks")
def get_risks():
    return planner.identify_risks()

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.get("/health")
def health_check():
    return {"status": "ok"}
