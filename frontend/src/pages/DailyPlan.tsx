import { useState } from 'react';
import { Clock, Zap, BookOpen } from 'lucide-react';
import { generatePlan, type StudyPlanResponse } from '../services/api';

const DailyPlan = () => {
  const [hours, setHours] = useState(2);
  const [adaptive, setAdaptive] = useState(true);
  const [plan, setPlan] = useState<StudyPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await generatePlan(hours, adaptive);
      setPlan(data);
    } catch (error) {
      console.error('Failed to generate plan', error);
      alert('Error generating plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Daily Study Plan</h2>

      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <form onSubmit={handleGenerate} className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-400 mb-1">Available Hours Today</label>
            <input 
              type="number" 
              step="0.5" 
              min="0.5" 
              value={hours}
              onChange={(e) => setHours(parseFloat(e.target.value))}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex items-center mb-3">
            <input 
              type="checkbox" 
              id="adaptive"
              checked={adaptive}
              onChange={(e) => setAdaptive(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600"
            />
            <label htmlFor="adaptive" className="ml-2 text-sm font-medium text-gray-300">Adaptive (Prioritize Weak Areas)</label>
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50 transition-colors"
          >
            <Zap size={20} />
            {loading ? 'Generating...' : 'Generate Plan'}
          </button>
        </form>
      </div>

      {plan && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex justify-between items-center text-gray-400">
            <span>Total Allocated: {plan.allocated_topics.reduce((sum, t) => sum + t.allocated_hours, 0).toFixed(1)}h</span>
            <span>{plan.allocated_topics.length} Topics</span>
          </div>

          <div className="grid gap-4">
            {plan.allocated_topics.map((item, index) => (
              <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:border-blue-500 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="bg-blue-500/20 p-3 rounded-lg text-blue-400 font-bold text-xl w-12 h-12 flex items-center justify-center">
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{item.topic.name}</h3>
                    <div className="text-sm text-gray-400 flex items-center gap-2">
                      <BookOpen size={14} /> {item.course.name}
                      <span className="text-gray-600">|</span>
                      <span>Skill: {item.topic.skill_level}%</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-6 w-full md:w-auto">
                  <div className="text-right">
                    <div className="text-xs text-gray-500 uppercase">Priority</div>
                    <div className="text-yellow-400 font-mono font-bold">{item.priority_score.toFixed(1)}</div>
                  </div>
                  
                  <div className="flex-1 md:flex-none bg-gray-700 rounded-lg p-2 px-4 flex items-center gap-2">
                    <Clock className="text-green-400" size={18} />
                    <span className="text-xl font-bold text-white">{item.allocated_hours.toFixed(1)}h</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {plan.allocated_topics.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No topics found to study. Ensure you have added courses and topics.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DailyPlan;

