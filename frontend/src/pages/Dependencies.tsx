import { useState, useEffect } from 'react';
import { GitBranch, Plus, Trash2, ArrowRight, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';
import { getCourses, getTopics, type Course, type Topic } from '../services/api';

const api = axios.create({ baseURL: '/api' });

type Dependency = {
  id: number;
  prerequisite_topic_id: number;
  dependent_topic_id: number;
  min_skill_threshold: number;
};

type DependencyGraph = {
  nodes: Array<{
    id: number;
    name: string;
    skill_level: number;
  }>;
  edges: Array<{
    from: number;
    to: number;
    threshold: number;
  }>;
};

const Dependencies = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [graph, setGraph] = useState<DependencyGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);

  // Form state
  const [prerequisiteId, setPrerequisiteId] = useState<number | null>(null);
  const [dependentId, setDependentId] = useState<number | null>(null);
  const [threshold, setThreshold] = useState(70);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [coursesData, graphData] = await Promise.all([
        getCourses(),
        api.get('/dependencies').then(r => r.data)
      ]);
      
      setCourses(coursesData);
      setGraph(graphData);

      // Load all topics
      const allTopics: Topic[] = [];
      for (const course of coursesData) {
        const topicsData = await getTopics(course.id);
        allTopics.push(...topicsData);
      }
      setTopics(allTopics);
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDependency = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prerequisiteId || !dependentId) return;

    try {
      await api.post('/dependencies', {
        prerequisite_topic_id: prerequisiteId,
        dependent_topic_id: dependentId,
        min_skill_threshold: threshold
      });
      
      setShowAddForm(false);
      setPrerequisiteId(null);
      setDependentId(null);
      setThreshold(70);
      loadData();
    } catch (error: any) {
      console.error('Failed to add dependency', error);
      alert(error.response?.data?.detail || 'Failed to add dependency');
    }
  };

  const handleDeleteDependency = async (depId: number) => {
    if (!confirm('Delete this dependency?')) return;

    try {
      await api.delete(`/dependencies/${depId}`);
      loadData();
    } catch (error) {
      console.error('Failed to delete dependency', error);
      alert('Failed to delete dependency');
    }
  };

  const getTopicName = (topicId: number) => {
    const topic = topics.find(t => t.id === topicId);
    return topic?.name || `Topic ${topicId}`;
  };

  const getTopicSkill = (topicId: number) => {
    const topic = topics.find(t => t.id === topicId);
    return topic?.skill_level || 0;
  };

  if (loading) return <div className="text-white p-6">Loading...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
          <GitBranch className="w-8 h-8" />
          Topic Dependencies
        </h1>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Dependency
        </button>
      </div>

      {/* Add Dependency Form */}
      {showAddForm && (
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4">Add New Dependency</h2>
          <form onSubmit={handleAddDependency}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-white mb-2">Prerequisite Topic</label>
                <select
                  value={prerequisiteId || ''}
                  onChange={(e) => setPrerequisiteId(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  required
                >
                  <option value="">Select prerequisite</option>
                  {topics.map(topic => (
                    <option key={topic.id} value={topic.id}>
                      {topic.name} (Skill: {topic.skill_level.toFixed(1)}%)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-white mb-2">Dependent Topic</label>
                <select
                  value={dependentId || ''}
                  onChange={(e) => setDependentId(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  required
                >
                  <option value="">Select dependent</option>
                  {topics.filter(t => t.id !== prerequisiteId).map(topic => (
                    <option key={topic.id} value={topic.id}>
                      {topic.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-white mb-2">Min Skill Threshold (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  required
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Add Dependency
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </form>

          {prerequisiteId && dependentId && (
            <div className="mt-4 p-3 bg-blue-900/30 border border-blue-600 rounded-lg">
              <p className="text-blue-300 text-sm">
                <strong>{getTopicName(prerequisiteId)}</strong> must reach {threshold}% skill 
                before <strong>{getTopicName(dependentId)}</strong> can be studied effectively.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Dependencies List */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-4">All Dependencies</h2>
        
        {graph && graph.edges.length > 0 ? (
          <div className="space-y-3">
            {graph.edges.map((edge, index) => {
              const prereqSkill = getTopicSkill(edge.from);
              const isSatisfied = prereqSkill >= edge.threshold;
              
              return (
                <div key={index} className="p-4 bg-gray-700 rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-white font-medium">{getTopicName(edge.from)}</p>
                        <p className="text-sm text-gray-400">Skill: {prereqSkill.toFixed(1)}%</p>
                      </div>
                      
                      {isSatisfied ? (
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      ) : (
                        <XCircle className="w-6 h-6 text-red-400" />
                      )}
                    </div>

                    <ArrowRight className="w-6 h-6 text-gray-400" />

                    <div>
                      <p className="text-white font-medium">{getTopicName(edge.to)}</p>
                      <p className="text-sm text-gray-400">
                        Requires: {edge.threshold}% {isSatisfied ? '✓ Met' : '✗ Not Met'}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      // Find dependency ID (we need to make this available in the API response)
                      // For now, we'll refresh after delete
                      const dep = graph.edges[index];
                      if (confirm(`Delete this dependency?`)) {
                        // We need to get the actual dependency ID from backend
                        // This is a simplified version
                        alert('Delete functionality needs dependency ID from backend');
                      }
                    }}
                    className="p-2 text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-gray-400">No dependencies defined yet. Add one to get started!</p>
        )}
      </div>

      {/* Dependency Graph Visualization */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">Dependency Graph</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {graph && graph.nodes.map(node => {
            const prerequisites = graph.edges.filter(e => e.to === node.id);
            const dependents = graph.edges.filter(e => e.from === node.id);

            if (prerequisites.length === 0 && dependents.length === 0) return null;

            return (
              <div key={node.id} className="p-4 bg-gray-700 rounded-lg">
                <h3 className="text-white font-semibold mb-2">{node.name}</h3>
                <p className="text-gray-400 text-sm mb-3">Skill: {node.skill_level.toFixed(1)}%</p>

                {prerequisites.length > 0 && (
                  <div className="mb-2">
                    <p className="text-gray-400 text-sm font-medium mb-1">Prerequisites:</p>
                    <ul className="space-y-1">
                      {prerequisites.map((prereq, idx) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-center gap-2">
                          <ArrowRight className="w-4 h-4" />
                          {getTopicName(prereq.from)} ({prereq.threshold}%)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {dependents.length > 0 && (
                  <div>
                    <p className="text-gray-400 text-sm font-medium mb-1">Unlocks:</p>
                    <ul className="space-y-1">
                      {dependents.map((dep, idx) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-center gap-2">
                          <ArrowRight className="w-4 h-4" />
                          {getTopicName(dep.to)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dependencies;
