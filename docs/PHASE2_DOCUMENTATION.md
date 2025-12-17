# Phase 2 - Skill Tracking & Adaptation

## Overview

Phase 2 adds intelligent skill tracking, quiz-based assessment, adaptive planning, and progress visualization to the Study Planner. The system now learns from user behavior and automatically adjusts study priorities based on performance and engagement.

---

## Features Implemented

### 1. Skill History Tracking (TICKET-201)

**Description**: Extended Topic model to track skill changes over time instead of a single static value.

**Database Schema**:
- `skill_history` table with:
  - `timestamp`: When the change occurred
  - `previous_skill`: Skill level before change
  - `new_skill`: Skill level after change
  - `reason`: Why the change occurred (quiz, self-assessment, decay)

**Usage**:
- All skill updates are automatically logged
- Viewable through option 11: "View Skill History"
- Provides complete audit trail of learning progress

---

### 2. Quiz Engine (TICKET-202)

**Description**: Simple MCQ-based quiz system for evaluating topic knowledge.

**Features**:
- Create quizzes with 5-10 multiple-choice questions
- Auto-scored based on correct answers
- Results stored with timestamps

**Usage**:
- Option 12: Create Quiz for Topic
- Option 13: Take Quiz
- Option 14: View Quiz Results

**Quiz Format**:
- Question text with 4 options (A, B, C, D)
- Single correct answer per question
- Score calculated as percentage correct

---

### 3. Skill Update Algorithm (TICKET-203)

**Description**: Intelligent skill adjustment based on quiz performance and behavior.

**Rules**:
1. **Quiz-based updates**:
   - Score > 50%: Skill increases
   - Score < 50%: Skill decreases
   - Formula: `skill_change = (quiz_score - 50) * 0.3`

2. **Daily caps**:
   - Maximum skill increase: 15 points per day
   - Prevents unrealistic jumps

3. **Self-assessment weight**:
   - Manual assessments have 50% weight vs quiz results
   - Large changes (>20 points) require confirmation

**Behavior**:
- Skill changes are gradual and realistic
- System prioritizes objective quiz data
- Safeguards against gaming the system

---

### 4. Manual Self-Assessment (TICKET-204)

**Description**: Users can manually update their perceived skill level.

**Features**:
- Option 10: Manual Skill Self-Assessment
- Weighted at 50% of quiz-based updates
- Large jumps require user confirmation
- All changes logged in skill history with "self-assessment" reason

**Usage Pattern**:
```
1. Select topic
2. Enter perceived skill level (0-100)
3. System applies 50% weight to the change
4. Confirms if change > 20 points
```

---

### 5. Study Session Tracking (TICKET-205)

**Description**: Track time spent studying each topic.

**Features**:
- Start/stop study sessions
- Automatic duration calculation
- Daily and total time aggregation
- Per-topic time tracking

**Usage**:
- Option 7: Start Study Session
- Option 8: End Study Session
- Option 9: View Study Time Statistics

**Data Collected**:
- Session start/end times
- Duration in minutes
- Associated topic

---

### 6. Skill Decay Logic (TICKET-206)

**Description**: Skills naturally decrease when topics are neglected.

**Decay Rules**:
- No decay if studied within last 7 days
- Decay starts after 7 days of inactivity
- Rate: 0.5 points per day of inactivity
- Maximum decay: 30% of current skill level
- Heavily weighted topics prioritized for study

**Application**:
- Option 17: Apply Skill Decay
- Recommended to run weekly
- All decay events logged in skill history

---

### 7. Weak Topic Detection (TICKET-207)

**Description**: Automatically identify topics needing attention.

**Detection Criteria**:
- Low skill level (< 70%)
- High exam weight
- Long inactivity period

**Urgency Score Formula**:
```
urgency = (100 - skill_level) * weight * 2 + min(days_inactive, 30) * 0.5
```

**Usage**:
- Option 6: View Weak Topics
- Shows top topics sorted by urgency
- Displays skill level, weight, and inactivity days

---

### 8. Adaptive Priority Recalculation (TICKET-208)

