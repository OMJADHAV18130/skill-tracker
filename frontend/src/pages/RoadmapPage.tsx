import { useDeferredValue, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  ArrowRight,
  ChevronDown,
  Circle,
  CircleCheckBig,
  CircleDot,
  Clock,
  Layers,
  Library,
  PauseCircle,
  PlayCircle,
  Search,
  Sparkles,
  Star,
  Target,
} from 'lucide-react';
import { usePhases, usePreferences, usePauseDsa, useResumeDsa, useUpdateTopicProgress } from '@/api/hooks';
import { Badge, priorityTone, statusLabel, statusTone } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Input, Select } from '@/components/ui/Field';
import { Modal } from '@/components/ui/Modal';
import { PageHeader, StatCard } from '@/components/ui/PageHeader';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/contexts/ToastContext';
import { cn } from '@/lib/cn';
import { formatHours, formatMinutes } from '@/lib/format';
import { usePageTitle } from '@/lib/usePageTitle';
import type { Phase, Topic, TopicStatus } from '@/types/api';

const accents: Record<string, string> = {
  amber: '#f59e0b',
  emerald: '#10b981',
  sky: '#0ea5e9',
  violet: '#8b5cf6',
  orange: '#f97316',
  indigo: '#6366f1',
  rose: '#f43f5e',
  cyan: '#06b6d4',
  teal: '#14b8a6',
};

function TopicStatusControl({ topic }: { topic: Topic }) {
  const mutation = useUpdateTopicProgress(topic.id);
  const { notify } = useToast();

  const update = async (status: TopicStatus) => {
    try {
      await mutation.mutateAsync({ status });
      notify(
        status === 'completed'
          ? `"${topic.title}" marked complete`
          : status === 'in_progress'
            ? `Keep going — "${topic.title}" is in progress`
            : `"${topic.title}" reset`,
        'success',
      );
    } catch {
      notify('Could not update this topic', 'error');
    }
  };

  return (
    <Select
      aria-label={`Status for ${topic.title}`}
      value={topic.progress.status}
      disabled={mutation.isPending}
      onChange={(event) => void update(event.target.value as TopicStatus)}
      className="h-8 w-full min-w-[7.5rem] text-xs sm:w-auto"
    >
      <option value="not_started">Not started</option>
      <option value="in_progress">In progress</option>
      <option value="completed">Completed</option>
    </Select>
  );
}

function TopicRow({ topic }: { topic: Topic }) {
  return (
    <li className="flex flex-col gap-2 px-4 py-3 transition-colors hover:bg-surface-hover/60 sm:flex-row sm:items-center sm:gap-3">
      <div className="flex min-w-0 flex-1 items-start gap-2.5">
        <span className="mt-0.5 shrink-0">
          {topic.progress.status === 'completed' ? (
            <CircleCheckBig className="h-4 w-4 text-success" aria-hidden="true" />
          ) : topic.progress.status === 'in_progress' ? (
            <CircleDot className="h-4 w-4 text-accent" aria-hidden="true" />
          ) : (
            <Circle className="h-4 w-4 text-faint" aria-hidden="true" />
          )}
        </span>
        <div className="min-w-0">
          <Link
            to={`/roadmap/topics/${topic.id}`}
            className="group inline-flex items-start gap-1.5 text-sm font-medium leading-snug text-text transition hover:text-accent"
          >
            <span>{topic.title}</span>
            {topic.is_key_topic ? (
              <Star className="mt-0.5 h-3 w-3 shrink-0 fill-warning text-warning" aria-label="Key topic" />
            ) : null}
          </Link>
          <div className="mt-1 flex flex-wrap items-center gap-1.5">
            <Badge>{topic.category}</Badge>
            <Badge tone={priorityTone(topic.progress.priority)}>{statusLabel(topic.progress.priority)} priority</Badge>
            <span className="inline-flex items-center gap-1 text-[11px] text-muted">
              <Clock className="h-3 w-3" aria-hidden="true" />
              {formatMinutes(topic.estimated_minutes)}
            </span>
            {topic.resources.length > 0 ? (
              <span className="inline-flex items-center gap-1 text-[11px] text-muted">
                <Library className="h-3 w-3" aria-hidden="true" />
                {topic.resources.length}
              </span>
            ) : null}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2 pl-6 sm:pl-0">
        <TopicStatusControl topic={topic} />
        <Link
          to={`/roadmap/topics/${topic.id}`}
          className="rounded-lg p-1.5 text-faint transition hover:bg-surface-2 hover:text-accent"
          aria-label={`Open ${topic.title}`}
        >
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </li>
  );
}

