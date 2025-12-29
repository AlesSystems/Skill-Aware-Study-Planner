# 📚 Skill-Aware Study Planner

> An intelligent, adaptive study planning system that learns from your performance, tracks skills over time, and automatically adjusts priorities based on quiz results and study behavior.

---

## ✨ What It Does

**Skill-Aware Study Planner** is a comprehensive study management system that helps you:

- 🎯 **Plan efficiently** - Get optimized daily study plans based on exam dates, topic importance, and your current skill levels
- 📊 **Track progress** - Monitor skill improvement over time with detailed history and visualizations
- 🧠 **Learn intelligently** - Take quizzes to verify understanding and automatically update your skill levels
- ⚠️ **Stay honest** - Detect when you're avoiding difficult topics or engaging in fake productivity
- 🔮 **Predict outcomes** - Get exam score estimates and risk analysis to know where you stand
- 🎓 **Study smarter** - Understand topic dependencies and optimize your time allocation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (Python 3.13 recommended)
- **Node.js 18+** and npm (for web UI)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Skill-Aware-Study-Planner
   ```

2. **Set up Python backend**
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

3. **Set up React frontend** (optional, for web UI)
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

#### Option 1: Web UI (Recommended)

**Terminal 1 - Start Backend:**
```bash
python -m uvicorn app.api.server:app --reload --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

#### Option 2: Command Line Interface

```bash
python main.py
```

---

## 🎨 Key Features

### 📖 Course & Topic Management

- Create courses with exam dates
- Add topics with importance weights (0-1 scale)
- Set initial skill levels (0-100)
- Visual weight validation (ensures topics sum to 100%)

### 📅 Intelligent Study Planning

- **Smart Priority Calculation**: Automatically prioritizes topics based on:
  - Exam urgency (days until exam)
  - Topic importance (weight)
  - Current skill gaps
  - Learning trends and study patterns

- **Adaptive Planning**: Plans adjust automatically as you:
  - Improve your skills through quizzes
  - Study different topics
  - Approach exam dates

- **Daily Study Plans**: Get optimized time allocation for each study session

### 📊 Skill Tracking & Assessment

- **Quiz Engine**: Create and take multiple-choice quizzes (5-10 questions)
- **Automatic Skill Updates**: Skills adjust based on quiz performance
- **Manual Self-Assessment**: Update skills manually (with reduced weight to prevent gaming)
- **Skill History**: Complete audit trail of all skill changes
- **Skill Decay**: Skills naturally decrease when topics are neglected (after 7 days)

### ⏱️ Study Session Tracking

- Start and stop study sessions per topic
- Track time spent on each topic
- View daily and weekly statistics
- Identify study patterns and habits

### 🎯 Progress Analytics

- **Skill Progress Charts**: Visualize skill improvement over time
- **Weak Topic Detection**: Automatically identify topics needing attention
- **Study Time Breakdown**: See where your time is going
- **Progress Dashboards**: Get comprehensive overviews of your learning journey

### 🧩 Intelligence & Decision Layer

- **Topic Dependencies**: Model prerequisite relationships between topics
- **Expected Exam Scores**: Predict your performance with confidence ranges
- **Risk Analysis**: Identify critical weaknesses and time pressure risks
- **What-If Scenarios**: Test different study strategies before committing
- **Strategy Comparison**: Compare balanced, high-weight, and weak-focus approaches
- **Decision Explainability**: Understand why the planner makes each recommendation

### 🎭 Honesty & Reality Check

- **Fake Productivity Detection**: Identifies when study time doesn't translate to improvement
- **Avoidance Pattern Detection**: Catches consistent avoidance of difficult topics
- **Overconfidence Detection**: Flags mismatches between self-assessment and quiz performance
- **Exam Simulation**: Predict your current exam score with pass/fail probability
- **Motivation vs Reality**: Compare time invested vs actual progress
- **Brutal Honesty Mode**: Optional unfiltered feedback for maximum accountability
- **Forced Re-Prioritization**: Automatic override when risk is too high