**Description**: Dynamic priority adjustment based on learning trends.

**Adaptive Factors**:

1. **Skill Trend**:
   - Declining skill → +30% priority boost
   - Slightly declining → +10% boost
   - Rapidly improving → -20% priority reduction

2. **Study Time Balance**:
   - Over-studied (>5 hours/week) → -10% priority
   - Under-studied (<1 hour/week) → +20% priority

3. **Inactivity Penalty**:
   - Topics not studied recently get priority boost

**Usage**:
- Option 5: Generate Daily Study Plan
- System asks: "Use adaptive planning? (y/n)"
- Adaptive mode enabled by default

---

### 9. Progress Visualization (TICKET-209)

**Description**: Visual feedback of learning progress.

**Available Views**:

1. **Skill Progress Chart** (Option 15):
   - Line chart showing skill changes over time
   - Color-coded by reason (quiz, self-assessment, decay)
   - Last 10 entries displayed

2. **Daily Study Time Chart** (Option 15):
   - Bar chart of study hours per day
   - Last 7 days displayed
   - Total minutes and hours shown

3. **Weakest Topics Summary** (Option 16):
   - Table view of 5 weakest topics
   - Shows skill, weight, and weakness score
   - Sorted by urgency

**Statistics Available** (Option 9):
- Daily breakdown of study time
- Total time per topic
- All-time totals

---

## New CLI Menu Structure

```
=================================================
  SKILL-AWARE STUDY PLANNER
=================================================

--- Course & Topic Management ---
1. Add Course
2. Add Topic to Course
3. View All Courses
4. View Topics for Course

--- Study Planning ---
5. Generate Daily Study Plan
6. View Weak Topics

--- Study Sessions ---
7. Start Study Session
8. End Study Session
9. View Study Time Statistics

--- Skill Tracking ---
10. Manual Skill Self-Assessment
11. View Skill History

--- Quizzes ---
12. Create Quiz for Topic
13. Take Quiz
14. View Quiz Results

--- Progress & Analytics ---
15. View Progress Charts
16. View Weakest Topics Summary

--- System ---
17. Apply Skill Decay
18. Exit
```

---

## Database Schema Updates

### New Tables

1. **skill_history**
   - id, topic_id, timestamp, previous_skill, new_skill, reason

2. **study_sessions**
   - id, topic_id, start_time, end_time, duration_minutes

3. **quizzes**
   - id, topic_id, title, created_at

4. **quiz_questions**
   - id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer

5. **quiz_attempts**
   - id, quiz_id, attempted_at, score, total_questions

---

## Workflow Examples

### Example 1: Taking a Quiz and Updating Skill

```
1. User selects "13. Take Quiz"
2. Chooses topic and quiz
3. Answers all questions
4. System calculates score
5. Skill automatically updated based on performance
6. Change logged in skill history
```

### Example 2: Adaptive Study Planning

```
1. User studies Topic A extensively (high time spent)
2. User neglects Topic B (high weight, low skill)
3. User takes quiz on Topic C and performs poorly
4. Next daily plan generation:
   - Topic A priority reduced (over-studied)
   - Topic B priority increased (weak + important)
   - Topic C priority increased (declining skill)
```

### Example 3: Skill Decay Detection

```
1. User hasn't studied Topic X for 14 days
2. System runs "17. Apply Skill Decay"
3. Topic X skill reduced by ~7 points (0.5 * 14 days)
4. Change logged as "decay" in skill history
5. Topic X appears in weak topics list
6. Gets priority boost in next study plan
```

---

## Configuration Parameters

Located in service classes, easily adjustable:

**SkillTrackingService**:
- `max_skill_increase_per_day`: 15.0 points
- `self_assessment_weight`: 0.5 (50%)
- `quiz_weight`: 1.0 (100%)
- `decay_start_days`: 7 days
- `decay_rate_per_day`: 0.5 points

**PlannerService**:
- Skill trend thresholds: -5, 0, +10
- Priority multipliers: 0.8x to 1.3x
- Study time thresholds: 60 min, 300 min

---

