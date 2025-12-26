import { Outlet, Link } from 'react-router-dom';
import { BookOpen, BarChart2, CheckSquare, Settings, Home } from 'lucide-react';

const Layout = () => {
  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Skill Planner
          </h1>
        </div>
        <nav className="p-4 space-y-2">
          <Link to="/" className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 transition-colors">
            <Home size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/courses" className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 transition-colors">
            <BookOpen size={20} />
            <span>Courses</span>
          </Link>
          <Link to="/plan" className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 transition-colors">
            <CheckSquare size={20} />
            <span>Daily Plan</span>
          </Link>
          <Link to="/progress" className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 transition-colors">
            <BarChart2 size={20} />
            <span>Progress</span>
          </Link>
          <div className="pt-4 border-t border-gray-700">
             <Link to="/settings" className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 text-gray-400 transition-colors">
              <Settings size={20} />
              <span>Settings</span>
            </Link>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gray-900">
        <header className="h-16 border-b border-gray-700 flex items-center px-8 bg-gray-800/50 backdrop-blur sticky top-0 z-10">
          <div className="flex-1"></div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-400">
              Honesty Mode: <span className="text-green-400">Constructive</span>
            </div>
          </div>
        </header>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;

