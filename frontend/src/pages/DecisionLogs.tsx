import { useState, useEffect } from 'react';
import { BookOpenCheck, Filter, Clock, Info } from 'lucide-react';
import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

type DecisionLog = {
  id: number;
  timestamp: string;
  decision_type: string;
  topic_id: number | null;
  explanation: string;
  metadata: any;
};

const DecisionLogs = () => {
  const [logs, setLogs] = useState<DecisionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    loadLogs();
  }, [limit, filterType]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      let response;
      if (filterType === 'all') {
        response = await api.get(`/decision-logs?limit=${limit}`);
      } else {
        response = await api.get(`/decision-logs/type/${filterType}?limit=${limit}`);
      }
      setLogs(response.data);
    } catch (error) {
      console.error('Failed to load decision logs', error);
    } finally {
      setLoading(false);
    }
  };

  const getDecisionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'priority_boost': 'bg-blue-900/30 border-blue-600 text-blue-300',
      'priority_reduction': 'bg-orange-900/30 border-orange-600 text-orange-300',
      'topic_allocation': 'bg-green-900/30 border-green-600 text-green-300',
      'skill_decay': 'bg-red-900/30 border-red-600 text-red-300',
      'dependency_block': 'bg-purple-900/30 border-purple-600 text-purple-300',
      'default': 'bg-gray-700 border-gray-600 text-gray-300'
    };
    return colors[type] || colors['default'];
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  if (loading) return <div className="text-white p-6">Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-white mb-6 flex items-center gap-2">
        <BookOpenCheck className="w-8 h-8" />
        Decision Logs
      </h1>

      <p className="text-gray-400 mb-6">
        View the reasoning behind all planning decisions made by the system.
        This helps you understand why certain topics were prioritized or deprioritized.
      </p>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <label className="text-white">Filter by type:</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg"
            >
              <option value="all">All Types</option>
              <option value="priority_boost">Priority Boost</option>
              <option value="priority_reduction">Priority Reduction</option>
              <option value="topic_allocation">Topic Allocation</option>
              <option value="skill_decay">Skill Decay</option>
              <option value="dependency_block">Dependency Block</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-white">Show:</label>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg"
            >
              <option value="10">Last 10</option>
              <option value="20">Last 20</option>
              <option value="50">Last 50</option>
              <option value="100">Last 100</option>
            </select>
          </div>

          <button
            onClick={loadLogs}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Decision Logs List */}
      <div className="space-y-3">
        {logs.length > 0 ? (
          logs.map((log) => (
            <div
              key={log.id}
              className={`border-2 rounded-lg p-4 ${getDecisionTypeColor(log.decision_type)}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-3 py-1 bg-gray-900/50 rounded-full text-sm font-medium">
                      {log.decision_type.replace(/_/g, ' ').toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-400 flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatTimestamp(log.timestamp)}
                    </span>
                  </div>

                  <p className="text-white mb-2">{log.explanation}</p>

                  {log.metadata && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm text-gray-400 hover:text-gray-300 flex items-center gap-1">
                        <Info className="w-4 h-4" />
                        Show Details
                      </summary>
                      <div className="mt-2 p-3 bg-gray-900/50 rounded-lg">
                        <pre className="text-xs text-gray-400 overflow-auto">
                          {JSON.stringify(log.metadata, null, 2)}
                        </pre>
                      </div>
                    </details>
                  )}
                </div>

                <div className="text-right">
                  <p className="text-xs text-gray-400">Log ID</p>
                  <p className="text-sm font-mono text-gray-300">#{log.id}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-gray-800 rounded-lg p-8 text-center">
            <p className="text-gray-400">No decision logs found.</p>
            <p className="text-gray-500 text-sm mt-2">
              Decision logs are created when the planner makes priority adjustments.
            </p>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-900/30 border border-blue-600 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Info className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-white font-semibold mb-2">About Decision Logs</h3>
            <ul className="text-gray-300 space-y-1 text-sm">
              <li>• <strong>Priority Boost:</strong> Topic priority increased due to low skill or high urgency</li>
              <li>• <strong>Priority Reduction:</strong> Topic deprioritized due to over-studying or low weight</li>
              <li>• <strong>Topic Allocation:</strong> Time allocated during daily plan generation</li>
              <li>• <strong>Skill Decay:</strong> Skill level reduced due to inactivity</li>
              <li>• <strong>Dependency Block:</strong> Topic blocked due to unmet prerequisites</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DecisionLogs;
