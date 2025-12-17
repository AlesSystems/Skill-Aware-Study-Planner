# Converting Skill-Aware Study Planner to React GUI

This guide provides a step-by-step approach to convert the CLI-based Study Planner into a modern React web application.

---

## Architecture Overview

### Current Architecture
```
CLI → Services → Storage → Database
```

### Target Architecture
```
React Frontend → REST API → Services → Storage → Database
```

---

## Phase 1: Backend API Setup

### Step 1: Install FastAPI Dependencies

Add to `requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic[email]==2.5.3
```

### Step 2: Create API Structure

```
project/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── courses.py
│   │   ├── topics.py
│   │   ├── quizzes.py
│   │   ├── study_sessions.py
│   │   ├── planner.py
│   │   └── analytics.py
│   └── dependencies.py      # Shared dependencies
└── app/                     # Existing code
```

### Step 3: Create FastAPI Application

**api/main.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import courses, topics, quizzes, study_sessions, planner, analytics

app = FastAPI(
    title="Skill-Aware Study Planner API",
    description="Intelligent adaptive study planning system",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["quizzes"])
app.include_router(study_sessions.router, prefix="/api/study-sessions", tags=["study_sessions"])
app.include_router(planner.router, prefix="/api/planner", tags=["planner"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
def root():
    return {"message": "Skill-Aware Study Planner API", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 4: Create API Endpoints

**api/routes/courses.py**:
```python
from fastapi import APIRouter, HTTPException
from typing import List
from app.storage.storage_service import StorageService
from app.models.models import Course

router = APIRouter()

def get_storage():
    return StorageService()

@router.post("/", response_model=Course)
def create_course(course: Course):
    storage = get_storage()
    return storage.create_course(course)

@router.get("/", response_model=List[Course])
def get_courses():
    storage = get_storage()
    return storage.get_all_courses()

@router.get("/{course_id}", response_model=Course)
def get_course(course_id: int):
    storage = get_storage()
    course = storage.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.delete("/{course_id}")
def delete_course(course_id: int):
    storage = get_storage()
    success = storage.delete_course(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}
```

**api/routes/planner.py**:
```python
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from app.storage.storage_service import StorageService
from app.services.planner_service import PlannerService

router = APIRouter()

class PlanRequest(BaseModel):
    available_hours: float
    adaptive: bool = True

@router.post("/daily-plan")
def generate_daily_plan(request: PlanRequest):
    storage = StorageService()
    planner = PlannerService(storage)
    plan = planner.generate_daily_plan(request.available_hours, adaptive=request.adaptive)
    
    return {
        "daily_hours": plan.daily_hours,
        "total_allocated_hours": plan.get_total_allocated_hours(),
        "topics": [
            {
                "topic": item['topic'].model_dump(),
                "course": item['course'].model_dump(),
                "priority_score": item['priority_score'],
                "urgency_factor": item['urgency_factor'],
                "allocated_hours": item['allocated_hours']
            }
            for item in plan.allocated_topics
        ]
    }

@router.get("/weak-topics")
def get_weak_topics():
    storage = StorageService()
    planner = PlannerService(storage)
    weak_topics = planner.detect_weak_topics()
    
    return [
        {
            "topic": item['topic'].model_dump(),
            "course": item['course'].model_dump(),
            "urgency_score": item['urgency_score'],
            "days_inactive": item['days_inactive']
        }
        for item in weak_topics
    ]
```

**api/routes/quizzes.py**:
```python
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.storage.storage_service import StorageService
from app.services.quiz_service import QuizService
from app.services.skill_tracking_service import SkillTrackingService
from app.models.models import Quiz, QuizAttempt

router = APIRouter()

@router.post("/", response_model=Quiz)
def create_quiz(quiz: Quiz):
    storage = StorageService()
    quiz_service = QuizService(storage.db)
    return quiz_service.create_quiz(quiz)

@router.get("/topic/{topic_id}", response_model=List[Quiz])
def get_quizzes_by_topic(topic_id: int):
    storage = StorageService()
    quiz_service = QuizService(storage.db)
    return quiz_service.get_quizzes_by_topic(topic_id)

@router.get("/{quiz_id}", response_model=Quiz)
def get_quiz(quiz_id: int):
    storage = StorageService()
    quiz_service = QuizService(storage.db)
    quiz = quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/{quiz_id}/attempt", response_model=QuizAttempt)
def submit_quiz_attempt(quiz_id: int, answers: Dict[int, str]):
    storage = StorageService()
    quiz_service = QuizService(storage.db)
    skill_tracking = SkillTrackingService(storage.db)
    
    attempt = quiz_service.submit_quiz_attempt(quiz_id, answers)
    
    # Update skill based on quiz performance
    quiz = quiz_service.get_quiz(quiz_id)
    skill_tracking.update_skill_from_quiz(quiz.topic_id, attempt.score)
    
    return attempt

@router.get("/{quiz_id}/attempts", response_model=List[QuizAttempt])
def get_quiz_attempts(quiz_id: int):
    storage = StorageService()
    quiz_service = QuizService(storage.db)
    return quiz_service.get_quiz_attempts(quiz_id)
```

### Step 5: Run Backend API

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api/main.py

# Or with uvicorn directly
uvicorn api.main:app --reload --port 8000
```

API will be available at: http://localhost:8000  
Interactive docs at: http://localhost:8000/docs

---

## Phase 2: React Frontend Setup

### Step 1: Create React App

```bash
npx create-react-app study-planner-frontend
cd study-planner-frontend
```

### Step 2: Install Dependencies

```bash
npm install axios react-router-dom
npm install @mui/material @emotion/react @emotion/styled
npm install recharts  # For charts
npm install react-query  # For API state management
npm install date-fns  # For date formatting
```

### Step 3: Project Structure

```
study-planner-frontend/
├── public/
├── src/
│   ├── api/
│   │   └── client.js           # Axios instance
│   ├── components/
│   │   ├── common/
│   │   │   ├── Navbar.jsx
│   │   │   └── Layout.jsx
│   │   ├── courses/
│   │   │   ├── CourseList.jsx
│   │   │   ├── CourseForm.jsx
│   │   │   └── CourseCard.jsx
│   │   ├── topics/
│   │   │   ├── TopicList.jsx
│   │   │   ├── TopicForm.jsx
│   │   │   └── TopicCard.jsx
│   │   ├── planner/
│   │   │   ├── StudyPlan.jsx
│   │   │   ├── PlanConfig.jsx
│   │   │   └── WeakTopics.jsx
│   │   ├── quizzes/
│   │   │   ├── QuizList.jsx
│   │   │   ├── QuizCreator.jsx
│   │   │   ├── QuizTaker.jsx
│   │   │   └── QuizResults.jsx
│   │   ├── sessions/
│   │   │   ├── SessionTimer.jsx
│   │   │   └── SessionHistory.jsx
│   │   └── analytics/
│   │       ├── SkillProgressChart.jsx
│   │       ├── StudyTimeChart.jsx
│   │       └── Dashboard.jsx
│   ├── hooks/
│   │   ├── useCourses.js
│   │   ├── useTopics.js
│   │   ├── useQuizzes.js
│   │   └── useStudySessions.js
│   ├── pages/
│   │   ├── HomePage.jsx
│   │   ├── CoursesPage.jsx
│   │   ├── PlannerPage.jsx
│   │   ├── QuizzesPage.jsx
│   │   └── AnalyticsPage.jsx
│   ├── App.jsx
│   └── index.js
└── package.json
```

### Step 4: API Client Setup

**src/api/client.js**:
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const coursesAPI = {
  getAll: () => apiClient.get('/courses'),
  getById: (id) => apiClient.get(`/courses/${id}`),
  create: (data) => apiClient.post('/courses', data),
  delete: (id) => apiClient.delete(`/courses/${id}`),
};

export const topicsAPI = {
  getAll: () => apiClient.get('/topics'),
  getById: (id) => apiClient.get(`/topics/${id}`),
  getByCourse: (courseId) => apiClient.get(`/topics/course/${courseId}`),
  create: (data) => apiClient.post('/topics', data),
};

export const plannerAPI = {
  generateDailyPlan: (hours, adaptive = true) => 
    apiClient.post('/planner/daily-plan', { available_hours: hours, adaptive }),
  getWeakTopics: () => apiClient.get('/planner/weak-topics'),
};

export const quizzesAPI = {
  getByTopic: (topicId) => apiClient.get(`/quizzes/topic/${topicId}`),
  getById: (id) => apiClient.get(`/quizzes/${id}`),
  create: (data) => apiClient.post('/quizzes', data),
  submitAttempt: (quizId, answers) => 
    apiClient.post(`/quizzes/${quizId}/attempt`, answers),
  getAttempts: (quizId) => apiClient.get(`/quizzes/${quizId}/attempts`),
};

export default apiClient;
```

### Step 5: React Query Hooks

**src/hooks/useCourses.js**:
```javascript
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { coursesAPI } from '../api/client';

export const useCourses = () => {
  return useQuery('courses', () => coursesAPI.getAll().then(res => res.data));
};

export const useCreateCourse = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    (courseData) => coursesAPI.create(courseData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
      },
    }
  );
};

export const useDeleteCourse = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    (courseId) => coursesAPI.delete(courseId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
      },
    }
  );
};
```

### Step 6: Key React Components

**src/components/planner/StudyPlan.jsx**:
```javascript
import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { plannerAPI } from '../../api/client';
import { Card, CardContent, Typography, Slider, Button, CircularProgress } from '@mui/material';

function StudyPlan() {
  const [hours, setHours] = useState(4);
  const [adaptive, setAdaptive] = useState(true);
  const [shouldFetch, setShouldFetch] = useState(false);

  const { data: plan, isLoading, error } = useQuery(
    ['studyPlan', hours, adaptive],
    () => plannerAPI.generateDailyPlan(hours, adaptive).then(res => res.data),
    { enabled: shouldFetch }
  );

  const handleGenerate = () => {
    setShouldFetch(true);
  };

  if (error) return <div>Error loading study plan</div>;

  return (
    <div>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Configure Your Study Plan
          </Typography>
          
          <Typography gutterBottom>
            Available Hours: {hours}
          </Typography>
          <Slider
            value={hours}
            onChange={(e, value) => setHours(value)}
            min={1}
            max={12}
            step={0.5}
            marks
          />
          
          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Generate Plan'}
          </Button>
        </CardContent>
      </Card>

      {plan && (
        <div>
          <Typography variant="h5" gutterBottom>
            Your Study Plan
          </Typography>
          
          {plan.topics.map((item, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6">
                  {item.topic.name}
                </Typography>
                <Typography color="text.secondary">
                  {item.course.name}
                </Typography>
                <Typography>
                  Current Skill: {item.topic.skill_level}%
                </Typography>
                <Typography>
                  Study Time: {item.allocated_hours.toFixed(1)} hours
                </Typography>
                <Typography variant="caption">
                  Priority Score: {item.priority_score.toFixed(3)}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default StudyPlan;
```

**src/components/quizzes/QuizTaker.jsx**:
```javascript
import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { quizzesAPI } from '../../api/client';
import { 
  Card, CardContent, Typography, Radio, RadioGroup, 
  FormControlLabel, Button, Alert 
} from '@mui/material';

function QuizTaker({ quizId, onComplete }) {
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);

  const { data: quiz, isLoading } = useQuery(
    ['quiz', quizId],
    () => quizzesAPI.getById(quizId).then(res => res.data)
  );

  const submitMutation = useMutation(
    () => quizzesAPI.submitAttempt(quizId, answers),
    {
      onSuccess: (data) => {
        setShowResults(true);
        if (onComplete) onComplete(data.data);
      },
    }
  );

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = () => {
    if (Object.keys(answers).length === quiz.questions.length) {
      submitMutation.mutate();
    }
  };

  if (isLoading) return <div>Loading quiz...</div>;
  if (!quiz) return <div>Quiz not found</div>;

  if (showResults) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Quiz Complete!
          </Typography>
          <Typography variant="h6">
            Score: {submitMutation.data.data.score.toFixed(1)}%
          </Typography>
          <Typography>
            Your skill level has been updated!
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        {quiz.title}
      </Typography>

      {quiz.questions.map((question, index) => (
        <Card key={question.id} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Question {index + 1}: {question.question_text}
            </Typography>
            
            <RadioGroup
              value={answers[question.id] || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            >
              <FormControlLabel value="A" control={<Radio />} label={`A) ${question.option_a}`} />
              <FormControlLabel value="B" control={<Radio />} label={`B) ${question.option_b}`} />
              <FormControlLabel value="C" control={<Radio />} label={`C) ${question.option_c}`} />
              <FormControlLabel value="D" control={<Radio />} label={`D) ${question.option_d}`} />
            </RadioGroup>
          </CardContent>
        </Card>
      ))}

      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={Object.keys(answers).length !== quiz.questions.length}
        fullWidth
      >
        Submit Quiz
      </Button>
    </div>
  );
}

export default QuizTaker;
```