function PhaseCard({
  phase,
  index,
  expanded,
  onToggle,
}: {
  phase: Phase;
  index: number;
  expanded: boolean;
  onToggle: () => void;
}) {
  const accent = accents[phase.accent ?? ''] ?? 'var(--accent)';

  return (
    <Card className="overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={expanded}
        className="flex w-full items-start gap-3 px-4 py-4 text-left transition-colors hover:bg-surface-hover/50 sm:px-5"
      >
        <span
          className="tabular mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold"
          style={{ background: `${accent}1f`, color: accent }}
        >
          {String(index + 1).padStart(2, '0')}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-sm font-semibold text-text">{phase.title}</h2>
            <Badge tone={statusTone(phase.status)}>{statusLabel(phase.status)}</Badge>
            <span className="text-[11px] text-faint">{phase.month_label}</span>
          </div>
          <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted">{phase.summary}</p>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
            <span>
              {phase.completed_count}/{phase.topic_count} topics
            </span>
            {phase.in_progress_count > 0 ? <span>{phase.in_progress_count} in progress</span> : null}
            <span>{formatHours(phase.estimated_minutes)}h estimated</span>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <ProgressBar
              value={phase.completion_percentage}
              size="sm"
              tone={phase.status === 'completed' ? 'success' : 'accent'}
              className="max-w-md"
            />
            <span className="tabular shrink-0 text-[11px] font-medium text-text">
              {Math.round(phase.completion_percentage)}%
            </span>
          </div>
        </div>
        <ChevronDown
          className={`mt-1 h-4 w-4 shrink-0 text-faint transition-transform ${expanded ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      {expanded ? (
        <div className="animate-in border-t border-line">
          {phase.project_brief ? (
            <div className="mx-4 mt-3 rounded-lg border border-line bg-surface-2 px-3 py-2.5 sm:mx-5">
              <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-faint">Phase project</p>
              <p className="mt-0.5 text-xs leading-relaxed text-muted">{phase.project_brief}</p>
            </div>
          ) : null}
          <ul className="mt-2 divide-y divide-line">
            {phase.topics.map((topic) => (
              <TopicRow key={topic.id} topic={topic} />
            ))}
          </ul>
        </div>
      ) : null}
    </Card>
  );
}

export default function RoadmapPage() {
  usePageTitle('Roadmap');
  const [searchParams, setSearchParams] = useSearchParams();
  const trackParam = searchParams.get('track') === 'dsa' ? 'dsa' : 'core';
  const [track, setTrack] = useState<'core' | 'dsa'>(trackParam);
  const { data, isLoading, isError, refetch } = usePhases(track);
  const { data: coreData } = usePhases('core');
  const { data: dsaData } = usePhases('dsa');
  const { data: prefs } = usePreferences();
  const pauseDsa = usePauseDsa();
  const resumeDsa = useResumeDsa();
  const { notify } = useToast();
  const [search, setSearch] = useState('');
  const deferredSearch = useDeferredValue(search);
  const [status, setStatus] = useState<'all' | TopicStatus>('all');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const initialised = useRef(false);
  const [pauseOpen, setPauseOpen] = useState(false);
  const [resumeOn, setResumeOn] = useState('');

  useEffect(() => {
    if (trackParam !== track) {
      setTrack(trackParam);
    }
  }, [trackParam, track]);

  useEffect(() => {
    if (!data || initialised.current) return;
    const active =
      data.items.find((phase) => phase.status === 'in_progress') ??
      data.items.find((phase) => phase.status !== 'completed') ??
      data.items[0];
    if (active) setExpanded(new Set([active.id]));
    initialised.current = true;
  }, [data]);

  const query = deferredSearch.trim().toLowerCase();

  const visiblePhases = useMemo(() => {
    if (!data) return [];
    return data.items
      .map((phase) => {
        const phaseMatches =
          !query ||
          [phase.title, phase.summary, phase.month_label].some((value) =>
            value.toLowerCase().includes(query),
          );
        const topics = phase.topics.filter((topic) => {
          const matchesText =
            phaseMatches ||
            [topic.title, topic.description, topic.category, ...(topic.subtopics ?? [])].some((value) =>
              value.toLowerCase().includes(query),
            );
          const matchesStatus = status === 'all' || topic.progress.status === status;
          return matchesText && matchesStatus;
        });
        return { ...phase, topics };
      })
      .filter((phase) => phase.topics.length > 0);
  }, [data, query, status]);

  const toggle = (id: string) => {
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const switchTrack = (nextTrack: 'core' | 'dsa') => {
    setTrack(nextTrack);
    setExpanded(new Set());
    initialised.current = false;
    const params = new URLSearchParams(searchParams);
    if (nextTrack === 'core') params.delete('track');
    else params.set('track', 'dsa');
    setSearchParams(params, { replace: true });
  };

  const dsaPaused = Boolean(prefs?.dsa_paused);
  const dsaPausedUntil = prefs?.dsa_paused_until;

  const handlePause = async () => {
    try {
      await pauseDsa.mutateAsync(resumeOn || null);
      setPauseOpen(false);
      setResumeOn('');
      notify('DSA track paused', 'success');
    } catch {
      notify('Could not pause the DSA track', 'error');
    }
  };

  const handleResume = async () => {
    try {
      await resumeDsa.mutateAsync();
      notify('DSA track resumed', 'success');
    } catch {
      notify('Could not resume the DSA track', 'error');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-5">
        <div>
          <div className="h-3 w-24 rounded bg-bg-subtle" />
          <div className="mt-2 h-7 w-56 rounded bg-bg-subtle" />
        </div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <CardSkeleton key={index} />
          ))}
        </div>
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="h-28 rounded-card border border-line bg-surface shimmer" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-5">
        <PageHeader title="Roadmap" description="Your twelve-month path from Java foundations to production DevOps." />
        <ErrorState onRetry={() => void refetch()} />
      </div>
    );
  }

  const phasesCompleted = data.items.filter((phase) => phase.status === 'completed').length;
  const inProgress = data.items.filter((phase) => phase.status === 'in_progress').length;
  const filtering = query.length > 0 || status !== 'all';
  const isExpanded = (phaseId: string) => expanded.has(phaseId) || filtering;
  const totalEstimated = data.items.reduce((sum, phase) => sum + phase.estimated_minutes, 0);
  const coreCount = coreData?.items.length ?? 7;
  const coreTopics = coreData?.total_topics ?? 69;
  const dsaCount = dsaData?.items.length ?? 2;
  const dsaTopics = dsaData?.total_topics ?? 24;

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow={track === 'dsa' ? 'Parallel track' : '12-month curriculum'}
        title={track === 'dsa' ? 'DSA interview track' : 'Backend + DevOps roadmap'}
        description={
          track === 'dsa'
            ? 'Two phases of patterns and problems to run alongside the core roadmap, with an easy pause option for exam periods.'
            : 'Seven phases, 69 topics and a project per phase. Update a topic\'s status to keep the whole dashboard accurate.'
        }
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {track === 'dsa' ? (
              dsaPaused ? (
                <Button variant="secondary" size="md" onClick={() => void handleResume()} disabled={resumeDsa.isPending}>
                  <PlayCircle className="h-4 w-4" aria-hidden="true" />
                  Resume track
                </Button>
              ) : (
                <Button variant="secondary" size="md" onClick={() => setPauseOpen(true)}>
                  <PauseCircle className="h-4 w-4" aria-hidden="true" />
                  Pause track
                </Button>
              )
            ) : null}
            <Button
              variant="secondary"
              size="md"
              onClick={() => setExpanded(new Set(data.items.map((phase) => phase.id)))}
            >
              <Layers className="h-4 w-4" aria-hidden="true" />
              Expand all
            </Button>
          </div>
        }
      />

      <Card>
        <CardBody className="flex flex-col gap-2 py-2 sm:flex-row sm:items-center">
          <div className="inline-flex rounded-lg border border-line bg-surface-2 p-0.5">
            <button
              type="button"
              onClick={() => switchTrack('core')}
              className={cn(
                'flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition',
                track === 'core' ? 'bg-surface text-text shadow-sm' : 'text-muted hover:text-text',
              )}
            >
              Backend + DevOps
              <span className="rounded-full bg-bg-subtle px-1.5 py-0.5 text-[10px] tabular">
                {coreCount} phases · {coreTopics} topics
              </span>
            </button>
            <button
              type="button"
              onClick={() => switchTrack('dsa')}
              className={cn(
                'flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition',
                track === 'dsa' ? 'bg-surface text-text shadow-sm' : 'text-muted hover:text-text',
              )}
            >
              DSA track
              <Badge tone="accent">Parallel</Badge>
              <span className="rounded-full bg-bg-subtle px-1.5 py-0.5 text-[10px] tabular">
                {dsaCount} phases · {dsaTopics} topics
              </span>
              {dsaPaused ? <Badge tone="warning">Paused</Badge> : null}
            </button>
          </div>
        </CardBody>
      </Card>

      {track === 'dsa' && dsaPaused ? (
        <div className="flex flex-col gap-2 rounded-card border border-warning/40 bg-warning/5 px-4 py-3 text-sm text-text sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <PauseCircle className="h-4 w-4 text-warning" aria-hidden="true" />
            <span>
              DSA track is paused{dsaPausedUntil ? ` until ${dsaPausedUntil}` : ''}. Your progress is saved and won't count against your active dashboard goals.
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => void handleResume()} disabled={resumeDsa.isPending}>
            <PlayCircle className="h-3.5 w-3.5" aria-hidden="true" />
            Resume
          </Button>
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label={track === 'dsa' ? 'DSA completion' : 'Overall completion'}
          value={`${Math.round(data.completion_percentage)}%`}
          hint={`${data.completed_topics} of ${data.total_topics} topics`}
          icon={<Target className="h-4 w-4" aria-hidden="true" />}
          tone="accent"
        />
        <StatCard
          label="Topics complete"
          value={data.completed_topics}
          hint={`${data.total_topics - data.completed_topics} remaining`}
          icon={<CircleCheckBig className="h-4 w-4" aria-hidden="true" />}
          tone="success"
        />
        <StatCard
          label="Phases complete"
          value={`${phasesCompleted}/${data.items.length}`}
          hint={`${inProgress} phase${inProgress === 1 ? '' : 's'} in progress`}
          icon={<Layers className="h-4 w-4" aria-hidden="true" />}
        />
        <StatCard
          label="Estimated study"
          value={`${formatHours(totalEstimated)}h`}
          hint="Across every topic in this track"
          icon={<Clock className="h-4 w-4" aria-hidden="true" />}
        />
      </div>

      <Card>
        <CardBody className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
              aria-hidden="true"
            />
            <Input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search topics, categories or subtopics…"
              aria-label="Search the roadmap"
              className="pl-9"
            />
          </div>
          <div className="flex items-center gap-2">
            <Select
              value={status}
              onChange={(event) => setStatus(event.target.value as 'all' | TopicStatus)}
              aria-label="Filter by topic status"
              className="sm:w-40"
            >
              <option value="all">All statuses</option>
              <option value="not_started">Not started</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Completed</option>
            </Select>
            <Button variant="ghost" size="md" onClick={() => setExpanded(new Set())}>
              Collapse all
            </Button>
          </div>
        </CardBody>
      </Card>

      {filtering ? (
        <p className="text-xs text-muted">
          Showing {visiblePhases.reduce((sum, phase) => sum + phase.topics.length, 0)} topics across{' '}
          {visiblePhases.length} phase{visiblePhases.length === 1 ? '' : 's'}.
        </p>
      ) : null}

      {visiblePhases.length === 0 ? (
        <Card>
          <EmptyState
            icon={Search}
            title="No topics match those filters"
            description="Try a different search term or clear the status filter."
            action={
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setSearch('');
                  setStatus('all');
                }}
              >
                Clear filters
              </Button>
            }
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {visiblePhases.map((phase) => (
            <PhaseCard
              key={phase.id}
              phase={phase}
              index={data.items.findIndex((item) => item.id === phase.id)}
              expanded={isExpanded(phase.id)}
              onToggle={() => toggle(phase.id)}
            />
          ))}
        </div>
      )}

      {track === 'dsa' ? (
        <div className="flex flex-col gap-2 rounded-card border border-line bg-surface-2 px-4 py-3 text-xs text-muted sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-accent" aria-hidden="true" />
            <span>DSA is designed to run in parallel with your core roadmap. Pause it during exams without losing any progress.</span>
          </div>
          <Link to="/dashboard" className="inline-flex items-center gap-1 font-medium text-accent transition hover:text-accent-hover">
            View dashboard
            <ArrowRight className="h-3 w-3" aria-hidden="true" />
          </Link>
        </div>
      ) : null}

      <Modal open={pauseOpen} onClose={() => setPauseOpen(false)} title="Pause DSA track" description="Pause the parallel DSA track for exam season. Your topic progress, notes and checklists stay exactly as they are.">
        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-text" htmlFor="dsa-resume-on">
              Resume on (optional)
            </label>
            <Input
              id="dsa-resume-on"
              type="date"
              value={resumeOn}
              onChange={(event) => setResumeOn(event.target.value)}
            />
            <p className="mt-1 text-[11px] text-muted">Leave blank to pause indefinitely. We'll auto-resume when the date passes.</p>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setPauseOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handlePause()} disabled={pauseDsa.isPending}>
              <PauseCircle className="h-4 w-4" aria-hidden="true" />
              Pause track
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
