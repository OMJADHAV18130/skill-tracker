import type { Priority, ProjectStatus, TopicStatus } from '@/types/api';

export const PRIORITY_OPTIONS: Array<{ value: Priority; label: string }> = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
];

export const TOPIC_STATUS_OPTIONS: Array<{ value: TopicStatus; label: string }> = [
  { value: 'not_started', label: 'Not started' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
];

export const PROJECT_STATUS_OPTIONS: Array<{ value: ProjectStatus; label: string }> = [
  { value: 'not_started', label: 'Not started' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'archived', label: 'Archived' },
];

export const TASK_CATEGORIES = [
  'General',
  'Java',
  'Spring Boot',
  'SQL',
  'Databases',
  'Security',
  'Testing',
  'Linux',
  'Networking',
  'Docker',
  'CI/CD',
  'Cloud',
  'Kubernetes',
  'Monitoring',
  'System Design',
  'Career',
];

export const RESOURCE_CATEGORIES = [
  'Java',
  'Spring Boot',
  'Databases',
  'Security',
  'Linux',
  'Docker',
  'CI/CD',
  'Cloud',
  'Kubernetes',
  'Monitoring',
  'DSA',
  'System Design',
];

export const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export const DEMO_EMAIL = 'demo@devpath.dev';
export const DEMO_PASSWORD = 'devpath-demo-123';
