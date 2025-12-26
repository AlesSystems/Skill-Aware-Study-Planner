import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getCourses, getTopics, getSkillHistory, getWeakTopics, type Course, type Topic, type SkillHistory, type WeakTopic } from '../services/api';
import { AlertTriangle, TrendingUp } from 'lucide-react';

const Progress = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [history, setHistory] = useState<SkillHistory[]>([]);
  const [weakTopics, setWeakTopics] = useState<WeakTopic[]>([]);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadTopics(parseInt(selectedCourse));
    }
  }, [selectedCourse]);

  useEffect(() => {
    if (selectedTopic) {
      loadHistory(parseInt(selectedTopic));
    }
  }, [selectedTopic]);

  const loadInitialData = async () => {
    try {
      const [coursesData, weakData] = await Promise.all([
        getCourses(),
        getWeakTopics()
      ]);
      setCourses(coursesData);
      setWeakTopics(weakData);
    } catch (error) {
      console.error('Failed to load data', error);
    }
  };

  const loadTopics = async (courseId: number) => {
    try {
      const data = await getTopics(courseId);
      setTopics(data);
      if (data.length > 0) setSelectedTopic(data[0].id.toString());
      else setSelectedTopic('');
    } catch (error) {
      console.error('Failed to load topics', error);
    }
  };

  const loadHistory = async (topicId: number) => {
    try {
      const data = await getSkillHistory(topicId);
      // Format date for chart
      const formatted = data.map(h => ({
        ...h,
        date: new Date(h.timestamp).toLocaleDateString()
      })).reverse(); 
      setHistory(formatted);
    } catch (error) {
      console.error('Failed to load history', error);
    }
  };

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-white">Progress & Analytics</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Skill History Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-400" /> Skill History
            </h3>
            <div className="flex gap-2">
              <select 
                className="bg-gray-700 text-white rounded px-2 py-1 text-sm border border-gray-600 outline-none"
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
              >
                <option value="">Select Course</option>
                {courses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <select 
                className="bg-gray-700 text-white rounded px-2 py-1 text-sm border border-gray-600 outline-none"
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                disabled={!selectedCourse}
              >
                <option value="">Select Topic</option>
                {topics.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
          </div>

          <div className="h-64 w-full">
            {history.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" fontSize={12} />
                  <YAxis stroke="#9CA3AF" fontSize={12} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }}
                    itemStyle={{ color: '#F3F4F6' }}
                  />
                  <Line type="monotone" dataKey="new_skill" stroke="#3B82F6" strokeWidth={2} dot={{ fill: '#3B82F6' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                {selectedTopic ? 'No history yet' : 'Select a topic to view history'}
              </div>
            )}
          </div>
        </div>

        {/* Weak Topics */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
            <AlertTriangle size={20} className="text-yellow-500" /> Weak Topics
          </h3>
          
          <div className="space-y-4 max-h-64 overflow-y-auto pr-2">
            {weakTopics.map((item, i) => (
              <div key={i} className="bg-gray-700/50 p-3 rounded flex items-center justify-between">
                <div>
                  <div className="font-medium text-white">{item.topic.name}</div>
                  <div className="text-xs text-gray-400">{item.course.name}</div>
                </div>
                <div className="text-right">
                  <div className="text-red-400 font-bold">{item.topic.skill_level.toFixed(0)}%</div>
                  <div className="text-xs text-gray-500">{item.days_inactive} days inactive</div>
                </div>
              </div>
            ))}
            {weakTopics.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No weak topics detected. Good job!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Progress;