## Technical Architecture

### Service Layer Structure

```
app/
├── services/
│   ├── planner_service.py          # Study plan generation + adaptive logic
│   ├── quiz_service.py             # Quiz CRUD and scoring
│   ├── skill_tracking_service.py   # Skill updates and decay
│   ├── study_session_service.py    # Time tracking
│   └── progress_service.py         # Visualization and analytics
```

### Data Flow

```
User Action → Service Layer → Database Layer → Skill History
                ↓
          Priority Calculation
                ↓
          Adaptive Planner
                ↓
          Updated Study Plan
```

---

## Future Enhancements

Ideas for Phase 3+:

1. **Machine Learning Integration**:
   - Predict optimal study times
   - Personalized decay rates
   - Intelligent question difficulty adjustment

2. **Spaced Repetition**:
   - Integrate SRS algorithm
   - Automatic review scheduling

3. **Collaboration Features**:
   - Share quizzes between users
   - Study groups
   - Leaderboards

4. **Advanced Analytics**:
   - Skill trajectory predictions
   - Exam readiness scoring
   - Study efficiency metrics

---

## Phase 2 Definition of Done

✅ Skills change based on quizzes and study behavior  
✅ Planner adapts automatically to performance  
✅ Weak topics are detected reliably  
✅ Skill decay is active and configurable  
✅ Progress is visible through multiple views  
✅ All features integrated into CLI  
✅ Documentation complete  

---

## Converting to React GUI

**Yes, this application can be converted to a React GUI!**

### Architecture Considerations:

1. **Backend API** (Recommended approach):
   - Convert services to REST API endpoints using FastAPI or Flask
   - Keep all business logic in service layer
   - React frontend communicates via HTTP

2. **File Structure**:
```
project/
├── backend/
│   ├── app/              # Existing Python code
│   ├── api/              # New API endpoints
│   └── main.py           # FastAPI/Flask app
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API client
│   │   └── App.jsx
│   └── package.json
```

3. **Key API Endpoints Needed**:
   - POST /courses, GET /courses
   - POST /topics, GET /topics
   - POST /quizzes, GET /quizzes, POST /quizzes/:id/attempt
   - POST /study-sessions/start, POST /study-sessions/end
   - GET /study-plan
   - GET /weak-topics
   - GET /progress/skill-history/:topicId
   - POST /skill-assessment

4. **React Components**:
   - Dashboard (overview)
   - CourseList, TopicList
   - StudyPlanView
   - QuizTaker, QuizCreator
   - SkillProgressChart (using Chart.js or Recharts)
   - StudySessionTimer
   - WeakTopicsAlert

5. **State Management**:
   - Use React Context or Redux for global state
   - React Query for API data fetching/caching

6. **Migration Strategy**:
   - Phase 1: Create FastAPI wrapper around existing services
   - Phase 2: Build React components page by page
   - Phase 3: Add real-time features (WebSocket for timer)
   - Phase 4: Progressive Web App (PWA) for mobile

### Example FastAPI Endpoint:

```python
from fastapi import FastAPI
from app.services.planner_service import PlannerService

app = FastAPI()

@app.get("/api/study-plan")
def get_study_plan(hours: float, adaptive: bool = True):
    storage = StorageService()
    planner = PlannerService(storage)
    plan = planner.generate_daily_plan(hours, adaptive=adaptive)
    return plan.model_dump()
```

### Example React Component:

```jsx
function StudyPlan() {
  const [hours, setHours] = useState(4);
  const { data: plan } = useQuery(['studyPlan', hours], 
    () => fetch(`/api/study-plan?hours=${hours}`).then(r => r.json())
  );
  
  return (
    <div>
      <input type="number" value={hours} onChange={e => setHours(e.target.value)} />
      {plan?.allocated_topics.map(item => (
        <StudyPlanItem key={item.topic.id} {...item} />
      ))}
    </div>
  );
}
```

**Conclusion**: The current architecture is well-suited for conversion to a React GUI. The clean separation between business logic (services) and interface (CLI) makes it straightforward to replace the CLI with a web frontend.
