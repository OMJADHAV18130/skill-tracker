/** Typed wrappers around every backend endpoint the UI needs. */

import { api } from '@/api/client';
import type {
  CalendarResponse,
  Dashboard,
  DailyTask,
  DayPlan,
  ImportPreview,
  ISODate,
  Page,
  PhaseListResponse,
  Preferences,
  Project,
  ProjectChecklistItem,
  ProjectMilestone,
  ProjectSummary,
  Resource,
  ResourceListResponse,
  Streak,
  StudySession,
  Topic,
  TopicChecklistItem,
  TopicNavigation,
  TopicNote,
  TopicProgress,
  WeekSummary,
} from '@/types/api';

export interface TaskInput {
  title: string;
  task_date: ISODate;
  description?: string | null;
  category?: string;
  estimated_minutes?: number;
  priority?: 'low' | 'medium' | 'high';
  topic_id?: string | null;
}

export interface ProjectInput {
  name: string;
  description?: string;
  required_skills?: string[];
  priority?: 'low' | 'medium' | 'high';
  status?: 'not_started' | 'in_progress' | 'completed' | 'archived';
  start_date?: ISODate | null;
  target_date?: ISODate | null;
  repo_url?: string | null;
  demo_url?: string | null;
  notes?: string | null;
}

export interface ResourceInput {
  title: string;
  url: string;
  description?: string;
  category: string;
  tags?: string[];
  linked_topic_id?: string | null;
}

export interface PreferenceInput {
  daily_goal_minutes?: number;
  roadmap_start_date?: ISODate;
  theme?: 'light' | 'dark' | 'system';
  reminders_enabled?: boolean;
  reminder_time?: string;
  timezone?: string;
  phase_durations?: Record<string, number>;
  sidebar_collapsed?: boolean;
}

export const roadmapApi = {
  phases: (track: 'core' | 'dsa' = 'core') => {
    const query = track === 'dsa' ? '?track=dsa' : '';
    return api.get<PhaseListResponse>(`/roadmap/phases${query}`);
  },
  topic: (id: string) => api.get<Topic>(`/roadmap/topics/${id}`),
  navigation: (id: string) => api.get<TopicNavigation>(`/roadmap/topics/${id}/navigation`),
  updateProgress: (id: string, body: Partial<Pick<TopicProgress, 'status' | 'priority' | 'rating'>>) =>
    api.patch<Topic>(`/roadmap/topics/${id}/progress`, body),
  next: (track: 'core' | 'dsa' = 'core') => {
    const query = track === 'dsa' ? '?track=dsa' : '';
    return api.get<Topic | null>(`/roadmap/next${query}`);
  },
  notes: (topicId: string) => api.get<TopicNote[]>(`/roadmap/topics/${topicId}/notes`),
  createNote: (topicId: string, content: string) =>
    api.post<TopicNote>(`/roadmap/topics/${topicId}/notes`, { content }),
  updateNote: (noteId: string, content: string) =>
    api.patch<TopicNote>(`/roadmap/notes/${noteId}`, { content }),
  deleteNote: (noteId: string) => api.delete<void>(`/roadmap/notes/${noteId}`),
  checklist: (topicId: string) =>
    api.get<TopicChecklistItem[]>(`/roadmap/topics/${topicId}/checklist`),
  createChecklist: (topicId: string, title: string) =>
    api.post<TopicChecklistItem>(`/roadmap/topics/${topicId}/checklist`, { title }),
  updateChecklist: (itemId: string, body: { title?: string; is_done?: boolean }) =>
    api.patch<TopicChecklistItem>(`/roadmap/checklist/${itemId}`, body),
  deleteChecklist: (itemId: string) => api.delete<void>(`/roadmap/checklist/${itemId}`),
};

