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
