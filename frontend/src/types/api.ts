/** Typed mirrors of the FastAPI response models. */

export type UUID = string;
export type ISODate = string; // YYYY-MM-DD
export type ISODateTime = string;

export type TopicStatus = 'not_started' | 'in_progress' | 'completed';
export type Priority = 'low' | 'medium' | 'high';
export type ProjectStatus = 'not_started' | 'in_progress' | 'completed' | 'archived';
export type Theme = 'light' | 'dark' | 'system';

export interface User {
  id: UUID;
  email: string;
  username: string;
  full_name: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: ISODateTime;
  last_login_at: ISODateTime | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

/* ------------------------------------------------------------------ roadmap */

export interface TopicNote {
  id: UUID;
  topic_id: UUID;
  content: string;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface TopicChecklistItem {
  id: UUID;
  topic_id: UUID;
  title: string;
  is_done: boolean;
  order_index: number;
}

export interface ResourceBrief {
  id: UUID;
  title: string;
  url: string;
  category: string;
  description: string;
  is_official: boolean;
}

export interface TopicProgress {
  status: TopicStatus;
  priority: Priority;
  rating: number | null;
  started_at: ISODateTime | null;
  completed_at: ISODateTime | null;
  notes: TopicNote[];
  checklist: TopicChecklistItem[];
}

export interface TopicNavigation {
  previous: Topic | null;
  next: Topic | null;
  position: number;
  total: number;
}

export interface Topic {
  id: UUID;
  phase_id: UUID;
  slug: string;
  title: string;
  description: string;
  category: string;
  estimated_minutes: number;
  order_index: number;
  track?: 'core' | 'dsa' | string;
  subtopics: string[];
  is_key_topic: boolean;
  progress: TopicProgress;
  resources: ResourceBrief[];
}

export interface Phase {
  id: UUID;
  key: string;
  title: string;
  summary: string;
  month_label: string;
  duration_months: number;
  order_index: number;
  project_brief: string | null;
  accent: string | null;
  topic_count: number;
  completed_count: number;
  in_progress_count: number;
  completion_percentage: number;
  estimated_minutes: number;
  status: TopicStatus;
  topics: Topic[];
}

export interface PhaseListResponse {
  items: Phase[];
  track?: 'core' | 'dsa' | string;
  total_topics: number;
  completed_topics: number;
  completion_percentage: number;
}

export interface Phase {
  id: UUID;
  key: string;
  title: string;
  summary: string;
  month_label: string;
  duration_months: number;
  order_index: number;
  track?: 'core' | 'dsa' | string;
  project_brief: string | null;
  accent: string | null;
  topics: Topic[];
  topic_count: number;
  completed_count: number;
  in_progress_count: number;
  completion_percentage: number;
  estimated_minutes: number;
  status: TopicStatus | 'not_started' | 'in_progress' | 'completed';
}

/* ------------------------------------------------------------------ planner */

export interface DailyTask {
  id: UUID;
  title: string;
  description: string | null;
  task_date: ISODate;
  category: string;
  estimated_minutes: number;
  actual_minutes: number;
  priority: Priority;
  is_completed: boolean;
  completed_at: ISODateTime | null;
  session_note: string | null;
  carried_from_id: UUID | null;
  topic_id: UUID | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface StudySession {
  id: UUID;
  task_id: UUID | null;
  topic_id: UUID | null;
  session_date: ISODate;
  minutes: number;
  note: string | null;
  created_at: ISODateTime;
}

export interface DaySummary {
  date: ISODate;
  planned_minutes: number;
  completed_minutes: number;
  logged_minutes: number;
  planned_tasks: number;
  completed_tasks: number;
  goal_minutes: number;
  goal_percentage: number;
}

export interface DayPlan {
  goal_minutes: number;
  tasks: DailyTask[];
  sessions: StudySession[];
  summary: DaySummary;
}

export interface CalendarDay {
  date: ISODate;
  total_minutes: number;
  session_count: number;
  completed_tasks: number;
  has_activity: boolean;
}

export interface CalendarResponse {
  month: string;
  days: CalendarDay[];
  total_minutes: number;
  active_days: number;
  average_minutes_per_active_day: number;
}

export interface WeekSummary {
  week_start: ISODate;
  week_end: ISODate;
  total_minutes: number;
  total_hours: number;
  average_minutes_per_day: number;
  goal_minutes_per_day: number;
  days_achieved: number;
  tasks_completed: number;
  by_category: Record<string, number>;
  daily_minutes: Record<string, number>;
}

export interface Streak {
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  last_active_date: ISODate | null;
  rule: string;
}

/* ----------------------------------------------------------------- projects */

export interface ProjectMilestone {
  id: UUID;
  project_id: UUID;
  title: string;
  description: string | null;
  is_completed: boolean;
  completed_at: ISODateTime | null;
  due_date: ISODate | null;
  order_index: number;
}

export interface ProjectChecklistItem {
  id: UUID;
  project_id: UUID;
  title: string;
  is_done: boolean;
  order_index: number;
}

export interface Project {
  id: UUID;
  name: string;
  description: string;
  required_skills: string[];
  status: ProjectStatus;
  priority: Priority;
  start_date: ISODate | null;
  target_date: ISODate | null;
  repo_url: string | null;
  demo_url: string | null;
  notes: string | null;
  order_index: number;
  created_at: ISODateTime;
  updated_at: ISODateTime;
  milestones: ProjectMilestone[];
  checklist_items: ProjectChecklistItem[];
  milestone_count: number;
  completed_milestones: number;
  completion_percentage: number;
  checklist_count: number;
  completed_checklist_items: number;
  checklist_percentage: number;
  days_remaining: number | null;
}

export interface ProjectSummary {
  total: number;
  not_started: number;
  in_progress: number;
  completed: number;
  average_completion: number;
}

/* ---------------------------------------------------------------- resources */

export interface Resource {
  id: UUID;
  title: string;
  url: string;
  description: string;
  category: string;
  tags: string[];
  is_official: boolean;
  is_bookmarked: boolean;
  linked_topic_id: UUID | null;
  linked_topic_title: string | null;
  notes: string | null;
}

export interface ResourceListResponse {
  items: Resource[];
  total: number;
  categories: string[];
  bookmarked_count: number;
}

/* ------------------------------------------------------------------ settings */

export interface Preferences {
  id: UUID;
  user_id: UUID;
  daily_goal_minutes: number;
  roadmap_start_date: ISODate;
  theme: Theme;
  reminders_enabled: boolean;
  reminder_time: string;
  timezone: string;
  phase_durations: Record<string, number>;
  sidebar_collapsed: boolean;
  dsa_paused?: boolean;
  dsa_paused_at?: ISODateTime | null;
  dsa_paused_until?: ISODate | null;
}

export interface ImportPreview {
  valid: boolean;
  schema_version: string | null;
  warnings: string[];
  errors: string[];
  counts: Record<string, number>;
}

/* ----------------------------------------------------------------- dashboard */

export interface PhaseProgressDto {
  key: string;
  title: string;
  month_label: string;
  completion_percentage: number;
  completed_topics: number;
  total_topics: number;
  status: TopicStatus;
}

export interface DailyStudyPoint {
  date: ISODate;
  minutes: number;
  goal_minutes: number;
  label: string;
}

export interface MilestoneDto {
  id: string;
  title: string;
  kind: 'topic' | 'project';
  due_label: string | null;
  completed: boolean;
  subtitle: string | null;
}

export interface ActivityDto {
  id: string;
  type: string;
  title: string;
  detail: string | null;
  occurred_at: string | null;
}

export interface ProjectStatusDto {
  id: UUID;
  name: string;
  status: ProjectStatus;
  completion_percentage: number;
  completed_milestones: number;
  milestone_count: number;
  repo_url: string | null;
  demo_url: string | null;
}

export interface DashboardTaskDto {
  id: UUID;
  title: string;
  task_date: ISODate;
  category: string;
  estimated_minutes: number;
  priority: Priority;
  is_completed: boolean;
}

export interface DsaTrackSummary {
  total_topics: number;
  completed_topics: number;
  in_progress_topics: number;
  completion_percentage: number;
  paused: boolean;
  paused_until: ISODate | null;
  phases: PhaseProgressDto[];
  next_recommended_topic: {
    id?: string;
    title?: string;
    description?: string;
    category?: string;
    estimated_minutes?: number;
    status?: TopicStatus;
    phase_id?: string;
  };
}


export interface Dashboard {
  overall_completion_percentage: number;
  completed_topics: number;
  total_topics: number;
  in_progress_topics: number;
  current_phase: {
    key?: string;
    title?: string;
    month_label?: string;
    completion_percentage?: number;
    completed_topics?: number;
    total_topics?: number;
    project_brief?: string | null;
  };
  next_recommended_topic: {
    id?: string;
    title?: string;
    description?: string;
    category?: string;
    estimated_minutes?: number;
    status?: TopicStatus;
    phase_id?: string;
  };
  dsa?: DsaTrackSummary;
  total_study_minutes: number;
  total_study_hours: number;
  current_streak: number;
  longest_streak: number;
  weekly_study: DailyStudyPoint[];
  phase_progress: PhaseProgressDto[];
  todays_tasks: DashboardTaskDto[];
  todays_planned_minutes: number;
  todays_completed_minutes: number;
  todays_goal_minutes: number;
  todays_goal_percentage: number;
  upcoming_milestones: MilestoneDto[];
  recent_activity: ActivityDto[];
  projects: ProjectStatusDto[];
  projects_completed: number;
  projects_total: number;
}

/* --------------------------------------------------------------------- api */

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    request_id?: string;
  };
}
