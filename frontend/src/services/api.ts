import axios from 'axios';

// Since we have proxy setup in vite.config.ts
const api = axios.create({
  baseURL: '/api',
});

export type Course = {
  id: number;
  name: string;
  exam_date: string;
};

export type Topic = {
  id: number;
  course_id: number;
  name: string;
  weight: number;
  skill_level: number;
};

export type AllocatedTopic = {
  topic: Topic;
  course: Course;
  priority_score: number;
  urgency_factor: number;
  allocated_hours: number;
};

export type StudyPlanResponse = {
  daily_hours: number;
  allocated_topics: AllocatedTopic[];
};

export type SkillHistory = {
  id: number;
  topic_id: number;
  timestamp: string;
  previous_skill: number;
  new_skill: number;
  reason: string;
};

export type WeakTopic = {
  topic: Topic;
  course: Course;
  days_inactive: number;
  urgency_score: number;
};

export type ExpectedScore = {
  course_name: string;
  estimated_score: number;
  score_range: [number, number];
  total_weight_coverage: number;
  dependency_penalty: number;
  high_risk_topics: any[];
};

export type Risk = {
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  course: string;
  description: string;
};

export type QuizQuestion = {
  id?: number;
  quiz_id?: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
};

export type Quiz = {
  id?: number;
  topic_id: number;
  title: string;
  created_at: string;
  questions: QuizQuestion[];
};

export type QuizAttempt = {
  id: number;
  quiz_id: number;
  attempted_at: string;
  score: number;
  total_questions: number;
};

export type StudySession = {
  id?: number;
  topic_id: number;
  start_time: string;
  end_time?: string;
  duration_minutes?: number;
};

export const getCourses = async () => {
  const response = await api.get<Course[]>('/courses');
  return response.data;
};

export const createCourse = async (course: Omit<Course, 'id'>) => {
  const response = await api.post<Course>('/courses', course);
  return response.data;
};

export const getTopics = async (courseId: number) => {
  const response = await api.get<Topic[]>(`/courses/${courseId}/topics`);
  return response.data;
};

export const createTopic = async (topic: Omit<Topic, 'id'>) => {
  const response = await api.post<Topic>('/topics', topic);
  return response.data;
};

export const generatePlan = async (hours: number, adaptive: boolean) => {
  const response = await api.post<StudyPlanResponse>('/plan', { hours, adaptive });
  return response.data;
};

export const getSkillHistory = async (topicId: number) => {
  const response = await api.get<SkillHistory[]>(`/topics/${topicId}/history`);
  return response.data;
};

export const getWeakTopics = async () => {
  const response = await api.get<WeakTopic[]>('/analytics/weak-topics');
  return response.data;
};

export const getExpectedScores = async () => {
  const response = await api.get<Record<string, ExpectedScore>>('/analytics/expected-scores');
  return response.data;
};

export const getRisks = async () => {
  const response = await api.get<Risk[]>('/analytics/risks');
  return response.data;
};

// CRUD Operations
export const updateCourse = async (courseId: number, course: Omit<Course, 'id'>) => {
  const response = await api.put<Course>(`/courses/${courseId}`, { ...course, id: courseId });
  return response.data;
};

export const deleteCourse = async (courseId: number) => {
  await api.delete(`/courses/${courseId}`);
};

export const updateTopic = async (topicId: number, topic: Omit<Topic, 'id'>) => {
  const response = await api.put<Topic>(`/topics/${topicId}`, { ...topic, id: topicId });
  return response.data;
};

export const deleteTopic = async (topicId: number) => {
  await api.delete(`/topics/${topicId}`);
};

export const updateTopicSkill = async (topicId: number, skillLevel: number) => {
  const response = await api.patch<Topic>(`/topics/${topicId}/skill`, { skill_level: skillLevel });
  return response.data;
};

// Quiz APIs
export const createQuiz = async (data: { topic_id: number; title: string; questions: QuizQuestion[] }) => {
  const response = await api.post<Quiz>('/quizzes', data);
  return response.data;
};

export const getQuiz = async (quizId: number) => {
  const response = await api.get<Quiz>(`/quizzes/${quizId}`);
  return response.data;
};

export const getTopicQuizzes = async (topicId: number) => {
  const response = await api.get<Quiz[]>(`/topics/${topicId}/quizzes`);
  return response.data;
};

export const attemptQuiz = async (quizId: number, answers: Record<number, string>) => {
  const response = await api.post<QuizAttempt>(`/quizzes/${quizId}/attempt`, { answers });
  return response.data;
};

export const getQuizAttempts = async (quizId: number) => {
  const response = await api.get<QuizAttempt[]>(`/quizzes/${quizId}/attempts`);
  return response.data;
};

export const getTopicQuizResults = async (topicId: number) => {
  const response = await api.get(`/topics/${topicId}/quiz-results`);
  return response.data;
};

export const deleteQuiz = async (quizId: number) => {
  await api.delete(`/quizzes/${quizId}`);
};

// Study Session APIs
export const startStudySession = async (topicId: number) => {
  const response = await api.post<StudySession>('/study-sessions/start', { topic_id: topicId });
  return response.data;
};

export const endStudySession = async (sessionId: number) => {
  const response = await api.post<StudySession>(`/study-sessions/${sessionId}/end`, {});
  return response.data;
};

export const getActiveSession = async () => {
  const response = await api.get<StudySession | null>('/study-sessions/active');
  return response.data;
};

export const getStudySessions = async (limit: number = 50) => {
  const response = await api.get<StudySession[]>(`/study-sessions?limit=${limit}`);
  return response.data;
};

export const getStudyStatistics = async () => {
  const response = await api.get('/study-sessions/statistics');
  return response.data;
};

export const getTopicSessions = async (topicId: number) => {
  const response = await api.get<StudySession[]>(`/topics/${topicId}/sessions`);
  return response.data;
};

// Skill Assessment APIs
export const manualSkillAssessment = async (topicId: number, skillLevel: number, reason: string = 'Manual self-assessment') => {
  const response = await api.post(`/topics/${topicId}/skill-assessment`, { skill_level: skillLevel, reason });
  return response.data;
};

export const applySkillDecay = async () => {
  const response = await api.post('/skill-decay/apply', {});
  return response.data;
};

export const getDecayStatus = async () => {
  const response = await api.get('/skill-decay/status');
  return response.data;
};
