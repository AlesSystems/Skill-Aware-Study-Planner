# Skill-Aware Study Planner

An intelligent, adaptive study planning system that learns from your performance, tracks skills over time, and automatically adjusts priorities based on quiz results and study behavior.

## Features

### Phase 1 - Foundation (MVP)
- ✅ Model courses with exam dates
- ✅ Define topics with weights and skill levels
- ✅ Calculate priority scores based on urgency and skill gaps
- ✅ Generate daily study plans optimized by priority
- ✅ Local data persistence with SQLite
- ✅ CLI interface

### Phase 2 - Skill Tracking & Adaptation (Current)
- ✅ **Skill History Tracking**: Complete audit trail of skill changes
- ✅ **Quiz Engine**: MCQ-based quizzes (5-10 questions per quiz)
- ✅ **Intelligent Skill Updates**: Automatic adjustment based on quiz performance
- ✅ **Manual Self-Assessment**: User-driven skill updates with reduced weight
- ✅ **Study Session Tracking**: Time tracking per topic with start/stop
- ✅ **Skill Decay Logic**: Natural skill decrease for neglected topics
- ✅ **Weak Topic Detection**: Automatic identification of topics needing attention
- ✅ **Adaptive Priority Recalculation**: Dynamic planning based on learning trends
- ✅ **Progress Visualization**: Charts for skill progress and study time

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the CLI interface
python main.py
```

## CLI Menu Overview

```
--- Course & Topic Management ---
1. Add Course
2. Add Topic to Course
3. View All Courses
4. View Topics for Course

--- Study Planning ---
5. Generate Daily Study Plan (with adaptive mode)
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

## Priority Formula

**Base Priority**:
```
priority = topic_weight × (1 - skill_level / 100) × urgency
```

**Adaptive Adjustments**:
- Declining skill trend: +10% to +30% priority boost
- Over-studied topics: -10% priority reduction
- Under-studied topics: +20% priority boost

Where:
- **topic_weight**: Importance of topic (0-1)
- **skill_level**: Current mastery (0-100)
- **urgency**: Multiplier based on days until exam

### Urgency Rules
- \>30 days: Low urgency (1.0x)
- 7-30 days: Medium urgency (2.0x)
- <7 days: High urgency (3.0x)

## Skill Management

### Skill Update Rules
1. **Quiz-based**: Full weight (100%)
   - Score > 50%: Skill increases
   - Score < 50%: Skill decreases
   - Max daily increase: 15 points

2. **Self-assessment**: Reduced weight (50%)
   - Large changes (>20 points) require confirmation
   - Helps prevent gaming the system

3. **Skill Decay**: After 7 days of inactivity
   - Rate: 0.5 points per day
   - Maximum: 30% of current skill

## Project Structure
```
study-planner/
├── app/
│   ├── models/           # Data models (Pydantic)
│   ├── services/         # Business logic
│   │   ├── planner_service.py
│   │   ├── quiz_service.py
│   │   ├── skill_tracking_service.py
│   │   ├── study_session_service.py
│   │   └── progress_service.py
│   ├── planner/          # Priority & planning algorithms
│   └── storage/          # Database layer (SQLAlchemy)
├── docs/                 # Documentation
│   └── PHASE2_DOCUMENTATION.md
├── tests/                # Unit tests
├── main.py               # CLI Entry point
└── requirements.txt
```

## Database Schema

### Core Tables
- `courses`: Course information and exam dates
- `topics`: Topics with weights and current skill levels

### Phase 2 Tables
- `skill_history`: Audit trail of all skill changes
- `study_sessions`: Time tracking records
- `quizzes`: Quiz definitions
- `quiz_questions`: MCQ questions with answers
- `quiz_attempts`: Quiz submission records with scores

## Development Status

### Phase 1 (MVP) - ✅ Complete
- Project structure
- Core data models
- Priority calculation
- Daily plan generation
- Local storage (SQLite)
- CLI interface

### Phase 2 (Skill Tracking & Adaptation) - ✅ Complete
- Skill history tracking
- Quiz engine with auto-scoring
- Intelligent skill updates
- Manual self-assessment
- Study session tracking
- Skill decay logic
- Weak topic detection
- Adaptive priority recalculation
- Progress visualization

## Documentation

- **Phase 2 Features**: See [docs/PHASE2_DOCUMENTATION.md](docs/PHASE2_DOCUMENTATION.md)
- **Converting to React GUI**: See React conversion guide in Phase 2 docs

## Converting to React GUI

**Yes! This application is ready for React conversion.**

The clean separation between business logic (services) and interface (CLI) makes it straightforward to:
1. Create a FastAPI/Flask REST API wrapper
2. Build React components consuming the API
3. Maintain all existing business logic

See [docs/PHASE2_DOCUMENTATION.md](docs/PHASE2_DOCUMENTATION.md) for detailed conversion guide with examples.

## Future Enhancements

### Potential Phase 3+
- Machine learning for personalized decay rates
- Spaced repetition system (SRS) integration
- Advanced analytics and predictions
- Study group collaboration features
- Web/mobile interface
- Cloud sync and multi-device support

## License

MIT
