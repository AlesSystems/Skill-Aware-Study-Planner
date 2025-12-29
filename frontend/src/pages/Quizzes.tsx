import { useState, useEffect } from 'react';
import { Plus, BookOpen, CheckCircle, XCircle, Clock } from 'lucide-react';
import { getCourses, getTopics, getTopicQuizzes, createQuiz, attemptQuiz, getQuizAttempts, type Course, type Topic, type Quiz, type QuizQuestion, type QuizAttempt } from '../services/api';

const Quizzes = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeView, setActiveView] = useState<'list' | 'create' | 'take' | 'results'>('list');
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);
  const [quizAttempts, setQuizAttempts] = useState<QuizAttempt[]>([]);

  // Create quiz state
  const [quizTitle, setQuizTitle] = useState('');
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);

  // Take quiz state
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [quizResult, setQuizResult] = useState<QuizAttempt | null>(null);

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadTopics(selectedCourse);
    }
  }, [selectedCourse]);

  useEffect(() => {
    if (selectedTopic) {
      loadQuizzes(selectedTopic);
    }
  }, [selectedTopic]);

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

  const loadTopics = async (courseId: number) => {
    try {
      const data = await getTopics(courseId);
      setTopics(data);
    } catch (error) {
      console.error('Failed to load topics', error);
    }
  };

  const loadQuizzes = async (topicId: number) => {
    try {
      const data = await getTopicQuizzes(topicId);
      setQuizzes(data);
    } catch (error) {
      console.error('Failed to load quizzes', error);
    }
  };

  const addQuestion = () => {
    setQuestions([...questions, {
      question_text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_answer: 'A'
    }]);
  };

  const updateQuestion = (index: number, field: keyof QuizQuestion, value: string) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], [field]: value };
    setQuestions(updated);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const handleCreateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTopic) return;

    try {
      await createQuiz({
        topic_id: selectedTopic,
        title: quizTitle,
        questions
      });
      setQuizTitle('');
      setQuestions([]);
      setShowCreateForm(false);
      setActiveView('list');
      loadQuizzes(selectedTopic);
    } catch (error) {
      console.error('Failed to create quiz', error);
      alert('Error creating quiz');
    }
  };

  const handleTakeQuiz = async (quiz: Quiz) => {
    setSelectedQuiz(quiz);
    setUserAnswers({});
    setQuizResult(null);
    setActiveView('take');
  };

  const handleSubmitQuiz = async () => {
    if (!selectedQuiz) return;

    try {
      const result = await attemptQuiz(selectedQuiz.id!, userAnswers);
      setQuizResult(result);
      setActiveView('results');
      if (selectedTopic) {
        loadQuizzes(selectedTopic);
      }
    } catch (error) {
      console.error('Failed to submit quiz', error);
      alert('Error submitting quiz');
    }
  };

  const handleViewAttempts = async (quiz: Quiz) => {
    try {
      const attempts = await getQuizAttempts(quiz.id!);
      setQuizAttempts(attempts);
      setSelectedQuiz(quiz);
      setActiveView('results');
    } catch (error) {
      console.error('Failed to load attempts', error);
    }
  };

  if (loading) return <div className="text-white p-6">Loading...</div>;

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-4 flex items-center gap-2">
          <BookOpen className="w-8 h-8" />
          Quizzes
        </h1>

        {/* Course & Topic Selection */}
        <div className="flex gap-4 mb-4">
          <select
            value={selectedCourse || ''}
            onChange={(e) => {
              setSelectedCourse(Number(e.target.value));
              setSelectedTopic(null);
            }}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg"
          >
            <option value="">Select Course</option>
            {courses.map(course => (
              <option key={course.id} value={course.id}>{course.name}</option>
            ))}
          </select>

          {selectedCourse && (
            <select
              value={selectedTopic || ''}
              onChange={(e) => setSelectedTopic(Number(e.target.value))}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg"
            >
              <option value="">Select Topic</option>
              {topics.map(topic => (
                <option key={topic.id} value={topic.id}>{topic.name}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {activeView === 'list' && selectedTopic && (
        <div>
          <div className="mb-4 flex gap-4">
            <button
              onClick={() => {
                setShowCreateForm(true);
                setActiveView('create');
              }}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <Plus className="w-5 h-5" />
              Create Quiz
            </button>
          </div>

          <div className="grid gap-4">
            {quizzes.length === 0 ? (
              <p className="text-gray-400">No quizzes yet. Create one to get started!</p>
            ) : (
              quizzes.map(quiz => (
                <div key={quiz.id} className="bg-gray-800 rounded-lg p-6">
                  <h3 className="text-xl font-semibold text-white mb-2">{quiz.title}</h3>
                  <p className="text-gray-400 mb-4">{quiz.questions.length} questions</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleTakeQuiz(quiz)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Take Quiz
                    </button>
                    <button
                      onClick={() => handleViewAttempts(quiz)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      View Attempts
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeView === 'create' && (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-white">Create New Quiz</h2>
            <button
              onClick={() => {
                setActiveView('list');
                setShowCreateForm(false);
              }}
              className="text-gray-400 hover:text-white"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleCreateQuiz}>
            <div className="mb-4">
              <label className="block text-white mb-2">Quiz Title</label>
              <input
                type="text"
                value={quizTitle}
                onChange={(e) => setQuizTitle(e.target.value)}
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                required
              />
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-xl text-white">Questions</h3>
                <button
                  type="button"
                  onClick={addQuestion}
                  className="px-3 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              {questions.map((q, index) => (
                <div key={index} className="mb-6 p-4 bg-gray-700 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-white font-semibold">Question {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeQuestion(index)}
                      className="text-red-400 hover:text-red-600"
                    >
                      Remove
                    </button>
                  </div>

                  <input
                    type="text"
                    placeholder="Question text"
                    value={q.question_text}
                    onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-600 text-white rounded mb-2"
                    required
                  />

                  <div className="grid grid-cols-2 gap-2 mb-2">
                    <input
                      type="text"
                      placeholder="Option A"
                      value={q.option_a}
                      onChange={(e) => updateQuestion(index, 'option_a', e.target.value)}
                      className="px-3 py-2 bg-gray-600 text-white rounded"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Option B"
                      value={q.option_b}
                      onChange={(e) => updateQuestion(index, 'option_b', e.target.value)}
                      className="px-3 py-2 bg-gray-600 text-white rounded"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Option C"
                      value={q.option_c}
                      onChange={(e) => updateQuestion(index, 'option_c', e.target.value)}
                      className="px-3 py-2 bg-gray-600 text-white rounded"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Option D"
                      value={q.option_d}
                      onChange={(e) => updateQuestion(index, 'option_d', e.target.value)}
                      className="px-3 py-2 bg-gray-600 text-white rounded"
                      required
                    />
                  </div>

                  <select
                    value={q.correct_answer}
                    onChange={(e) => updateQuestion(index, 'correct_answer', e.target.value)}
                    className="px-3 py-2 bg-gray-600 text-white rounded"
                  >
                    <option value="A">A is correct</option>
                    <option value="B">B is correct</option>
                    <option value="C">C is correct</option>
                    <option value="D">D is correct</option>
                  </select>
                </div>
              ))}
            </div>

            <button
              type="submit"
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              disabled={questions.length === 0}
            >
              Create Quiz
            </button>
          </form>
        </div>
      )}

      {activeView === 'take' && selectedQuiz && (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-white">{selectedQuiz.title}</h2>
            <button
              onClick={() => setActiveView('list')}
              className="text-gray-400 hover:text-white"
            >
              Cancel
            </button>
          </div>

          {selectedQuiz.questions.map((q, index) => (
            <div key={q.id || index} className="mb-6 p-4 bg-gray-700 rounded-lg">
              <h3 className="text-white font-semibold mb-3">
                {index + 1}. {q.question_text}
              </h3>
              <div className="space-y-2">
                {['A', 'B', 'C', 'D'].map(option => (
                  <label key={option} className="flex items-center gap-2 text-white cursor-pointer hover:bg-gray-600 p-2 rounded">
                    <input
                      type="radio"
                      name={`question-${q.id || index}`}
                      value={option}
                      checked={userAnswers[q.id || index] === option}
                      onChange={() => setUserAnswers({ ...userAnswers, [q.id || index]: option })}
                    />
                    <span>{option}. {q[`option_${option.toLowerCase()}` as keyof QuizQuestion]}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}

          <button
            onClick={handleSubmitQuiz}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            disabled={Object.keys(userAnswers).length !== selectedQuiz.questions.length}
          >
            Submit Quiz
          </button>
        </div>
      )}

      {activeView === 'results' && (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-white">Quiz Results</h2>
            <button
              onClick={() => setActiveView('list')}
              className="text-gray-400 hover:text-white"
            >
              Back to List
            </button>
          </div>

          {quizResult && (
            <div className="mb-6 p-6 bg-gray-700 rounded-lg">
              <div className="text-center">
                <div className={`text-6xl font-bold mb-4 ${quizResult.score >= 70 ? 'text-green-400' : 'text-red-400'}`}>
                  {quizResult.score.toFixed(1)}%
                </div>
                <p className="text-gray-300 text-lg">
                  You scored {quizResult.score.toFixed(1)}% on this quiz
                </p>
              </div>
            </div>
          )}

          {quizAttempts.length > 0 && (
            <div>
              <h3 className="text-xl text-white mb-4">Previous Attempts</h3>
              <div className="space-y-2">
                {quizAttempts.map(attempt => (
                  <div key={attempt.id} className="p-4 bg-gray-700 rounded-lg flex justify-between items-center">
                    <div>
                      <p className="text-white">
                        {new Date(attempt.attempted_at).toLocaleDateString()} at {new Date(attempt.attempted_at).toLocaleTimeString()}
                      </p>
                    </div>
                    <div className={`text-2xl font-bold ${attempt.score >= 70 ? 'text-green-400' : 'text-red-400'}`}>
                      {attempt.score.toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Quizzes;
