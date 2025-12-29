import { useState, useEffect } from 'react';
import { Brain, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';
import { getCourses, getTopics, manualSkillAssessment, applySkillDecay, getDecayStatus, type Course, type Topic } from '../services/api';

const SkillManagement = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [newSkill, setNewSkill] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [decayStatus, setDecayStatus] = useState<any>(null);

  useEffect(() => {
    loadCourses();
    loadDecayStatus();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadTopics(selectedCourse);
    }
  }, [selectedCourse]);

  const loadCourses = async () => {
    try {
      const data = await getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses', error);
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

  const loadDecayStatus = async () => {
    try {
      const data = await getDecayStatus();
      setDecayStatus(data);
    } catch (error) {
      console.error('Failed to load decay status', error);
    }
  };

  const handleManualAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTopic) return;

    setLoading(true);
    try {
      await manualSkillAssessment(selectedTopic, parseFloat(newSkill), reason || 'Manual self-assessment');
      alert('Skill level updated successfully!');
      setNewSkill('');
      setReason('');
      loadTopics(selectedCourse!);
    } catch (error) {
      console.error('Failed to update skill', error);
      alert('Error updating skill level');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyDecay = async () => {
    if (!confirm('Apply skill decay to all inactive topics? This will reduce skill levels for topics not studied recently.')) {
      return;
    }

    setLoading(true);
    try {
      const result = await applySkillDecay();
      alert(`Skill decay applied to ${result.topics_affected} topics`);
      loadDecayStatus();
      if (selectedCourse) {
        loadTopics(selectedCourse);
      }
    } catch (error) {
      console.error('Failed to apply decay', error);
      alert('Error applying skill decay');
    } finally {
      setLoading(false);
    }
  };

  const currentTopic = topics.find(t => t.id === selectedTopic);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-white mb-6 flex items-center gap-2">
        <Brain className="w-8 h-8" />
        Skill Management
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Manual Assessment Section */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <CheckCircle className="w-6 h-6 text-green-400" />
            Manual Skill Assessment
          </h2>

          <form onSubmit={handleManualAssessment}>
            <div className="mb-4">
              <label className="block text-white mb-2">Select Course</label>
              <select
                value={selectedCourse || ''}
                onChange={(e) => {
                  setSelectedCourse(Number(e.target.value));
                  setSelectedTopic(null);
                }}
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
              >
                <option value="">Select Course</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>{course.name}</option>
                ))}
              </select>
            </div>

            {selectedCourse && (
              <div className="mb-4">
                <label className="block text-white mb-2">Select Topic</label>
                <select
                  value={selectedTopic || ''}
                  onChange={(e) => setSelectedTopic(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                >
                  <option value="">Select Topic</option>
                  {topics.map(topic => (
                    <option key={topic.id} value={topic.id}>
                      {topic.name} - Current: {topic.skill_level.toFixed(1)}%
                    </option>
                  ))}
                </select>
              </div>
            )}

            {currentTopic && (
              <>
                <div className="mb-4 p-4 bg-gray-700 rounded-lg">
                  <p className="text-gray-300">Current Skill Level</p>
                  <p className="text-3xl font-bold text-white">{currentTopic.skill_level.toFixed(1)}%</p>
                </div>

                <div className="mb-4">
                  <label className="block text-white mb-2">New Skill Level (0-100)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                    required
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-white mb-2">Reason (optional)</label>
                  <input
                    type="text"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="e.g., Completed practice problems"
                    className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !newSkill}
                  className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  Update Skill Level
                </button>

                {newSkill && Math.abs(parseFloat(newSkill) - currentTopic.skill_level) > 20 && (
                  <div className="mt-4 p-3 bg-yellow-900/50 border border-yellow-600 rounded-lg">
                    <p className="text-yellow-300 text-sm">
                      ⚠️ Large change detected ({Math.abs(parseFloat(newSkill) - currentTopic.skill_level).toFixed(1)} points). 
                      Manual assessments have reduced weight to prevent gaming.
                    </p>
                  </div>
                )}
              </>
            )}
          </form>
        </div>

        {/* Skill Decay Section */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingDown className="w-6 h-6 text-orange-400" />
            Skill Decay Management
          </h2>

          <div className="mb-6">
            <p className="text-gray-300 mb-4">
              Skills naturally decay when topics are not studied for 7+ days. 
              Decay rate: 0.5 points per day, max 30% of current skill.
            </p>

            <button
              onClick={handleApplyDecay}
              disabled={loading}
              className="w-full px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <TrendingDown className="w-5 h-5" />
              Apply Skill Decay Now
            </button>
          </div>

          {decayStatus && (
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Decay Status</h3>
              
              {decayStatus.eligible_topics && decayStatus.eligible_topics.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-gray-400 mb-3">
                    {decayStatus.eligible_topics.length} topic(s) eligible for decay:
                  </p>
                  {decayStatus.eligible_topics.map((topic: any) => (
                    <div key={topic.topic_id} className="p-3 bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-white font-medium">{topic.topic_name}</p>
                          <p className="text-gray-400 text-sm">
                            {topic.days_inactive} days inactive
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-white">{topic.current_skill.toFixed(1)}%</p>
                          <p className="text-orange-400 text-sm">
                            Will decay to {topic.skill_after_decay.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 bg-green-900/30 border border-green-600 rounded-lg">
                  <p className="text-green-300 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    No topics eligible for decay. Keep up the good work!
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-900/30 border border-blue-600 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-white font-semibold mb-2">About Skill Tracking</h3>
            <ul className="text-gray-300 space-y-1 text-sm">
              <li>• Quiz results automatically update skills (100% weight)</li>
              <li>• Manual assessments have reduced weight (50%) to prevent gaming</li>
              <li>• Skill decay applies after 7 days of inactivity</li>
              <li>• All changes are recorded in skill history</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillManagement;