---

## 📐 How It Works

### Priority Calculation

The system calculates study priorities using this formula:

```
Priority = Topic Weight × (1 - Skill Level / 100) × Urgency Factor
```

**Urgency Factors:**
- More than 30 days until exam: **1.0x** (Low urgency)
- 7-30 days until exam: **2.0x** (Medium urgency)
- Less than 7 days until exam: **3.0x** (High urgency)

**Adaptive Adjustments:**
- Declining skill trend: +10% to +30% priority boost
- Over-studied topics: -10% priority reduction
- Under-studied topics: +20% priority boost

### Skill Management

**Quiz-Based Updates** (100% weight):
- Score > 50%: Skill increases
- Score < 50%: Skill decreases
- Maximum daily increase: 15 points

**Self-Assessment** (50% weight):
- Manual updates have reduced weight to prevent gaming
- Large changes (>20 points) require confirmation

**Skill Decay**:
- Starts after 7 days of inactivity
- Rate: 0.5 points per day
- Maximum decay: 30% of current skill level

---

## 🖥️ User Interfaces

### Web UI (React + TypeScript)

Modern, responsive web interface with:
- 📊 Interactive dashboards
- 📈 Progress charts and visualizations
- 🎨 Clean, distraction-free design
- ⚡ Real-time updates
- 📱 Responsive layout

### Command Line Interface

Full-featured CLI for:
- Quick access and automation
- Terminal-based workflows
- Scripting and integration

---

## 🗂️ Project Structure

```
Skill-Aware-Study-Planner/
├── app/
│   ├── api/              # FastAPI REST endpoints
│   ├── models/           # Data models (Pydantic)
│   ├── services/         # Business logic layer
│   ├── planner/          # Priority & planning algorithms
│   └── storage/          # Database layer (SQLAlchemy)
├── frontend/             # React + TypeScript web UI
│   ├── src/
│   │   ├── components/   # Reusable React components
│   │   ├── pages/        # Page components
│   │   └── services/    # API client
├── docs/                 # Documentation
├── tests/                # Unit tests
├── main.py              # CLI entry point
└── requirements.txt     # Python dependencies
```

---

## 💾 Data Storage

All data is stored locally in a **SQLite database** (`study_planner.db`):
- No internet required
- Complete privacy
- Easy backup (just copy the database file)
- Portable across devices

**Database Tables:**
- `courses` - Course information and exam dates
- `topics` - Topics with weights and skill levels
- `skill_history` - Complete audit trail of skill changes
- `study_sessions` - Time tracking records
- `quizzes` - Quiz definitions and questions
- `quiz_attempts` - Quiz results and scores
- `topic_dependencies` - Prerequisite relationships
- `decision_logs` - Planner decision explanations

---

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running quickly
- **[Phase 2 Documentation](docs/PHASE2_DOCUMENTATION.md)** - Skill tracking features
- **[Phase 4 Documentation](docs/phase4_documentation.md)** - Honesty & reality check system
- **[Missing Features Analysis](docs/MISSING_FEATURES_ANALYSIS.md)** - Development roadmap

---

## 🛠️ Development

### Running Tests

```bash
python test_app.py
python tests/test_phase4.py
```

### API Documentation

When the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🎯 Use Cases

- **Students preparing for exams** - Get optimized study plans and track progress
- **Self-learners** - Structure your learning with skill tracking
- **Teachers** - Help students identify weak areas and focus their study time
- **Anyone learning** - Make data-driven decisions about what to study next

---

## 🔮 Future Enhancements

- Machine learning for personalized study patterns
- Spaced repetition system (SRS) integration
- Multi-exam scheduling optimization
- Study group collaboration features
- Cloud sync and multi-device support
- PDF/document ingestion for automated topic extraction
- AI-powered quiz generation from course materials
- Desktop app version (Electron/Tauri)

---

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ for students who want to study smarter, not harder.**
