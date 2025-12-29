import { useState } from 'react';
import { Sparkles, TrendingUp, Calendar, Target, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

const Scenarios = () => {
  const [scenarioType, setScenarioType] = useState<'hours' | 'strategies' | 'skip'>('hours');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Hours change scenario
  const [currentHours, setCurrentHours] = useState(3);
  const [newHours, setNewHours] = useState(5);

  // Strategy comparison
  const [availableHours, setAvailableHours] = useState(4);

  // Skip suggestions
  const [skipHours, setSkipHours] = useState(3);

  const runHoursChangeScenario = async () => {
    setLoading(true);
    try {
      const response = await api.post('/scenarios/simulate', {
        scenario_type: 'hours_change',
        params: {
          current_hours: currentHours,
          new_hours: newHours
        }
      });
      setResult(response.data);
    } catch (error) {
      console.error('Failed to run scenario', error);
      alert('Error running scenario');
    } finally {
      setLoading(false);
    }
  };

  const runStrategyComparison = async () => {
    setLoading(true);
    try {
      const response = await api.post('/scenarios/compare-strategies', {
        available_hours: availableHours
      });
      setResult(response.data);
    } catch (error) {
      console.error('Failed to run scenario', error);
      alert('Error running scenario');
    } finally {
      setLoading(false);
    }
  };

  const runSkipSuggestions = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/scenarios/skip-suggestions?available_hours=${skipHours}`);
      setResult(response.data);
    } catch (error) {
      console.error('Failed to get suggestions', error);
      alert('Error getting suggestions');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-white mb-6 flex items-center gap-2">
        <Sparkles className="w-8 h-8" />
        What-If Scenarios
      </h1>

      {/* Scenario Type Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <button
          onClick={() => {
            setScenarioType('hours');
            setResult(null);
          }}
          className={`p-4 rounded-lg border-2 transition-colors ${
            scenarioType === 'hours'
              ? 'bg-purple-600 border-purple-400'
              : 'bg-gray-800 border-gray-700 hover:border-gray-600'
          }`}
        >
          <TrendingUp className="w-8 h-8 mb-2 mx-auto text-white" />
          <h3 className="text-white font-semibold">Study Hours Change</h3>
          <p className="text-gray-400 text-sm mt-1">
            See impact of different daily study time
          </p>
        </button>

        <button
          onClick={() => {
            setScenarioType('strategies');
            setResult(null);
          }}
          className={`p-4 rounded-lg border-2 transition-colors ${
            scenarioType === 'strategies'
              ? 'bg-purple-600 border-purple-400'
              : 'bg-gray-800 border-gray-700 hover:border-gray-600'
          }`}
        >
          <Target className="w-8 h-8 mb-2 mx-auto text-white" />
          <h3 className="text-white font-semibold">Strategy Comparison</h3>
          <p className="text-gray-400 text-sm mt-1">
            Compare balanced vs focused approaches
          </p>
        </button>

        <button
          onClick={() => {
            setScenarioType('skip');
            setResult(null);
          }}
          className={`p-4 rounded-lg border-2 transition-colors ${
            scenarioType === 'skip'
              ? 'bg-purple-600 border-purple-400'
              : 'bg-gray-800 border-gray-700 hover:border-gray-600'
          }`}
        >
          <AlertTriangle className="w-8 h-8 mb-2 mx-auto text-white" />
          <h3 className="text-white font-semibold">Skip Suggestions</h3>
          <p className="text-gray-400 text-sm mt-1">
            Topics you might consider skipping
          </p>
        </button>
      </div>

      {/* Scenario Input Forms */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        {scenarioType === 'hours' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">Study Hours Change Simulation</h2>
            <p className="text-gray-400 mb-4">
              See how changing your daily study time affects topic coverage and expected scores.
            </p>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-white mb-2">Current Daily Hours</label>
                <input
                  type="number"
                  min="0"
                  max="24"
                  step="0.5"
                  value={currentHours}
                  onChange={(e) => setCurrentHours(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                />
              </div>

              <div>
                <label className="block text-white mb-2">New Daily Hours</label>
                <input
                  type="number"
                  min="0"
                  max="24"
                  step="0.5"
                  value={newHours}
                  onChange={(e) => setNewHours(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                />
              </div>
            </div>

            <button
              onClick={runHoursChangeScenario}
              disabled={loading}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        )}

        {scenarioType === 'strategies' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">Strategy Comparison</h2>
            <p className="text-gray-400 mb-4">
              Compare different study strategies: balanced approach, high-weight focus, and weak-topic focus.
            </p>

            <div className="mb-4">
              <label className="block text-white mb-2">Available Daily Hours</label>
              <input
                type="number"
                min="0"
                max="24"
                step="0.5"
                value={availableHours}
                onChange={(e) => setAvailableHours(Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
              />
            </div>

            <button
              onClick={runStrategyComparison}
              disabled={loading}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? 'Comparing...' : 'Compare Strategies'}
            </button>
          </div>
        )}

        {scenarioType === 'skip' && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-4">Skip Topic Suggestions</h2>
            <p className="text-gray-400 mb-4">
              Get suggestions for topics you might consider skipping based on low weight and time constraints.
            </p>

            <div className="mb-4">
              <label className="block text-white mb-2">Available Daily Hours</label>
              <input
                type="number"
                min="0"
                max="24"
                step="0.5"
                value={skipHours}
                onChange={(e) => setSkipHours(Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
              />
            </div>

            <button
              onClick={runSkipSuggestions}
              disabled={loading}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Get Suggestions'}
            </button>
          </div>
        )}
      </div>

      {/* Results Display */}
      {result && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-yellow-400" />
            Simulation Results
          </h2>

          {scenarioType === 'hours' && result.scenario === 'study_hours_change' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-gray-700 rounded-lg">
                  <p className="text-gray-400 text-sm">Current Coverage</p>
                  <p className="text-2xl font-bold text-white">{result.current_topics_covered}</p>
                  <p className="text-gray-400 text-xs">topics</p>
                </div>

                <div className="p-4 bg-gray-700 rounded-lg">
                  <p className="text-gray-400 text-sm">New Coverage</p>
                  <p className="text-2xl font-bold text-white">{result.new_topics_covered}</p>
                  <p className="text-gray-400 text-xs">topics</p>
                </div>

                <div className="p-4 bg-gray-700 rounded-lg">
                  <p className="text-gray-400 text-sm">Topics Gained</p>
                  <p className="text-2xl font-bold text-green-400">+{result.topics_gained}</p>
                </div>

                <div className="p-4 bg-gray-700 rounded-lg">
                  <p className="text-gray-400 text-sm">Topics Lost</p>
                  <p className="text-2xl font-bold text-red-400">-{result.topics_lost}</p>
                </div>
              </div>

              <div className="p-4 bg-blue-900/30 border border-blue-600 rounded-lg">
                <p className="text-blue-300">
                  <strong>Recommendation:</strong> {result.recommendation === 'increase_hours' 
                    ? 'Increasing study hours will improve coverage' 
                    : 'Maintain current study hours'}
                </p>
              </div>
            </div>
          )}

          {scenarioType === 'strategies' && result.strategies && (
            <div className="space-y-4">
              {Object.entries(result.strategies).map(([key, strategy]: [string, any]) => (
                <div key={key} className="p-4 bg-gray-700 rounded-lg">
                  <h3 className="text-xl font-bold text-white mb-2">{strategy.name}</h3>
                  <p className="text-gray-300 mb-3">{strategy.description}</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-gray-400 text-sm">Topics Covered</p>
                      <p className="text-2xl font-bold text-white">{strategy.topics_covered}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm">Expected Score</p>
                      <p className="text-2xl font-bold text-white">
                        {Object.values(strategy.expected_scores).reduce((a: any, b: any) => a + b.estimated_score, 0).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {result.best_strategy_name && (
                <div className="p-4 bg-green-900/30 border border-green-600 rounded-lg">
                  <p className="text-green-300">
                    <strong>🏆 Best Strategy:</strong> {result.best_strategy_name}
                  </p>
                  <p className="text-green-200 text-sm mt-1">{result.reason}</p>
                </div>
              )}
            </div>
          )}

          {scenarioType === 'skip' && Array.isArray(result) && (
            <div>
              {result.length > 0 ? (
                <div className="space-y-3">
                  <p className="text-gray-400 mb-4">
                    Based on your available time, consider skipping these {result.length} topics:
                  </p>
                  {result.map((suggestion: any, index: number) => (
                    <div key={index} className="p-4 bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-white font-semibold">{suggestion.topic}</h4>
                          <p className="text-gray-400 text-sm mt-1">{suggestion.reason}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-gray-400 text-sm">Weight: {(suggestion.weight * 100).toFixed(1)}%</p>
                          <p className="text-gray-400 text-sm">Skill: {suggestion.skill_level.toFixed(1)}%</p>
                          <p className="text-green-400 text-sm">Save: {suggestion.time_saved_estimate.toFixed(1)}h</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 bg-green-900/30 border border-green-600 rounded-lg">
                  <p className="text-green-300">
                    ✓ No topics recommended to skip. You have adequate time!
                  </p>
                </div>
              )}
            </div>
          )}

          <div className="mt-4">
            <pre className="text-xs text-gray-400 bg-gray-900 p-4 rounded-lg overflow-auto max-h-96">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default Scenarios;