export const plannerApi = {
  tasks: (params: {
    page?: number;
    page_size?: number;
    start?: ISODate;
    end?: ISODate;
    category?: string;
    is_completed?: boolean;
  }) => api.get<Page<DailyTask>>('/planner/tasks', { query: params }),
  day: (date: ISODate) => api.get<DayPlan>('/planner/day', { query: { date } }),
  createTask: (body: TaskInput) => api.post<DailyTask>('/planner/tasks', body),
  updateTask: (id: string, body: Partial<TaskInput>) =>
    api.patch<DailyTask>(`/planner/tasks/${id}`, body),
  deleteTask: (id: string) => api.delete<void>(`/planner/tasks/${id}`),
  setCompletion: (id: string, is_completed: boolean) =>
    api.patch<DailyTask>(`/planner/tasks/${id}/completion`, { is_completed }),
  logTime: (id: string, actual_minutes: number, session_note?: string, completed?: boolean) =>
    api.post<DailyTask>(`/planner/tasks/${id}/log`, { actual_minutes, session_note, completed }),
  carryForward: (id: string, target_date: ISODate) =>
    api.post<DailyTask>(`/planner/tasks/${id}/carry-forward`, {
      target_date,
      delete_original: true,
    }),
  sessions: (params: { start?: ISODate; end?: ISODate }) =>
    api.get<StudySession[]>('/planner/sessions', { query: params }),
  createSession: (body: {
    minutes: number;
    session_date: ISODate;
    task_id?: string | null;
    topic_id?: string | null;
    note?: string | null;
  }) => api.post<StudySession>('/planner/sessions', body),
  deleteSession: (id: string) => api.delete<void>(`/planner/sessions/${id}`),
  calendar: (year: number, month: number) =>
    api.get<CalendarResponse>('/planner/calendar', { query: { year, month } }),
  week: (anchor?: ISODate) =>
    api.get<WeekSummary>('/planner/week', { query: anchor ? { anchor } : undefined }),
  streak: () => api.get<Streak>('/planner/streak'),
};

export const projectsApi = {
  list: () => api.get<Project[]>('/projects'),
  summary: () => api.get<ProjectSummary>('/projects/summary'),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (body: ProjectInput) => api.post<Project>('/projects', body),
  update: (id: string, body: Partial<ProjectInput>) =>
    api.patch<Project>(`/projects/${id}`, body),
  remove: (id: string) => api.delete<void>(`/projects/${id}`),
  complete: (id: string) => api.post<Project>(`/projects/${id}/complete`),
  addMilestone: (projectId: string, body: { title: string; description?: string; due_date?: ISODate | null }) =>
    api.post<ProjectMilestone>(`/projects/${projectId}/milestones`, body),
  updateMilestone: (id: string, body: { title?: string; is_completed?: boolean; due_date?: ISODate | null; description?: string | null }) =>
    api.patch<ProjectMilestone>(`/projects/milestones/${id}`, body),
  deleteMilestone: (id: string) => api.delete<void>(`/projects/milestones/${id}`),
  addChecklist: (projectId: string, title: string) =>
    api.post<ProjectChecklistItem>(`/projects/${projectId}/checklist`, { title }),
  updateChecklist: (id: string, body: { title?: string; is_done?: boolean }) =>
    api.patch<ProjectChecklistItem>(`/projects/checklist/${id}`, body),
  deleteChecklist: (id: string) => api.delete<void>(`/projects/checklist/${id}`),
};

export const resourcesApi = {
  list: (params: { q?: string; category?: string; bookmarked?: boolean }) =>
    api.get<ResourceListResponse>('/resources', { query: params }),
  categories: () => api.get<string[]>('/resources/categories'),
  create: (body: ResourceInput) => api.post<Resource>('/resources', body),
  update: (id: string, body: Partial<ResourceInput>) =>
    api.patch<Resource>(`/resources/${id}`, body),
  setBookmark: (id: string, is_bookmarked: boolean) =>
    api.put<Resource>(`/resources/${id}/bookmark`, { is_bookmarked }),
  linkTopic: (id: string, topicId: string | null) =>
    api.put<Resource>(`/resources/${id}/link`, undefined, {
      query: topicId ? { topic_id: topicId } : undefined,
    }),
  remove: (id: string) => api.delete<void>(`/resources/${id}`),
};

export const settingsApi = {
  get: () => api.get<Preferences>('/settings'),
  update: (body: PreferenceInput) => api.patch<Preferences>('/settings', body),
  pauseDsa: (resume_on?: string | null) =>
    api.post<Preferences>('/settings/dsa/pause', resume_on ? { resume_on } : {}),
  resumeDsa: () => api.post<Preferences>('/settings/dsa/resume'),
  exportJson: () => api.download('/settings/export.json', 'devpath-progress.json'),
  exportCsv: () => api.download('/settings/export.csv', 'devpath-progress.csv'),
  validateImport: (payload: unknown) =>
    api.post<ImportPreview>('/settings/import/validate', payload),
  import: (payload: unknown, mode: 'replace' | 'merge' = 'replace') =>
    api.post<{ message: string }>('/settings/import', { payload, confirm: true, mode }),
  reset: () => api.post<{ message: string }>('/settings/reset', undefined, { query: { confirm: true } }),
};

export const dashboardApi = {
  get: () => api.get<Dashboard>('/dashboard'),
};

export interface ProfileInput {
  full_name?: string | null;
  email?: string;
  username?: string;
}

export const profileApi = {
  update: (body: ProfileInput) =>
    api.patch<import('@/types/api').User>('/auth/me', body),
  changePassword: (current_password: string, new_password: string) =>
    api.post<{ message: string }>('/auth/change-password', {
      current_password,
      new_password,
    }),
};