**src/components/analytics/SkillProgressChart.jsx**:
```javascript
import React from 'react';
import { useQuery } from 'react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { analyticsAPI } from '../../api/client';

function SkillProgressChart({ topicId }) {
  const { data: skillHistory } = useQuery(
    ['skillHistory', topicId],
    () => analyticsAPI.getSkillHistory(topicId).then(res => res.data)
  );

  if (!skillHistory) return null;

  return (
    <LineChart width={600} height={300} data={skillHistory}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis domain={[0, 100]} />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="skill" stroke="#8884d8" name="Skill Level" />
    </LineChart>
  );
}

export default SkillProgressChart;
```

### Step 7: Main App Component

**src/App.jsx**:
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import Navbar from './components/common/Navbar';
import HomePage from './pages/HomePage';
import CoursesPage from './pages/CoursesPage';
import PlannerPage from './pages/PlannerPage';
import QuizzesPage from './pages/QuizzesPage';
import AnalyticsPage from './pages/AnalyticsPage';

const queryClient = new QueryClient();
const theme = createTheme();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/planner" element={<PlannerPage />} />
            <Route path="/quizzes" element={<QuizzesPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

## Phase 3: Running the Full Stack

### Terminal 1: Backend API
```bash
cd /path/to/project
python api/main.py
# API runs on http://localhost:8000
```

### Terminal 2: React Frontend
```bash
cd study-planner-frontend
npm start
# React app runs on http://localhost:3000
```

---

## Additional Features for Web Version

1. **Real-time Study Timer**: WebSocket connection for live timer updates
2. **Notifications**: Browser notifications for study reminders
3. **PWA**: Progressive Web App for mobile access
4. **Dark Mode**: Theme switcher
5. **Data Export**: Download study history as CSV/PDF
6. **Keyboard Shortcuts**: Power user features

---

## Deployment

### Backend (FastAPI)
- **Heroku**: `heroku create` + Procfile
- **Railway**: One-click deploy
- **AWS Lambda**: Serverless with Mangum

### Frontend (React)
- **Vercel**: Connected to GitHub repo
- **Netlify**: Drag & drop or GitHub integration
- **GitHub Pages**: Static hosting

### Database
- **PostgreSQL**: Replace SQLite for production
- **Supabase**: Managed PostgreSQL + Auth

---

## Summary

The conversion is straightforward because:
1. ✅ Business logic is separated in service classes
2. ✅ Data models use Pydantic (FastAPI native)
3. ✅ No UI dependencies in core code
4. ✅ Clean API boundaries

Total conversion time: **2-3 weeks** for a functional MVP web app.
