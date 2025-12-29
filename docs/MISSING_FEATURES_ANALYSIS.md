# Missing Features Analysis

## Executive Summary

This document provides a comprehensive analysis of missing features in the Skill-Aware Study Planner application. While Phases 1-5 are documented as complete, there are significant gaps between the backend services (which are fully implemented) and the frontend UI/API endpoints.

## Critical Missing Features

### 1. Backend API Endpoints Missing

#### Quiz System (Phase 2)
- ❌ `POST /quizzes` - Create a quiz for a topic
- ❌ `GET /quizzes/{quiz_id}` - Get quiz details
- ❌ `GET /topics/{topic_id}/quizzes` - List quizzes for a topic
- ❌ `POST /quizzes/{quiz_id}/attempt` - Submit quiz answers and get score
- ❌ `GET /quizzes/{quiz_id}/attempts` - View quiz attempt history
- ❌ `GET /topics/{topic_id}/quiz-results` - Get quiz results summary

**Impact**: Users cannot create or take quizzes through the web UI, which is a core Phase 2 feature.

#### Study Session Tracking (Phase 2)
- ❌ `POST /study-sessions/start` - Start a study session for a topic
- ❌ `POST /study-sessions/{session_id}/end` - End an active study session
- ❌ `GET /study-sessions/active` - Get currently active study session
- ❌ `GET /study-sessions` - Get study session history
- ❌ `GET /study-sessions/statistics` - Get study time statistics
- ❌ `GET /topics/{topic_id}/sessions` - Get sessions for a specific topic

**Impact**: Users cannot track study time through the web UI, which is essential for adaptive planning and fake productivity detection.

#### Skill Tracking (Phase 2)
- ❌ `POST /topics/{topic_id}/skill-assessment` - Manual skill self-assessment
- ❌ `POST /skill-decay/apply` - Apply skill decay to all topics
- ❌ `GET /skill-decay/status` - Check which topics are eligible for decay

**Impact**: Users cannot manually update skills or apply decay through the web UI.

#### Phase 4: Honesty & Reality Check System
- ❌ `GET /honesty/fake-productivity/{topic_id}` - Detect fake productivity for a topic
- ❌ `GET /honesty/avoidance-patterns` - Get avoidance pattern analysis
- ❌ `GET /honesty/overconfidence/{topic_id}` - Detect overconfidence
- ❌ `GET /honesty/warnings` - Get all honesty warnings
- ❌ `POST /honesty/brutal-mode/toggle` - Toggle brutal honesty mode
- ❌ `GET /honesty/brutal-mode/status` - Get brutal honesty mode status
- ❌ `GET /exam-simulation/{course_id}` - Simulate exam for a course
- ❌ `GET /exam-simulation/{course_id}/motivation-reality` - Get motivation vs reality dashboard
- ❌ `GET /reprioritization/check` - Check for forced re-prioritization
- ❌ `GET /reprioritization/active` - Get active priority overrides
- ❌ `GET /consequences/active` - Get active lockouts and consequences

**Impact**: Phase 4 features are completely unavailable in the web UI, despite being fully implemented in the backend.

#### Phase 3: Intelligence & Decision Layer
- ❌ `POST /dependencies` - Add a topic dependency
- ❌ `GET /dependencies` - List all dependencies
- ❌ `GET /topics/{topic_id}/prerequisites` - Get prerequisites for a topic
- ❌ `GET /topics/{topic_id}/dependents` - Get topics that depend on this one
- ❌ `DELETE /dependencies/{dependency_id}` - Remove a dependency
- ❌ `POST /scenarios/simulate` - Run what-if scenario simulation
- ❌ `POST /scenarios/compare-strategies` - Compare different study strategies
- ❌ `GET /scenarios/skip-suggestions` - Get suggestions for topics to skip
- ❌ `GET /decision-logs` - View decision log history
- ❌ `GET /decision-logs/{log_id}` - Get detailed decision explanation

**Impact**: Phase 3 intelligence features are unavailable in the web UI.

#### CRUD Operations
- ❌ `PUT /courses/{course_id}` - Update course details
- ❌ `DELETE /courses/{course_id}` - Delete a course (endpoint exists but returns 501)
- ❌ `PUT /topics/{topic_id}` - Update topic details
- ❌ `DELETE /topics/{topic_id}` - Delete a topic
- ❌ `PATCH /topics/{topic_id}/skill` - Quick skill level update

**Impact**: Users cannot edit or delete courses/topics through the web UI.

### 2. Frontend UI Components Missing

