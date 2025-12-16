# Quick Start Guide

## Phase 1 Complete! ✅

The Skill-Aware Study Planner MVP is ready to use.

## What's Implemented

### ✅ TICKET-001: Project Initialization
- Clean folder structure created
- README and documentation added
- .gitignore configured

### ✅ TICKET-002: Core Data Models
- Course model (id, name, exam_date)
- Topic model (id, course_id, name, weight, skill_level)
- Validation included

### ✅ TICKET-003: Local Storage Layer
- SQLite database implementation
- Full CRUD operations
- Data persists between runs

### ✅ TICKET-004: Priority Calculation Engine
- Formula: `priority = weight × (1 - skill/100) × urgency`
- Isolated and testable logic
- Sorting by priority score

### ✅ TICKET-005: Urgency Calculation
- >30 days: 1.0x urgency
- 7-30 days: 2.0x urgency
- <7 days: 3.0x urgency

### ✅ TICKET-006: Daily Study Plan Generator
- Allocates time proportionally to priority
- Respects available study hours
- Smart distribution algorithm

### ✅ TICKET-007: CLI Interface
- Add/edit courses and topics
- Generate daily plans
- Update skill levels
- View all data

### ✅ TICKET-008: Validation & Error Handling
- Input validation for all fields
- Weight sum validation
- Graceful error messages

### ✅ TICKET-009: Documentation
- Complete README
- Formula explanation
- Usage instructions

## Quick Start

```bash
# Run the CLI application
python main.py
```

## Example Workflow

1. **Add a Course**: Enter course name and exam date
2. **Add Topics**: Define topics with weights (should sum to 1.0) and skill levels (0-100)
3. **Generate Plan**: Input available study hours and get an optimized plan
4. **Study**: Follow the plan!
5. **Update Skills**: After studying, update your skill levels
6. **Regenerate**: Plan adapts as your skills improve and exams get closer

## Testing

Run the test script to verify everything works:
```bash
python test_app.py
```

## Architecture

```
app/
├── models/         # Pydantic data models
├── storage/        # SQLAlchemy database layer
├── planner/        # Priority & planning algorithms
└── services/       # Business logic coordination
```

## Key Features

- **Smart Priority Calculation**: Focuses on skill gaps and exam urgency
- **Adaptive Planning**: Plans change as you improve
- **Local First**: No internet required, data stored locally
- **Validated Input**: Catches errors before they cause problems

## Next Steps (Future Phases)

- Phase 2: React UI for better user experience
- Phase 3: Analytics and progress tracking
- Phase 4: Multi-user and cloud sync

## Data Storage

All data is stored in `study_planner.db` (SQLite file).
To reset: simply delete this file.

---

**Phase 1 Definition of Done**: ✅ Complete
- ✅ User can model courses and topics
- ✅ System calculates priorities correctly
- ✅ Daily study plan is generated
- ✅ Data persists locally
- ✅ Logic works without UI polish
