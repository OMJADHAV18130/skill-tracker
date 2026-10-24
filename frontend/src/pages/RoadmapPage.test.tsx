import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import RoadmapPage from '@/pages/RoadmapPage';
import { ToastProvider } from '@/contexts/ToastContext';
import type { Phase, PhaseListResponse, Topic, TopicStatus } from '@/types/api';

const { updateProgress, refetch, state } = vi.hoisted(() => ({
  updateProgress: vi.fn(),
  refetch: vi.fn(),
  state: { roadmap: null as unknown },
}));

vi.mock('@/api/hooks', () => ({
  usePhases: () => ({
    data: state.roadmap,
    isLoading: false,
    isError: false,
    refetch,
  }),
  usePreferences: () => ({ data: null }),
  usePauseDsa: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useResumeDsa: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useUpdateTopicProgress: () => ({
    mutateAsync: updateProgress,
    isPending: false,
  }),
}));

function makeTopic(
  id: string,
  title: string,
  status: TopicStatus = 'not_started',
): Topic {
  return {
    id,
    phase_id: 'phase-1',
    slug: id,
    title,
    description: `${title} description`,
    category: 'Java',
    estimated_minutes: 90,
    order_index: 1,
    track: 'core',
    subtopics: [`${title} subtopic`],
    is_key_topic: false,
    progress: {
      status,
      priority: 'medium',
      rating: null,
      started_at: null,
      completed_at: null,
      notes: [],
      checklist: [],
    },
    resources: [],
  };
}

function makePhase(
  id: string,
  title: string,
  status: TopicStatus,
  topics: Topic[],
): Phase {
  const completed = topics.filter((topic) => topic.progress.status === 'completed').length;
  return {
    id,
    key: id,
    title,
    summary: `${title} summary`,
    month_label: 'Months 1-2',
    duration_months: 2,
    order_index: 0,
    project_brief: null,
    accent: 'sky',
    track: 'core',
    topic_count: topics.length,
    completed_count: completed,
    in_progress_count: topics.filter((topic) => topic.progress.status === 'in_progress').length,
    completion_percentage: (completed / topics.length) * 100,
    estimated_minutes: topics.length * 90,
    status,
    topics,
  };
}

const phaseOne = makePhase('phase-1', 'Java foundations', 'in_progress', [
  makeTopic('topic-1', 'Collections', 'completed'),
  makeTopic('topic-2', 'Streams', 'in_progress'),
]);
const phaseTwo = makePhase('phase-2', 'Spring Boot', 'not_started', [
  makeTopic('topic-3', 'REST controllers'),
]);

const roadmap: PhaseListResponse = {
  items: [phaseOne, phaseTwo],
  track: 'core',
  total_topics: 3,
  completed_topics: 1,
  completion_percentage: 33.33,
};
state.roadmap = roadmap;

function renderRoadmap() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <RoadmapPage />
      </ToastProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  updateProgress.mockReset();
  updateProgress.mockResolvedValue(undefined);
  refetch.mockReset();
});

afterEach(() => {
  vi.clearAllTimers();
});

describe('RoadmapPage', () => {
  it('derives the summary and expands the active phase', () => {
    renderRoadmap();

    expect(screen.getByText('1/2 topics')).toBeInTheDocument();

    // The in-progress phase is expanded, so its topics are visible.
    expect(screen.getByRole('link', { name: 'Collections' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Streams' })).toBeInTheDocument();
    // The inactive phase stays collapsed.
    expect(screen.queryByRole('link', { name: 'REST controllers' })).not.toBeInTheDocument();
  });

  it('searches across topics and can clear the filters', async () => {
    renderRoadmap();

    await userEvent.type(screen.getByLabelText('Search the roadmap'), 'spring');

    expect(screen.getByText('Spring Boot')).toBeInTheDocument();
    expect(screen.queryByText('Java foundations')).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'REST controllers' })).toBeInTheDocument();
    expect(screen.getByText(/Showing 1 topics across 1 phase/)).toBeInTheDocument();

    await userEvent.clear(screen.getByLabelText('Search the roadmap'));
    await userEvent.selectOptions(screen.getByLabelText('Filter by topic status'), 'completed');

    expect(screen.getByRole('link', { name: 'Collections' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Streams' })).not.toBeInTheDocument();
  });

  it('shows an empty state when nothing matches', async () => {
    renderRoadmap();

    await userEvent.type(screen.getByLabelText('Search the roadmap'), 'kubernetes');

    expect(screen.getByText('No topics match those filters')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Clear filters' }));
    expect(screen.getByRole('link', { name: 'Collections' })).toBeInTheDocument();
  });

  it('persists a status change through the API and confirms it', async () => {
    renderRoadmap();

    const row = screen.getByRole('link', { name: 'Streams' }).closest('li');
    expect(row).not.toBeNull();

    await userEvent.selectOptions(
      within(row as HTMLElement).getByLabelText('Status for Streams'),
      'completed',
    );

    await waitFor(() =>
      expect(updateProgress).toHaveBeenCalledWith({ status: 'completed' }),
    );
    expect(await screen.findByText(/“Streams” marked complete/)).toBeInTheDocument();
  });
});
