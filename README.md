# Skill-Aware Study Planner

An intelligent study planning system that prioritizes topics based on skill level, exam urgency, and topic importance.

## Phase 1 - Foundation (MVP)

### Features
- Model courses with exam dates
- Define topics with weights and skill levels
- Calculate priority scores based on urgency and skill gaps
- Generate daily study plans optimized by priority
- Local data persistence with SQLite

### Priority Formula
```
priority = topic_weight × (1 - skill_level / 100) × urgency
```

Where:
- **topic_weight**: Importance of topic (0-1)
- **skill_level**: Current mastery (0-100)
- **urgency**: Multiplier based on days until exam

### Urgency Rules
- \>30 days: Low urgency (1.0x)
- 7-30 days: Medium urgency (2.0x)
- <7 days: High urgency (3.0x)

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

## Project Structure
```
study-planner/
├── app/
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   ├── planner/      # Priority & planning algorithms
│   └── storage/      # Database layer
├── tests/            # Unit tests
├── main.py           # Entry point
└── requirements.txt
```

## Development Status

Phase 1 MVP - Core functionality implemented
- ✅ Project structure
- ✅ Core data models
- ✅ Priority calculation
- ✅ Daily plan generation
- ✅ Local storage (SQLite)
- ✅ CLI interface

## Future Phases
- Phase 2: Enhanced UI with React
- Phase 3: Analytics and skill tracking
- Phase 4: Multi-user support and cloud sync
