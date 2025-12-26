import { useState, useEffect } from 'react';
import { getExpectedScores, getRisks, type ExpectedScore, type Risk } from '../services/api';
import { AlertTriangle, CheckCircle, TrendingUp, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [scores, setScores] = useState<Record<string, ExpectedScore>>({});
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [scoresData, risksData] = await Promise.all([
        getExpectedScores(),
        getRisks()
      ]);
      setScores(scoresData);
      setRisks(risksData);
    } catch (error) {
      console.error('Failed to load dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-white p-6">Loading...</div>;

  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold text-white">Exam Readiness Dashboard</h2>

      {/* Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(scores).map(([courseId, data]) => (
          <div key={courseId} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-2">{data.course_name}</h3>
            <div className="flex items-end gap-2 mb-4">
              <span className={`text-4xl font-bold ${data.estimated_score >= 60 ? 'text-green-400' : 'text-red-400'}`}>
                {data.estimated_score.toFixed(1)}%
              </span>
              <span className="text-gray-400 mb-1">Estimated Score</span>
            </div>
            
            <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
              <div 
                className={`h-2 rounded-full ${data.estimated_score >= 60 ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${Math.min(data.estimated_score, 100)}%` }}
              ></div>
            </div>

            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex justify-between">
                <span>Range</span>
                <span>{data.score_range[0].toFixed(1)}% - {data.score_range[1].toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Coverage</span>
                <span>{(data.total_weight_coverage * 100).toFixed(0)}%</span>
              </div>
              {data.dependency_penalty > 0 && (
                 <div className="flex justify-between text-red-400">
                  <span>Penalty</span>
                  <span>-{data.dependency_penalty.toFixed(1)}%</span>
                </div>
              )}
            </div>
          </div>
        ))}
        {Object.keys(scores).length === 0 && (
          <div className="col-span-full bg-gray-800 p-6 rounded-lg border border-gray-700 text-center text-gray-500">
            No courses data available. Add courses and topics to see predictions.
          </div>
        )}
      </div>

      {/* Risks Section */}
      {risks.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertCircle className="text-red-500" /> Risks & Warnings
          </h3>
          <div className="space-y-4">
            {risks.map((risk, index) => (
              <div key={index} className="flex items-start gap-4 p-4 bg-gray-700/30 rounded-lg border border-gray-700/50">
                <div className={`
                  p-2 rounded-full 
                  ${risk.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : 
                    risk.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400' : 
                    'bg-yellow-500/20 text-yellow-400'}
                `}>
                  <AlertTriangle size={20} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded 
                      ${risk.severity === 'CRITICAL' ? 'bg-red-500 text-white' : 
                        risk.severity === 'HIGH' ? 'bg-orange-500 text-white' : 
                        'bg-yellow-500 text-black'}
                    `}>
                      {risk.severity}
                    </span>
                    <span className="text-gray-400 text-sm">{risk.type}</span>
                  </div>
                  <p className="text-white font-medium">{risk.description}</p>
                  <p className="text-sm text-gray-500 mt-1">{risk.course}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link to="/plan" className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg flex flex-col items-center justify-center gap-2 transition-colors">
          <CheckCircle size={24} />
          <span className="font-bold">Generate Plan</span>
        </Link>
        <Link to="/courses" className="bg-gray-700 hover:bg-gray-600 text-white p-4 rounded-lg flex flex-col items-center justify-center gap-2 transition-colors">
          <TrendingUp size={24} />
          <span className="font-bold">Manage Courses</span>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
