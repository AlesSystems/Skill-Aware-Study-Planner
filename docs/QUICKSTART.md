# Quick Start Guide

## Phase 5 Complete! ✅

The Skill-Aware Study Planner now includes a modern web UI with **React + TypeScript** and a FastAPI backend.

## What's Implemented

### ✅ Phase 1-4: Core Features
- Course and Topic management
- Priority calculation engine
- Skill tracking and adaptation
- Quiz engine and study sessions
- Dependency management
- Risk analysis and exam score prediction
- Honesty & Reality Check System

### ✅ Phase 5: Frontend UI & User Experience
- **TICKET-501**: Frontend tech stack (React + TypeScript + Tailwind CSS)
- **TICKET-502**: Global app layout with sidebar navigation
- **TICKET-503**: Course & Topic Management UI (full CRUD)
- **TICKET-504**: Daily Study Plan View (action-oriented design)
- **TICKET-505**: Skill Progress Visualization (charts and analytics)
- **TICKET-506**: Exam Readiness Dashboard (scores, risks, warnings)

## Quick Start

### Prerequisites

- **Python 3.9+** (Python 3.13 recommended)
- **Node.js 18+** and npm (or yarn/pnpm)

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install React frontend dependencies:**
```bash
cd frontend
npm install
```

### Running the Application

You need **two terminals** running simultaneously:

#### Terminal 1: Backend Server (FastAPI)
```bash
# From project root directory
python -m uvicorn app.api.server:app --reload --port 8000
```

The backend API will be available at:
- **API Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

#### Terminal 2: Frontend Development Server (React + Vite)
```bash
# From frontend directory
cd frontend
npm run dev
```

The React frontend will be available at:
- **Web UI**: `http://localhost:5173` (Vite default port)

> **Note**: The frontend is configured with a proxy that forwards `/api` requests to the backend at `http://localhost:8000`. Make sure the backend is running before accessing the frontend.

### Building for Production

To build the React frontend for production:

```bash
cd frontend
npm run build
```

This creates an optimized production build in `frontend/dist/`. You can preview the production build locally with:

```bash
npm run preview
```

For production deployment, serve the `dist/` folder with a static file server (e.g., nginx, Apache, or a simple HTTP server) and configure it to proxy API requests to your backend.

### Using the React Web Application

1. **Open your browser** to `http://localhost:5173` (the React frontend)
2. **Create a Course**: 
   - Navigate to "Courses" in the sidebar
   - Click "Add Course" button
   - Enter course name and exam date
3. **Add Topics**: 
   - Click on a course to view its details
   - Click "Add Topic" button
   - Set topic name, weight (0-1), and skill level (0-100)
4. **Generate Daily Plan**: 
   - Navigate to "Daily Plan" in the sidebar
   - Enter available study hours
   - Toggle adaptive planning if desired
   - Click "Generate Plan" to see your optimized study schedule
5. **View Progress**: 
   - Navigate to "Progress" in the sidebar
   - View skill history charts and identify weak topics
6. **Check Dashboard**: 
   - Navigate to "Dashboard" in the sidebar
   - View exam readiness scores, risk warnings, and overall progress

## Alternative: CLI Mode

You can still use the original CLI interface:

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

### Backend (Python/FastAPI)
```
app/
├── models/         # Pydantic data models
├── storage/        # SQLAlchemy database layer
├── planner/        # Priority & planning algorithms
├── services/       # Business logic coordination
└── api/            # FastAPI REST endpoints
```

### Frontend (React + TypeScript + Vite)
```
frontend/
├── src/
│   ├── components/ # Reusable React components (e.g., Layout.tsx)
│   ├── pages/      # Page components (Dashboard, Courses, DailyPlan, Progress, CourseDetail)
│   ├── services/   # API client (api.ts - axios-based)
│   ├── App.tsx     # Main React app component
│   └── main.tsx    # React entry point
├── public/         # Static assets
├── package.json    # Dependencies and scripts
└── vite.config.ts  # Vite configuration with API proxy
```

**Tech Stack:**
- **Frontend**: React 19, TypeScript, Tailwind CSS, Vite
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite (local file: `study_planner.db`)

## Key Features

- **Smart Priority Calculation**: Focuses on skill gaps and exam urgency
- **Adaptive Planning**: Plans change as you improve
- **Local First**: No internet required, data stored locally
- **Validated Input**: Catches errors before they cause problems
- **Modern Web UI**: Beautiful, responsive interface with real-time updates
- **Exam Readiness Dashboard**: See your predicted scores and risks at a glance
- **Progress Tracking**: Visual charts showing skill improvement over time

## API Endpoints

The backend exposes a REST API:

- `GET /courses` - List all courses
- `POST /courses` - Create a course
- `GET /courses/{id}/topics` - Get topics for a course
- `POST /topics` - Create a topic
- `POST /plan` - Generate daily study plan
- `GET /analytics/expected-scores` - Get exam score predictions
- `GET /analytics/risks` - Get risk analysis
- `GET /analytics/weak-topics` - Get weak topics list
- `GET /topics/{id}/history` - Get skill history for a topic

Full API documentation available at `http://localhost:8000/docs`

## Troubleshooting

### Backend won't start
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Verify Python version: `python --version` (should be 3.9+)

### Frontend (React) won't start
- Ensure Node.js is installed: `node --version` (should be 18+)
- Ensure npm is installed: `npm --version`
- Install dependencies: `cd frontend && npm install`
- Check if port 5173 is already in use (Vite default port)
- Try clearing node_modules and reinstalling: `rm -rf node_modules && npm install`
- Check for TypeScript errors: `npm run build` (will show compilation errors)

### API connection errors
- **Ensure backend is running first** on port 8000 before starting the frontend
- Check browser console (F12) for CORS or network errors
- Verify the proxy configuration in `frontend/vite.config.ts` is correct
- Test backend directly: Open `http://localhost:8000/docs` in your browser
- If using a different backend port, update the proxy target in `vite.config.ts`

## Data Storage

All data is stored in `study_planner.db` (SQLite file).
To reset: simply delete this file.

---

**Phase 5 Definition of Done**: ✅ Complete
- ✅ User can fully operate the planner via UI
- ✅ Core decisions are visible and explained
- ✅ Risks and honesty signals are clear
- ✅ UI supports daily real-world use
