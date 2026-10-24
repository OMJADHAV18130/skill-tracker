/** TanStack Query hooks. Mutations invalidate every view they can affect. */

import { useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query';
import {
  dashboardApi,
  plannerApi,
  profileApi,
  projectsApi,
  resourcesApi,
  roadmapApi,
  settingsApi,
  type PreferenceInput,
  type ProfileInput,
  type ProjectInput,
  type ResourceInput,
  type TaskInput,
} from '@/api/endpoints';
import type { ISODate, TopicProgress } from '@/types/api';

const KEYS = {
  dashboard: ['dashboard'] as const,
  phases: ['phases'] as const,
  topic: (id: string) => ['topic', id] as const,
  navigation: (id: string) => ['navigation', id] as const,
  projects: ['projects'] as const,
  projectSummary: ['project-summary'] as const,
  resources: ['resources'] as const,
  preferences: ['preferences'] as const,
  day: (date: ISODate) => ['day', date] as const,
  tasks: ['tasks'] as const,
  sessions: ['sessions'] as const,
  week: ['week'] as const,
  streak: ['streak'] as const,
  calendar: (year: number, month: number) => ['calendar', year, month] as const,
};

export function invalidateRoadmap(client: QueryClient, topicId?: string) {
  client.invalidateQueries({ queryKey: KEYS.phases });
  client.invalidateQueries({ queryKey: KEYS.dashboard });
  client.invalidateQueries({ queryKey: KEYS.streak });
  client.invalidateQueries({ queryKey: KEYS.week });
  if (topicId) {
    client.invalidateQueries({ queryKey: KEYS.topic(topicId) });
    client.invalidateQueries({ queryKey: KEYS.navigation(topicId) });
  }
}

export function invalidatePlanner(client: QueryClient) {
  client.invalidateQueries({ queryKey: KEYS.tasks });
  client.invalidateQueries({ queryKey: KEYS.sessions });
  client.invalidateQueries({ queryKey: ['day'] });
  client.invalidateQueries({ queryKey: KEYS.dashboard });
  client.invalidateQueries({ queryKey: KEYS.week });
  client.invalidateQueries({ queryKey: KEYS.streak });
  client.invalidateQueries({ queryKey: ['calendar'] });
}

export function invalidateProjects(client: QueryClient) {
  client.invalidateQueries({ queryKey: KEYS.projects });
  client.invalidateQueries({ queryKey: KEYS.projectSummary });
  client.invalidateQueries({ queryKey: KEYS.dashboard });
}

export function invalidateResources(client: QueryClient) {
  client.invalidateQueries({ queryKey: KEYS.resources });
}

export function invalidateSettings(client: QueryClient) {
  client.invalidateQueries({ queryKey: KEYS.preferences });
  client.invalidateQueries({ queryKey: KEYS.dashboard });
}

/* --------------------------------------------------------------- queries */

export function useDashboard() {
  return useQuery({ queryKey: KEYS.dashboard, queryFn: dashboardApi.get });
}

export function usePhases(track: 'core' | 'dsa' = 'core') {
  return useQuery({
    queryKey: [...KEYS.phases, track],
    queryFn: () => roadmapApi.phases(track),
    staleTime: 60_000,
  });
}

export function useTopic(id: string | undefined) {
  return useQuery({
    queryKey: KEYS.topic(id ?? ''),
    queryFn: () => roadmapApi.topic(id!),
    enabled: Boolean(id),
  });
}

export function useTopicNavigation(id: string | undefined) {
  return useQuery({
    queryKey: KEYS.navigation(id ?? ''),
    queryFn: () => roadmapApi.navigation(id!),
    enabled: Boolean(id),
  });
}

export function useProjects() {
  return useQuery({ queryKey: KEYS.projects, queryFn: projectsApi.list });
}

export function useProjectSummary() {
  return useQuery({ queryKey: KEYS.projectSummary, queryFn: projectsApi.summary });
}

export function useResources(params: { q?: string; category?: string; bookmarked?: boolean }) {
  return useQuery({
    queryKey: [...KEYS.resources, params],
    queryFn: () => resourcesApi.list(params),
  });
}

export function usePreferences() {
  return useQuery({ queryKey: KEYS.preferences, queryFn: settingsApi.get });
}

export function useDay(date: ISODate) {
  return useQuery({ queryKey: KEYS.day(date), queryFn: () => plannerApi.day(date) });
}

export function useWeek(anchor?: ISODate) {
  return useQuery({ queryKey: [...KEYS.week, anchor ?? 'current'], queryFn: () => plannerApi.week(anchor) });
}

export function useStreak() {
  return useQuery({ queryKey: KEYS.streak, queryFn: plannerApi.streak });
}

export function useCalendar(year: number, month: number) {
  return useQuery({
    queryKey: KEYS.calendar(year, month),
    queryFn: () => plannerApi.calendar(year, month),
  });
}

export function useSessions(params: { start?: ISODate; end?: ISODate }) {
  return useQuery({
    queryKey: [...KEYS.sessions, params],
    queryFn: () => plannerApi.sessions(params),
  });
}

/* ------------------------------------------------------------- mutations */

export function useUpdateTopicProgress(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Pick<TopicProgress, 'status' | 'priority' | 'rating'>>) =>
      roadmapApi.updateProgress(topicId, body),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useCreateNote(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (content: string) => roadmapApi.createNote(topicId, content),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useUpdateNote(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, content }: { id: string; content: string }) =>
      roadmapApi.updateNote(id, content),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useDeleteNote(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => roadmapApi.deleteNote(id),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useCreateChecklist(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (title: string) => roadmapApi.createChecklist(topicId, title),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useUpdateChecklist(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: { title?: string; is_done?: boolean } }) =>
      roadmapApi.updateChecklist(id, body),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useDeleteChecklist(topicId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => roadmapApi.deleteChecklist(id),
    onSuccess: () => invalidateRoadmap(client, topicId),
  });
}

