import { useState, useEffect } from 'react';
import { Plus, Calendar, Book, Trash2 } from 'lucide-react';
import { getCourses, createCourse, deleteCourse, type Course } from '../services/api';
import { Link } from 'react-router-dom';

const Courses = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  // Form state
  const [newName, setNewName] = useState('');
  const [newDate, setNewDate] = useState('');

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Ensure date is formatted correctly if needed, but input type="date" returns YYYY-MM-DD which is usually fine
      await createCourse({
        name: newName,
        exam_date: newDate, 
      });
      setShowForm(false);
      setNewName('');
      setNewDate('');
      loadCourses();
    } catch (error) {
      console.error('Failed to create course', error);
      alert('Error creating course. Ensure exam date is in the future.');
    }
  };

  const handleDelete = async (e: React.MouseEvent, courseId: number, courseName: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!confirm(`Delete course "${courseName}"? This will also delete all associated topics and data.`)) {
      return;
    }

    try {
      await deleteCourse(courseId);
      loadCourses();
    } catch (error) {
      console.error('Failed to delete course', error);
      alert('Error deleting course');
    }
  };

  if (loading) return <div className="text-white p-6">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Courses</h2>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus size={20} />
          Add Course
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-gray-800 p-6 rounded-lg border border-gray-700 space-y-4 animate-fade-in">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Course Name</label>
            <input 
              type="text" 
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Exam Date</label>
            <input 
              type="date" 
              value={newDate}
              onChange={(e) => setNewDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <button 
              type="button" 
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-gray-300 hover:text-white"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
            >
              Save Course
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map(course => (
          <div key={course.id} className="relative group">
            <Link 
              to={`/courses/${course.id}`} 
              className="block bg-gray-800 p-6 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <Book className="text-blue-400" size={24} />
                </div>
                <span className="text-xs font-mono text-gray-500">ID: {course.id}</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{course.name}</h3>
              <div className="flex items-center text-gray-400 text-sm">
                <Calendar size={16} className="mr-2" />
                {new Date(course.exam_date).toLocaleDateString()}
              </div>
            </Link>
            <button
              onClick={(e) => handleDelete(e, course.id, course.name)}
              className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-700"
              title="Delete course"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
      
      {courses.length === 0 && !showForm && (
        <div className="text-center text-gray-500 py-12">
          No courses found. Create one to get started!
        </div>
      )}
    </div>
  );
};

export default Courses;
