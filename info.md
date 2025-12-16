Phase 1 — Foundation (MVP)

Goal: Build a working Skill-Aware Study Planner that can model courses, topics, skills, and generate a daily study plan based on priority.

---

## TICKET-001: Project Initialization & Repo Setup

**Type:** Task  
**Priority:** High  

### Description
Initialize the project repository and basic structure for Phase 1 development.

### Acceptance Criteria
- Repository initialized
- Clear folder structure
- README with project description and Phase 1 scope
- Basic run instructions included

### Tasks
- Create repository
- Define folder structure
- Add `.gitignore`
- Write initial README

---

## TICKET-002: Define Core Data Models

**Type:** Feature  
**Priority:** High  

### Description
Create core data models to represent courses, topics, and exams.

### Data Models
- Course
  - id
  - name
  - exam_date
- Topic
  - id
  - course_id
  - name
  - weight (0–1)
  - skill_level (0–100)

### Acceptance Criteria
- Models are clearly defined
- Can be serialized/deserialized
- Stored locally (JSON or SQLite)

---

## TICKET-003: Implement Local Storage Layer

**Type:** Task  
**Priority:** High  

### Description
Implement a simple persistence layer to store courses and topics.

### Acceptance Criteria
- Data persists between runs
- Can load/save courses and topics
- No external dependencies required

### Notes
Preferred options:
- JSON files (simple)
- SQLite (slightly more robust)

---

## TICKET-004: Priority Calculation Engine

**Type:** Feature  
**Priority:** Critical  

### Description
Implement the core priority calculation logic for study planning.

### Formula
priority = topic_weight × (1 - skill_level / 100) × urgency

yaml
Copy code

Where:
- urgency increases as exam date approaches

### Acceptance Criteria
- Each topic receives a numeric priority score
- Topics can be sorted by priority
- Logic is isolated and testable

---

## TICKET-005: Urgency Calculation Logic

**Type:** Task  
**Priority:** High  

### Description
Implement urgency calculation based on exam proximity.

### Rules (Initial Version)
- >30 days remaining → low urgency
- 7–30 days → medium urgency
- <7 days → high urgency

### Acceptance Criteria
- Urgency factor returned as a multiplier
- Logic documented and adjustable

---

## TICKET-006: Daily Study Plan Generator

**Type:** Feature  
**Priority:** High  

### Description
Generate a daily study plan based on available study hours and topic priorities.

### Inputs
- Available hours per day
- Sorted topic priorities

### Output
- Ordered list of topics
- Allocated time per topic

### Acceptance Criteria
- Total allocated time ≤ available hours
- Higher priority topics get more time
- Plan regenerates correctly when data changes

---

## TICKET-007: Basic User Interface (CLI or Minimal Web)

**Type:** Task  
**Priority:** Medium  

### Description
Create a minimal interface to interact with the system.

### Features
- Add/edit courses
- Add/edit topics
- Set available study hours
- Generate daily plan

### Acceptance Criteria
- User can create a course and topics
- User can generate and view a daily plan
- No styling required

---

## TICKET-008: Validation & Edge Case Handling

**Type:** Task  
**Priority:** Medium  

### Description
Handle invalid or missing inputs gracefully.

### Examples
- No topics defined
- Exam date in the past
- Weights not summing to 1
- Skill level outside 0–100

### Acceptance Criteria
- Clear error messages
- Application does not crash

---

## TICKET-009: Phase 1 Documentation

**Type:** Task  
**Priority:** Medium  

### Description
Document Phase 1 design decisions and usage.

### Acceptance Criteria
- Updated README
- Explanation of priority formula
- Instructions to run Phase 1 MVP

---

## Phase 1 Definition of Done

- User can model a course and topics
- System calculates priorities correctly
- Daily study plan is generated
- Data persists locally
- Logic works without UI polish
If you want, next I can:

🧱 Convert these tickets into GitHub Issues

🧠 Provide exact data schemas

⚙️ Give you a starter folder structure + boilerplate

🔢 Refine the priority formula mathematically

Just tell me the next move.







You said:
What should I use for this app, what language and framework


ChatGPT said:
Short answer first, then reasoning.

✅ My Recommendation (Best Fit for You)
Language: Python
Framework: FastAPI (backend) + SQLite
UI (Phase 1): CLI or very thin web UI
Later UI: React / simple HTML

This is the highest signal / lowest bullshit stack for this project.

Why Python is the Right Choice Here
You are not building a game engine or anti-cheat kernel driver here.
This project is about:

algorithms

prioritization logic

data modeling

adaptability

iteration speed

Python wins hard on:

⚡ Fast iteration

🧠 Clear logic expression

📊 Math & heuristics

🧪 Easy testing

🤖 Future AI/ML extension

Recruiters will not downgrade you for Python on a planner app.
They will downgrade you for an over-engineered stack.

Why FastAPI (Not Django)
Feature	FastAPI	Django
Boilerplate	Low	High
API-first	Yes	Meh
Performance	Excellent	Fine
Learning value	High	Lower
Control	Full	Opinionated

FastAPI gives you:

clean separation of logic

type hints (important!)

auto docs

future mobile / web / CLI reuse

Why SQLite
Zero setup

Perfect for single-user study tool

Can migrate later to Postgres

Forces you to design schemas properly

JSON is fine for Week 1, SQLite is better for Week 2+.

Phase 1 Stack (Final)
text
Copy code
Backend logic: Python 3.11+
Framework: FastAPI
Persistence: SQLite
ORM: SQLAlchemy (optional but recommended)
Interface: CLI OR minimal web UI
Alternative Stacks (When They Make Sense)
Option B — Node.js (If You Want Frontend First)
Use if:

you want heavy UI early

you think in JS naturally

text
Copy code
Language: TypeScript
Backend: NestJS or Express
DB: SQLite
Downside: more ceremony, slower logic iteration.

Option C — Java (If You Want Max Academic Rigor)
Use if:

you want very formal architecture

you enjoy verbosity

text
Copy code
Language: Java
Framework: Spring Boot
DB: H2 / SQLite
Downside: slower to iterate, less fun.

What I Do NOT Recommend (Yet)
❌ C++ — wrong abstraction level
❌ Rust — great, but slows iteration here
❌ Flutter — UI-first, logic second
❌ Full React + backend on day 1 — premature

Folder Structure (Recommended)
text
Copy code
study-planner/
├── app/
│   ├── models/
│   ├── services/
│   ├── api/
│   ├── planner/
│   └── storage/
├── tests/
├── main.py
├── README.md
└── requirements.txt
Final Verdict
Python + FastAPI + SQLite

Fast to build

Easy to reason about

Easy to evolve

Looks clean on a CV

Lets the idea shine