#### Quiz System (Phase 2)
- ❌ Quiz creation form/page
- ❌ Quiz taking interface with MCQ questions
- ❌ Quiz results display
- ❌ Quiz history/attempts view
- ❌ Quiz management (edit, delete quizzes)

**Files Needed**:
- `frontend/src/pages/Quizzes.tsx` or quiz components
- `frontend/src/components/QuizCreator.tsx`
- `frontend/src/components/QuizTaker.tsx`
- `frontend/src/components/QuizResults.tsx`

#### Study Session Tracking (Phase 2)
- ❌ Study session timer component
- ❌ Start/stop session buttons
- ❌ Active session indicator
- ❌ Study time statistics page
- ❌ Daily/weekly time breakdown charts

**Files Needed**:
- `frontend/src/components/StudyTimer.tsx`
- `frontend/src/pages/StudySessions.tsx` or integrate into DailyPlan

#### Skill Management (Phase 2)
- ❌ Manual skill self-assessment form
- ❌ Skill update interface
- ❌ Skill decay application button/interface

**Files Needed**:
- `frontend/src/components/SkillAssessment.tsx`
- Integration into `CourseDetail.tsx` or `Progress.tsx`

#### Phase 4: Honesty & Reality Check UI
- ❌ Honesty warnings dashboard/component
- ❌ Fake productivity alerts
- ❌ Avoidance pattern indicators
- ❌ Overconfidence warnings
- ❌ Brutal honesty mode toggle
- ❌ Exam simulation page
- ❌ Motivation vs Reality dashboard page
- ❌ Forced re-prioritization alerts
- ❌ Active consequences/lockouts display

**Files Needed**:
- `frontend/src/pages/Honesty.tsx` or `frontend/src/pages/RealityCheck.tsx`
- `frontend/src/components/HonestyWarnings.tsx`
- `frontend/src/components/ExamSimulation.tsx`
- `frontend/src/components/MotivationReality.tsx`
- Integration into `Dashboard.tsx`

#### Phase 3: Intelligence Features UI
- ❌ Dependency management page
- ❌ Dependency graph visualization
- ❌ What-if scenario simulator page
- ❌ Strategy comparison interface
- ❌ Skip topic suggestions display
- ❌ Decision log viewer
- ❌ "Why This?" explainability component

**Files Needed**:
- `frontend/src/pages/Dependencies.tsx`
- `frontend/src/pages/Scenarios.tsx`
- `frontend/src/components/DependencyGraph.tsx`
- `frontend/src/components/ScenarioSimulator.tsx`
- `frontend/src/components/DecisionExplainer.tsx`
- Integration into `DailyPlan.tsx` for explainability

#### CRUD Operations UI
- ❌ Course edit form
- ❌ Course delete confirmation
- ❌ Topic edit form
- ❌ Topic delete confirmation
- ❌ Quick skill update (slider/input in topic list)

**Files Needed**:
- Edit forms in `Courses.tsx` and `CourseDetail.tsx`
- Delete confirmation modals

### 3. Frontend API Client Missing

The `frontend/src/services/api.ts` file is missing functions for:

- Quiz operations (create, get, take, view results)
- Study session operations (start, end, get active, statistics)
- Skill tracking (self-assessment, decay)
- Phase 4 operations (honesty, exam simulation, reprioritization)
- Phase 3 operations (dependencies, scenarios, decision logs)
- CRUD operations (update, delete for courses/topics)

### 4. Navigation & Routing Missing

The `frontend/src/App.tsx` routing is missing routes for:

- `/quizzes` - Quiz management and taking
- `/sessions` - Study session tracking
- `/honesty` or `/reality-check` - Phase 4 features
- `/dependencies` - Dependency management
- `/scenarios` - What-if simulations
- `/decisions` - Decision log viewer

The sidebar navigation in `Layout.tsx` likely needs updates to include these routes.

### 5. Phase 5 Tickets Not Fully Implemented

According to `info.md` Phase 5 tickets:

- ✅ **TICKET-501**: Frontend tech stack - DONE
- ✅ **TICKET-502**: Global app layout - DONE
- ✅ **TICKET-503**: Course & Topic Management UI - PARTIAL (missing edit/delete)
- ✅ **TICKET-504**: Daily Study Plan View - DONE
- ✅ **TICKET-505**: Skill Progress Visualization - DONE
- ✅ **TICKET-506**: Exam Readiness Dashboard - DONE
- ❌ **TICKET-507**: Explainability UI ("Why This?") - NOT IMPLEMENTED
- ❌ **TICKET-508**: Honesty & Reality Feedback UI - NOT IMPLEMENTED
- ❌ **TICKET-509**: Brutal Honesty Mode Toggle UI - NOT IMPLEMENTED
- ❌ **TICKET-510**: What-If Simulation UI - NOT IMPLEMENTED
- ⚠️ **TICKET-511**: UX Polish & Accessibility - PARTIAL (needs improvement)
- ⚠️ **TICKET-512**: Phase 5 Documentation - PARTIAL (QUICKSTART exists but missing detailed docs)

