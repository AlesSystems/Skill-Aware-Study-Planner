import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import DailyPlan from './pages/DailyPlan';
import Progress from './pages/Progress';
import Quizzes from './pages/Quizzes';
import StudySessions from './pages/StudySessions';
import SkillManagement from './pages/SkillManagement';
import Dependencies from './pages/Dependencies';
import Scenarios from './pages/Scenarios';
import DecisionLogs from './pages/DecisionLogs';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="courses" element={<Courses />} />
          <Route path="courses/:id" element={<CourseDetail />} />
          <Route path="plan" element={<DailyPlan />} />
          <Route path="progress" element={<Progress />} />
          <Route path="quizzes" element={<Quizzes />} />
          <Route path="sessions" element={<StudySessions />} />
          <Route path="skills" element={<SkillManagement />} />
          <Route path="dependencies" element={<Dependencies />} />
          <Route path="scenarios" element={<Scenarios />} />
          <Route path="decisions" element={<DecisionLogs />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
