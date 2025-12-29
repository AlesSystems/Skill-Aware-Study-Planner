import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Plus, ArrowLeft, Trash2, AlertTriangle, Edit2 } from 'lucide-react';
import { getTopics, createTopic, getCourses, deleteTopic, updateTopic, type Topic, type Course } from '../services/api';

const CourseDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);

  // Form State
  const [name, setName] = useState('');
  const [weight, setWeight] = useState(0.1);
  const [skill, setSkill] = useState(50);

  useEffect(() => {
    if (id) {
      loadData();
    }
  }, [id]);

  const loadData = async () => {
    try {
      const courseId = parseInt(id!);
      const [coursesData, topicsData] = await Promise.all([
        getCourses(),
        getTopics(courseId)
      ]);
      const foundCourse = coursesData.find(c => c.id === courseId);
      setCourse(foundCourse || null);
      setTopics(topicsData);
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    try {
      if (editingTopic) {
        await updateTopic(editingTopic.id!, {
          course_id: parseInt(id),
          name,
          weight: Number(weight),
          skill_level: Number(skill)
        });
        setEditingTopic(null);
      } else {
        await createTopic({
          course_id: parseInt(id),
          name,
          weight: Number(weight),
          skill_level: Number(skill)
        });
      }
      setShowForm(false);
      setName('');
      setWeight(0.1);
      setSkill(50);
      loadData();
    } catch (error) {
      console.error('Failed to create/update topic', error);
      alert('Error saving topic');
    }
  };

  const handleEditTopic = (topic: Topic) => {
    setEditingTopic(topic);
    setName(topic.name);
    setWeight(topic.weight);
    setSkill(topic.skill_level);
    setShowForm(true);
  };

  const handleDeleteTopic = async (topicId: number) => {
    if (!confirm('Are you sure you want to delete this topic?')) return;
    try {
      await deleteTopic(topicId);
      loadData();
    } catch (error) {
      console.error('Failed to delete topic', error);
      alert('Error deleting topic');
    }
  };

  const totalWeight = topics.reduce((sum, t) => sum + t.weight, 0);

  if (loading) return <div className="text-white p-6">Loading...</div>;
  if (!course) return <div className="text-white p-6">Course not found</div>;

  return (
    <div className="space-y-6">
      <button 
        onClick={() => navigate('/courses')}
        className="flex items-center text-gray-400 hover:text-white mb-4 transition-colors"
      >
        <ArrowLeft size={20} className="mr-2" /> Back to Courses
      </button>

      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold text-white">{course.name}</h2>
          <p className="text-gray-400">Exam: {new Date(course.exam_date).toLocaleDateString()}</p>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${Math.abs(totalWeight - 1.0) < 0.01 ? 'text-green-400' : 'text-yellow-400'}`}>
            Total Weight: {(totalWeight * 100).toFixed(0)}%
          </div>
          {Math.abs(totalWeight - 1.0) >= 0.01 && (
            <div className="text-xs text-yellow-500 flex items-center justify-end mt-1">
              <AlertTriangle size={12} className="mr-1" /> Should sum to 100%
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between items-center mt-8">
        <h3 className="text-xl font-bold text-white">Topics</h3>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus size={20} />
          Add Topic
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreateTopic} className="bg-gray-800 p-6 rounded-lg border border-gray-700 space-y-4 animate-fade-in">
          <h4 className="text-lg font-semibold text-white">{editingTopic ? 'Edit Topic' : 'Add Topic'}</h4>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Topic Name</label>
            <input 
              type="text" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Weight (0-1)</label>
              <input 
                type="number" 
                step="0.01" 
                min="0" 
                max="1"
                value={weight}
                onChange={(e) => setWeight(parseFloat(e.target.value))}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Current Skill (0-100)</label>
              <input 
                type="number" 
                min="0" 
                max="100"
                value={skill}
                onChange={(e) => setSkill(parseFloat(e.target.value))}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button 
              type="button" 
              onClick={() => {
                setShowForm(false);
                setEditingTopic(null);
                setName('');
                setWeight(0.1);
                setSkill(50);
              }}
              className="px-4 py-2 text-gray-300 hover:text-white"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
            >
              {editingTopic ? 'Update Topic' : 'Save Topic'}
            </button>
          </div>
        </form>
      )}

      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-900/50 text-gray-400 text-sm">
            <tr>
              <th className="p-4">Topic</th>
              <th className="p-4">Weight</th>
              <th className="p-4">Skill Level</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {topics.map(topic => (
              <tr key={topic.id} className="hover:bg-gray-750 transition-colors">
                <td className="p-4 text-white font-medium">{topic.name}</td>
                <td className="p-4 text-gray-300">{(topic.weight * 100).toFixed(0)}%</td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${topic.skill_level > 70 ? 'bg-green-500' : topic.skill_level > 40 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                        style={{ width: `${topic.skill_level}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-400">{topic.skill_level}%</span>
                  </div>
                </td>
                <td className="p-4 text-right">
                  <div className="flex gap-2 justify-end">
                    <button 
                      onClick={() => handleEditTopic(topic)}
                      className="text-blue-400 hover:text-blue-300 transition-opacity"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button 
                      onClick={() => handleDeleteTopic(topic.id!)}
                      className="text-red-400 hover:text-red-300 transition-opacity"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {topics.length === 0 && (
              <tr>
                <td colSpan={4} className="p-8 text-center text-gray-500">
                  No topics yet. Add one to start tracking.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CourseDetail;