export function useCreateTask() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: TaskInput) => plannerApi.createTask(body),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useUpdateTask() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: Partial<TaskInput> }) =>
      plannerApi.updateTask(id, body),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useDeleteTask() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => plannerApi.deleteTask(id),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useSetTaskCompletion() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, is_completed }: { id: string; is_completed: boolean }) =>
      plannerApi.setCompletion(id, is_completed),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useLogTaskTime() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      minutes,
      note,
      completed,
    }: {
      id: string;
      minutes: number;
      note?: string;
      completed?: boolean;
    }) => plannerApi.logTime(id, minutes, note, completed),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useCarryForward() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, target }: { id: string; target: ISODate }) =>
      plannerApi.carryForward(id, target),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useCreateSession() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: plannerApi.createSession,
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useDeleteSession() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => plannerApi.deleteSession(id),
    onSuccess: () => invalidatePlanner(client),
  });
}

export function useCreateProject() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: ProjectInput) => projectsApi.create(body),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useUpdateProject() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: Partial<ProjectInput> }) =>
      projectsApi.update(id, body),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useDeleteProject() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.remove(id),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useCompleteProject() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.complete(id),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useAddMilestone() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      title,
      due_date,
    }: {
      projectId: string;
      title: string;
      due_date?: ISODate | null;
    }) => projectsApi.addMilestone(projectId, { title, due_date }),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useUpdateMilestone() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      body,
    }: {
      id: string;
      body: { title?: string; is_completed?: boolean; due_date?: ISODate | null };
    }) => projectsApi.updateMilestone(id, body),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useDeleteMilestone() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.deleteMilestone(id),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useAddProjectChecklist() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, title }: { projectId: string; title: string }) =>
      projectsApi.addChecklist(projectId, title),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useUpdateProjectChecklist() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: { title?: string; is_done?: boolean } }) =>
      projectsApi.updateChecklist(id, body),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useDeleteProjectChecklist() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.deleteChecklist(id),
    onSuccess: () => invalidateProjects(client),
  });
}

export function useCreateResource() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: ResourceInput) => resourcesApi.create(body),
    onSuccess: () => invalidateResources(client),
  });
}

export function useUpdateResource() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: Partial<ResourceInput> }) =>
      resourcesApi.update(id, body),
    onSuccess: () => invalidateResources(client),
  });
}

export function useBookmarkResource() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, bookmarked }: { id: string; bookmarked: boolean }) =>
      resourcesApi.setBookmark(id, bookmarked),
    onSuccess: () => invalidateResources(client),
  });
}

export function useLinkResource() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, topicId }: { id: string; topicId: string | null }) =>
      resourcesApi.linkTopic(id, topicId),
    onSuccess: () => invalidateResources(client),
  });
}

export function useDeleteResource() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => resourcesApi.remove(id),
    onSuccess: () => invalidateResources(client),
  });
}

export function useUpdatePreferences() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: PreferenceInput) => settingsApi.update(body),
    onSuccess: () => invalidateSettings(client),
  });
}

export function usePauseDsa() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (resume_on?: string | null) => settingsApi.pauseDsa(resume_on),
    onSuccess: () => {
      invalidateSettings(client);
      client.invalidateQueries({ queryKey: KEYS.dashboard });
      client.invalidateQueries({ queryKey: KEYS.phases });
    },
  });
}

export function useResumeDsa() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => settingsApi.resumeDsa(),
    onSuccess: () => {
      invalidateSettings(client);
      client.invalidateQueries({ queryKey: KEYS.dashboard });
      client.invalidateQueries({ queryKey: KEYS.phases });
    },
  });
}

export function useUpdateProfile() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (body: ProfileInput) => profileApi.update(body),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ['me'] });
    },
  });
}