## Feature Completeness Matrix

| Feature Category | Backend Service | API Endpoint | Frontend UI | Status |
|-----------------|----------------|--------------|-------------|--------|
| **Phase 1: Foundation** |
| Course Management | ✅ | ✅ (CRUD partial) | ✅ (Create only) | 🟡 Partial |
| Topic Management | ✅ | ✅ (CRUD partial) | ✅ (Create only) | 🟡 Partial |
| Daily Study Plan | ✅ | ✅ | ✅ | ✅ Complete |
| Priority Calculation | ✅ | ✅ (via plan) | ✅ (via plan) | ✅ Complete |
| **Phase 2: Skill Tracking** |
| Skill History | ✅ | ✅ | ✅ | ✅ Complete |
| Quiz Engine | ✅ | ❌ | ❌ | 🔴 Missing |
| Study Sessions | ✅ | ❌ | ❌ | 🔴 Missing |
| Manual Assessment | ✅ | ❌ | ❌ | 🔴 Missing |
| Skill Decay | ✅ | ❌ | ❌ | 🔴 Missing |
| Weak Topic Detection | ✅ | ✅ | ✅ | ✅ Complete |
| **Phase 3: Intelligence** |
| Dependencies | ✅ | ❌ | ❌ | 🔴 Missing |
| Expected Scores | ✅ | ✅ | ✅ | ✅ Complete |
| Risk Analysis | ✅ | ✅ | ✅ | ✅ Complete |
| What-If Scenarios | ✅ | ❌ | ❌ | 🔴 Missing |
| Strategy Comparison | ✅ | ❌ | ❌ | 🔴 Missing |
| Decision Logs | ✅ | ❌ | ❌ | 🔴 Missing |
| **Phase 4: Honesty** |
| Fake Productivity | ✅ | ❌ | ❌ | 🔴 Missing |
| Avoidance Detection | ✅ | ❌ | ❌ | 🔴 Missing |
| Overconfidence | ✅ | ❌ | ❌ | 🔴 Missing |
| Exam Simulation | ✅ | ❌ | ❌ | 🔴 Missing |
| Reprioritization | ✅ | ❌ | ❌ | 🔴 Missing |
| Brutal Honesty Mode | ✅ | ❌ | ❌ | 🔴 Missing |

## Priority Recommendations

### High Priority (Core Functionality Missing)
1. **Quiz System** - Essential for Phase 2 skill tracking
2. **Study Session Tracking** - Required for adaptive planning and honesty detection
3. **CRUD Operations** - Users need to edit/delete courses and topics
4. **Manual Skill Assessment** - Core Phase 2 feature

### Medium Priority (Important Features)
5. **Phase 4 Honesty Features** - Critical for preventing self-deception
6. **Phase 3 Intelligence Features** - Adds significant value
7. **Explainability UI** - Makes the system transparent

### Low Priority (Polish)
8. **UX Improvements** - Loading states, error handling, accessibility
9. **Additional Visualizations** - More charts and analytics
10. **Documentation** - Detailed Phase 5 documentation

## Estimated Implementation Effort

### Backend API Endpoints
- Quiz endpoints: ~2-3 hours
- Study session endpoints: ~1-2 hours
- Skill tracking endpoints: ~1 hour
- Phase 4 endpoints: ~3-4 hours
- Phase 3 endpoints: ~3-4 hours
- CRUD endpoints: ~1 hour
- **Total Backend**: ~11-15 hours

### Frontend Components
- Quiz system: ~6-8 hours
- Study session tracking: ~4-5 hours
- Skill management: ~2-3 hours
- Phase 4 UI: ~8-10 hours
- Phase 3 UI: ~10-12 hours
- CRUD UI: ~3-4 hours
- **Total Frontend**: ~33-42 hours

### Total Estimated Effort: 44-57 hours

## Conclusion

While the backend services are fully implemented and the frontend has a solid foundation, there is a significant gap between what's available in the CLI and what's accessible through the web UI. The most critical missing features are:

1. Quiz system (completely missing)
2. Study session tracking (completely missing)
3. Phase 4 honesty features (completely missing)
4. Phase 3 intelligence features (completely missing)
5. Edit/delete functionality for courses and topics

The application is functional for basic use cases but lacks many of the advanced features that make it a comprehensive study planning system.

