import { useState, useEffect } from 'react';
import { Clock, Play, Square, TrendingUp, Calendar } from 'lucide-react';
import { getCourses, getTopics, startStudySession, endStudySession, getActiveSession, getStudySessions, getStudyStatistics, type Course, type Topic, type StudySession } from '../services/api';

const StudySessions = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [activeSession, setActiveSession] = useState<StudySession | null>(null);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadActiveSession, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadTopics(selectedCourse);
    }
  }, [selectedCourse]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (activeSession) {
      interval = setInterval(() => {
        const start = new Date(activeSession.start_time).getTime();
        const now = Date.now();
        setElapsedTime(Math.floor((now - start) / 1000));
      }, 1000);
    } else {
      setElapsedTime(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeSession]);

  const loadData = async () => {
    try {
      const [coursesData, activeSessionData, sessionsData, statsData] = await Promise.all([
        getCourses(),
        getActiveSession(),
        getStudySessions(20),
        getStudyStatistics()
      ]);
      setCourses(coursesData);
      setActiveSession(activeSessionData);
      setSessions(sessionsData);
      setStatistics(statsData);
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTopics = async (courseId: number) => {
    try {
      const data = await getTopics(courseId);
      setTopics(data);
    } catch (error) {
      console.error('Failed to load topics', error);
    }
  };

  const loadActiveSession = async () => {
    try {
      const data = await getActiveSession();
      setActiveSession(data);
    } catch (error) {
      console.error('Failed to load active session', error);
    }
  };

  const handleStartSession = async () => {
    if (!selectedTopic) {
      alert('Please select a topic first');
      return;
    }

    try {
      const session = await startStudySession(selectedTopic);
      setActiveSession(session);
      loadData();
    } catch (error: any) {
      console.error('Failed to start session', error);
      alert(error.response?.data?.detail || 'Failed to start session');
    }
  };

  const handleEndSession = async () => {
    if (!activeSession?.id) return;

    try {
      await endStudySession(activeSession.id);
      setActiveSession(null);
      loadData();
    } catch (error) {
      console.error('Failed to end session', error);
      alert('Failed to end session');
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const getTopicName = (topicId: number) => {
    const allTopics = topics;
    const topic = allTopics.find(t => t.id === topicId);
    return topic?.name || `Topic ${topicId}`;
  };

  if (loading) return <div className="text-white p-6">Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-white mb-6 flex items-center gap-2">
        <Clock className="w-8 h-8" />
        Study Sessions
      </h1>

      {/* Active Session Timer */}
      <div className="mb-6 bg-gradient-to-r from-purple-900 to-indigo-900 rounded-lg p-6">
        {activeSession ? (
          <div className="text-center">
            <h2 className="text-2xl text-white mb-4">Active Session</h2>
            <div className="text-6xl font-bold text-white mb-4 font-mono">
              {formatTime(elapsedTime)}
            </div>
            <p className="text-gray-300 mb-6">
              Studying: {getTopicName(activeSession.topic_id)}
            </p>
            <button
              onClick={handleEndSession}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 mx-auto"
            >
              <Square className="w-5 h-5" />
              End Session
            </button>
          </div>
        ) : (
          <div className="text-center">
            <h2 className="text-2xl text-white mb-4">No Active Session</h2>
            <div className="flex gap-4 justify-center mb-4">
              <select
                value={selectedCourse || ''}
                onChange={(e) => {
                  setSelectedCourse(Number(e.target.value));
                  setSelectedTopic(null);
                }}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg"
              >
                <option value="">Select Course</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>{course.name}</option>
                ))}
              </select>

              {selectedCourse && (
                <select
                  value={selectedTopic || ''}
                  onChange={(e) => setSelectedTopic(Number(e.target.value))}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg"
                >
                  <option value="">Select Topic</option>
                  {topics.map(topic => (
                    <option key={topic.id} value={topic.id}>{topic.name}</option>
                  ))}
                </select>
              )}
            </div>
            <button
              onClick={handleStartSession}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 mx-auto"
              disabled={!selectedTopic}
            >
              <Play className="w-5 h-5" />
              Start Session
            </button>
          </div>
        )}
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-400" />
              <h3 className="text-gray-400">Total Sessions</h3>
            </div>
            <p className="text-3xl font-bold text-white">{statistics.total_sessions}</p>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-green-400" />
              <h3 className="text-gray-400">Total Hours</h3>
            </div>
            <p className="text-3xl font-bold text-white">{statistics.total_hours.toFixed(1)}h</p>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-5 h-5 text-purple-400" />
              <h3 className="text-gray-400">Last 7 Days</h3>
            </div>
            <p className="text-3xl font-bold text-white">{statistics.last_7_days_hours.toFixed(1)}h</p>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-yellow-400" />
              <h3 className="text-gray-400">Avg Session</h3>
            </div>
            <p className="text-3xl font-bold text-white">{statistics.average_session_minutes.toFixed(0)}m</p>
          </div>
        </div>
      )}

      {/* Recent Sessions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-4">Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p className="text-gray-400">No study sessions yet. Start one to track your progress!</p>
        ) : (
          <div className="space-y-2">
            {sessions.map(session => (
              <div key={session.id} className="p-4 bg-gray-700 rounded-lg flex justify-between items-center">
                <div>
                  <p className="text-white font-semibold">{getTopicName(session.topic_id)}</p>
                  <p className="text-gray-400 text-sm">
                    {new Date(session.start_time).toLocaleDateString()} at {new Date(session.start_time).toLocaleTimeString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-400">
                    {session.duration_minutes ? formatDuration(session.duration_minutes) : 'In progress'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudySessions;
