# Phase 5 — Frontend UI & User Experience

Goal: Build a clear, honest, and decision-focused user interface that exposes the planner’s intelligence and guides daily action.

---

## TICKET-501: Frontend Tech Stack Setup

**Type:** Task  
**Priority:** High  

### Description
Initialize the frontend project and connect it to the backend API.

### Recommended Stack
- Framework: React
- Language: TypeScript
- Styling: Tailwind CSS
- Charts: Chart.js or Recharts

### Acceptance Criteria
- Frontend project initialized
- Backend API reachable
- Basic routing configured

---

## TICKET-502: Global App Layout

**Type:** Feature  
**Priority:** High  

### Description
Create the main application layout.

### Layout Sections
- Top bar (exam countdown, honesty status)
- Sidebar navigation
- Main content area

### Acceptance Criteria
- Consistent layout across pages
- Responsive design (desktop-first)
- Clean, distraction-free UI

---

## TICKET-503: Course & Topic Management UI

**Type:** Feature  
**Priority:** High  

### Description
UI to create, edit, and manage courses and topics.

### Features
- Add/edit courses
- Add/edit topics
- Set weights and exam dates
- Visual weight validation (sum = 100%)

### Acceptance Criteria
- CRUD operations fully functional
- Validation errors shown clearly
- Changes persist correctly

---

## TICKET-504: Daily Study Plan View

**Type:** Feature  
**Priority:** Critical  

### Description
Primary daily usage screen showing what to study today.

### Display
- Ordered topic list
- Time allocation per topic
- Priority indicators
- Dependency warnings

### Acceptance Criteria
- Clear action-oriented design
- High-priority items visually emphasized
- Explanations accessible per item

---

## TICKET-505: Skill Progress Visualization

**Type:** Feature  
**Priority:** High  

### Description
Visualize skill evolution over time.

### Charts
- Skill history per topic
- Weakest topics overview
- Skill decay indicators

### Acceptance Criteria
- Charts accurate and readable
- Hover explanations available
- No visual clutter

---

## TICKET-506: Exam Readiness Dashboard

**Type:** Feature  
**Priority:** Critical  

### Description
High-level overview of exam preparedness.

### Metrics
- Expected exam score range
- Pass/fail probability
- Risk indicators
- Blocking prerequisites

### Acceptance Criteria
- One-screen overview
- Risks clearly highlighted
- Updates dynamically

---

## TICKET-507: Explainability UI (“Why This?”)

**Type:** Feature  
**Priority:** High  

### Description
Expose planner reasoning to the user.

### Features
- “Why is this recommended?” button
- Priority breakdown (weight, skill, urgency)
- Dependency explanations

### Acceptance Criteria
- Decisions are transparent
- Explanations match backend logic
- No black-box behavior

---

## TICKET-508: Honesty & Reality Feedback UI

**Type:** Feature  
**Priority:** High  

### Description
Surface honesty-related signals without being noisy.

### Elements
- Fake productivity warnings
- Avoidance alerts
- Overconfidence flags

### Acceptance Criteria
- Warnings are visible but not spammy
- Severity clearly communicated
- User understands consequences

---

## TICKET-509: Brutal Honesty Mode Toggle UI

**Type:** Feature  
**Priority:** Medium  

### Description
UI to enable/disable Brutal Honesty Mode.

### Features
- Warning modal before enabling
- Visual mode indicator
- Immediate behavior change

### Acceptance Criteria
- Mode status always visible
- Toggle persists
- UX reflects mode severity

---

## TICKET-510: What-If Simulation UI

**Type:** Feature  
**Priority:** Medium  

### Description
UI to run and compare what-if study scenarios.

### Inputs
- Daily hours
- Strategy selection
- Exam date changes

### Outputs
- Projected scores
- Skill changes
- Risk comparison

### Acceptance Criteria
- Simulations clearly separated from real data
- Results easy to compare
- No accidental data overwrite

---

## TICKET-511: UX Polish & Accessibility

**Type:** Task  
**Priority:** Medium  

### Description
Improve usability and accessibility.

### Tasks
- Keyboard navigation
- Color contrast validation
- Loading states
- Error states

### Acceptance Criteria
- App usable without mouse
- Clear feedback on all actions
- No silent failures

---

## TICKET-512: Phase 5 Documentation

**Type:** Task  
**Priority:** Medium  

### Description
Document frontend architecture and UX principles.

### Content
- Component structure
- State management approach
- UX philosophy (clarity > motivation)

### Acceptance Criteria
- README updated
- Frontend onboarding instructions
- Phase 5 scope documented

---

## Phase 5 Definition of Done

- User can fully operate the planner via UI
- Core decisions are visible and explained
- Risks and honesty signals are clear
- UI supports daily real-world use
