from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService
from app.services.skill_tracking_service import SkillTrackingService
from app.services.quiz_service import QuizService
from app.services.study_session_service import StudySessionService
from app.models.models import Course, Topic, StudySession, TopicPriority, SkillHistory, Quiz, QuizQuestion, QuizAttempt
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
quiz_service = QuizService(storage.db)
study_session_service = StudySessionService(storage.db)

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
    try:
        # Check if course exists
        course = storage.get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Delete all topics first
        topics = storage.get_topics_by_course(course_id)
        for topic in topics:
            storage.delete_topic(topic.id)
        
        # Delete course
        storage.delete_course(course_id)
        return {"message": "Course deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/courses/{course_id}", response_model=Course)
def update_course(course_id: int, course: Course):
    try:
        existing = storage.get_course(course_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course.id = course_id
        updated = storage.update_course(course)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/topics/{topic_id}", response_model=Topic)
def update_topic(topic_id: int, topic: Topic):
    try:
        existing = storage.get_topic(topic_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic.id = topic_id
        updated = storage.update_topic(topic)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/topics/{topic_id}")
def delete_topic(topic_id: int):
    try:
        topic = storage.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        storage.delete_topic(topic_id)
        return {"message": "Topic deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/topics/{topic_id}/skill")
def update_topic_skill(topic_id: int, skill_level: float = Body(..., embed=True)):
    try:
        topic = storage.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        if skill_level < 0 or skill_level > 100:
            raise HTTPException(status_code=400, detail="Skill level must be between 0 and 100")
        
        old_skill = topic.skill_level
        topic.skill_level = skill_level
        updated = storage.update_topic(topic)
        
        # Record in history
        skill_tracking.record_skill_change(topic_id, old_skill, skill_level, "Manual update")
        
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# === Quiz Endpoints ===

class QuizCreateRequest(BaseModel):
    topic_id: int
    title: str
    questions: List[QuizQuestion]

class QuizAttemptRequest(BaseModel):
    answers: Dict[int, str]  # question_id -> answer

@app.post("/quizzes", response_model=Quiz)
def create_quiz(request: QuizCreateRequest):
    try:
        # Validate topic exists
        topic = storage.get_topic(request.topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        quiz = Quiz(
            topic_id=request.topic_id,
            title=request.title,
            created_at=datetime.now(),
            questions=request.questions
        )
        created = quiz_service.create_quiz(quiz)
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/quizzes/{quiz_id}", response_model=Quiz)
def get_quiz(quiz_id: int):
    quiz = quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.get("/topics/{topic_id}/quizzes", response_model=List[Quiz])
def get_topic_quizzes(topic_id: int):
    # Validate topic exists
    topic = storage.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    quizzes = quiz_service.get_quizzes_by_topic(topic_id)
    return quizzes

@app.post("/quizzes/{quiz_id}/attempt", response_model=QuizAttempt)
def attempt_quiz(quiz_id: int, request: QuizAttemptRequest):
    try:
        quiz = quiz_service.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        attempt = quiz_service.submit_attempt(quiz_id, request.answers)
        return attempt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/quizzes/{quiz_id}/attempts", response_model=List[QuizAttempt])
def get_quiz_attempts(quiz_id: int):
    quiz = quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = quiz_service.get_attempts(quiz_id)
    return attempts

@app.get("/topics/{topic_id}/quiz-results")
def get_topic_quiz_results(topic_id: int):
    topic = storage.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    results = quiz_service.get_topic_quiz_summary(topic_id)
    return results

# === Study Session Endpoints ===

@app.post("/study-sessions/start", response_model=StudySession)
def start_study_session(topic_id: int = Body(..., embed=True)):
    try:
        # Validate topic exists
        topic = storage.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Check for active session
        active = study_session_service.get_active_session()
        if active:
            raise HTTPException(status_code=400, detail="There is already an active study session")
        
        session = study_session_service.start_session(topic_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/study-sessions/{session_id}/end", response_model=StudySession)
def end_study_session(session_id: int):
    try:
        session = study_session_service.end_session(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/study-sessions/active", response_model=Optional[StudySession])
def get_active_session():
    return study_session_service.get_active_session()

@app.get("/study-sessions", response_model=List[StudySession])
def get_study_sessions(limit: int = 50):
    return study_session_service.get_all_sessions(limit=limit)

@app.get("/study-sessions/statistics")
def get_study_statistics():
    return study_session_service.get_statistics()

@app.get("/topics/{topic_id}/sessions", response_model=List[StudySession])
def get_topic_sessions(topic_id: int):
    topic = storage.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return study_session_service.get_sessions_by_topic(topic_id)

# === Skill Assessment Endpoint ===

@app.post("/topics/{topic_id}/skill-assessment")
def manual_skill_assessment(topic_id: int, skill_level: float = Body(..., embed=True), reason: str = Body("Manual self-assessment", embed=True)):
    try:
        topic = storage.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        if skill_level < 0 or skill_level > 100:
            raise HTTPException(status_code=400, detail="Skill level must be between 0 and 100")
        
        old_skill = topic.skill_level
        topic.skill_level = skill_level
        updated = storage.update_topic(topic)
        
        # Record in history
        skill_tracking.record_skill_change(topic_id, old_skill, skill_level, reason)
        
        return {
            "topic": updated,
            "previous_skill": old_skill,
            "new_skill": skill_level,
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/skill-decay/apply")
def apply_skill_decay():
    try:
        results = skill_tracking.apply_decay_to_all()
        return {
            "message": "Skill decay applied",
            "topics_affected": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/skill-decay/status")
def get_decay_status():
    try:
        status = skill_tracking.get_decay_eligible_topics()
        return status
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
