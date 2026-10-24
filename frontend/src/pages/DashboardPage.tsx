import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BookOpen,
  CalendarCheck2,
  CheckCircle2,
  Circle,
  Flame,
  FolderKanban,
  GraduationCap,
  Layers,
  PlayCircle,
  Sparkles,
  Target,
  Timer,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useDashboard, useSetTaskCompletion } from '@/api/hooks';
import { Badge, priorityTone, statusLabel, statusTone } from '@/components/ui/Badge';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { PageHeader, StatCard } from '@/components/ui/PageHeader';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { CardSkeleton, Skeleton } from '@/components/ui/Skeleton';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { cn } from '@/lib/cn';
import { formatHours, formatMinutes, relativeTime } from '@/lib/format';
import { usePageTitle } from '@/lib/usePageTitle';
import type { DashboardTaskDto } from '@/types/api';

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

function TodayTask({ task }: { task: DashboardTaskDto }) {
  const complete = useSetTaskCompletion();
  const { notify } = useToast();

  const toggle = async () => {
    try {
      await complete.mutateAsync({ id: task.id, is_completed: !task.is_completed });
      notify(task.is_completed ? 'Task re-opened' : 'Task completed', 'success');
    } catch {
      notify('Could not update the task', 'error');
    }
  };

  return (
    <li className="flex items-start gap-2.5 py-2.5">
      <button
        type="button"
        onClick={() => void toggle()}
        disabled={complete.isPending}
        className="mt-0.5 shrink-0 text-faint transition hover:text-accent disabled:opacity-50"
        aria-label={task.is_completed ? `Re-open ${task.title}` : `Complete ${task.title}`}
      >
        {task.is_completed ? (
          <CheckCircle2 className="h-[18px] w-[18px] text-success" />
        ) : (
          <Circle className="h-[18px] w-[18px]" />
        )}
      </button>
      <div className="min-w-0 flex-1">
        <p
          className={`text-sm leading-snug ${
            task.is_completed ? 'text-faint line-through' : 'font-medium text-text'
          }`}
        >
          {task.title}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-1.5">
          <Badge>{task.category}</Badge>
          <Badge tone={priorityTone(task.priority)}>{statusLabel(task.priority)}</Badge>
          <span className="inline-flex items-center gap-1 text-[11px] text-muted">
            <Timer className="h-3 w-3" aria-hidden="true" />
            {formatMinutes(task.estimated_minutes)}
          </span>
        </div>
      </div>
    </li>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-5">
      <div>
        <Skeleton className="h-3 w-32" />
        <Skeleton className="mt-2 h-7 w-72" />
        <Skeleton className="mt-2 h-4 w-96 max-w-full" />
      </div>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <CardSkeleton key={index} />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="This week" />
          <CardBody>
            <Skeleton className="h-52 w-full" />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Today" />
          <CardBody className="space-y-3">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-10 w-full" />
            ))}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  usePageTitle('Dashboard');
  const { data, isLoading, isError, refetch } = useDashboard();
  const { user } = useAuth();
  const navigate = useNavigate();

  if (isLoading) return <DashboardSkeleton />;

  if (isError || !data) {
    return (
      <div className="space-y-5">
        <PageHeader title="Dashboard" description="Your learning progress at a glance." />
        <ErrorState
          title="Could not load your dashboard"
          description="We could not reach the DevPath API. Make sure the backend is running and try again."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  const firstName = (user?.full_name || user?.username || 'there').split(' ')[0];
  const nextTopic = data.next_recommended_topic;
  const goal = data.weekly_study[0]?.goal_minutes ?? 0;
  const phasesComplete = data.phase_progress.filter((phase) => phase.status === 'completed').length;
  const today = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={today}
        title={`${greeting()}, ${firstName}`}
        description={
          data.todays_planned_minutes > 0
            ? `You have ${formatMinutes(
                data.todays_planned_minutes,
              )} planned today. Small, consistent sessions compound.`
            : 'No study time planned yet today. A focused 45-minute session is enough to keep the streak alive.'
        }
        actions={
          <>
            <button
              type="button"
              onClick={() => navigate('/roadmap')}
              className="inline-flex h-[38px] items-center gap-2 rounded-lg border border-line bg-surface px-3.5 text-sm font-medium text-text shadow-card transition hover:bg-surface-hover"
            >
              <BookOpen className="h-4 w-4" aria-hidden="true" />
              Roadmap
            </button>
            <button
              type="button"
              onClick={() => navigate('/planner')}
              className="inline-flex h-[38px] items-center gap-2 rounded-lg bg-accent px-3.5 text-sm font-medium text-accent-fg shadow-card transition hover:bg-accent-hover"
            >
              <CalendarCheck2 className="h-4 w-4" aria-hidden="true" />
              Open planner
            </button>
          </>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Roadmap completion"
          value={`${Math.round(data.overall_completion_percentage)}%`}
          hint={`${data.completed_topics} of ${data.total_topics} topics complete`}
          icon={<Target className="h-4 w-4" aria-hidden="true" />}
          tone="accent"
        />
        <StatCard
          label="Study time"
          value={`${formatHours(data.total_study_minutes)}h`}
          hint={`${formatMinutes(data.total_study_minutes)} logged in total`}
          icon={<GraduationCap className="h-4 w-4" aria-hidden="true" />}
        />
        <StatCard
          label="Current streak"
          value={`${data.current_streak} ${data.current_streak === 1 ? 'day' : 'days'}`}
          hint={`Longest streak: ${data.longest_streak} days`}
          icon={<Flame className="h-4 w-4" aria-hidden="true" />}
          tone={data.current_streak > 0 ? 'success' : 'default'}
        />
        <StatCard
          label="Projects shipped"
          value={`${data.projects_completed}/${data.projects_total}`}
          hint={`${data.in_progress_topics} topics in progress`}
          icon={<FolderKanban className="h-4 w-4" aria-hidden="true" />}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardHeader
              title="This week"
              description="Minutes from recorded study sessions, with your daily goal as a guide."
              action={
                <span className="tabular text-xs font-medium text-muted">
                  {formatHours(data.weekly_study.reduce((sum, day) => sum + day.minutes, 0))}h total
                </span>
              }
            />
            <CardBody className="pt-3">
              {data.weekly_study.length === 0 ? (
                <EmptyState
                  icon={Timer}
                  title="No study sessions yet"
                  description="Log your first session from the planner and your week will appear here."
                />
              ) : (
                <div className="h-[220px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.weekly_study} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}>
                      <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" vertical={false} />
                      <XAxis
                        dataKey="label"
                        tickLine={false}
                        axisLine={false}
                        tick={{ fill: 'var(--text-faint)', fontSize: 11 }}
                      />
                      <YAxis
                        tickLine={false}
                        axisLine={false}
                        tick={{ fill: 'var(--text-faint)', fontSize: 11 }}
                        allowDecimals={false}
                      />
                      <Tooltip
                        cursor={{ fill: 'var(--surface-hover)' }}
                        contentStyle={{
                          background: 'var(--surface)',
                          border: '1px solid var(--line)',
                          borderRadius: 10,
                          fontSize: 12,
                          color: 'var(--text)',
                          boxShadow: 'var(--shadow-md)',
                        }}
                        labelStyle={{ color: 'var(--text)', fontWeight: 600 }}
                        itemStyle={{ color: 'var(--text-muted)' }}
                        labelFormatter={(label) => String(label)}
                      />
                      {goal > 0 ? (
                        <ReferenceLine
                          y={goal}
                          stroke="var(--line-strong)"
                          strokeDasharray="4 4"
                          label={{
                            value: 'goal',
                            position: 'insideTopRight',
                            fill: 'var(--text-faint)',
                            fontSize: 10,
                          }}
                        />
                      ) : null}
                      <Bar dataKey="minutes" name="Minutes" fill="var(--accent)" radius={[6, 6, 0, 0]} maxBarSize={46} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardBody>
          </Card>

          {nextTopic.id ? (
            <div className="relative overflow-hidden rounded-card border border-accent/20 bg-accent-soft p-5 shadow-card">
              <div className="relative z-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0">
                  <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-accent-soft-fg">
                    <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
                    Continue learning
                  </p>
                  <h2 className="mt-1.5 text-base font-semibold text-text">{nextTopic.title}</h2>
                  <p className="mt-1 line-clamp-2 max-w-xl text-xs leading-relaxed text-muted">
                    {nextTopic.description}
                  </p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-muted">
                    {nextTopic.category ? <Badge tone="accent">{nextTopic.category}</Badge> : null}
                    {nextTopic.estimated_minutes ? (
                      <span className="inline-flex items-center gap-1">
                        <Timer className="h-3 w-3" aria-hidden="true" />
                        {formatMinutes(nextTopic.estimated_minutes)}
                      </span>
                    ) : null}
                  </div>
                </div>
                <Link
                  to={`/roadmap/topics/${nextTopic.id}`}
                  className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-accent-fg shadow-card transition hover:bg-accent-hover"
                >
                  <PlayCircle className="h-4 w-4" aria-hidden="true" />
                  Start topic
                </Link>
              </div>
            </div>
          ) : (
            <Card>
              <CardBody className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-success" aria-hidden="true" />
                <div>
                  <p className="text-sm font-semibold text-text">Every topic is complete</p>
                  <p className="text-xs text-muted">
                    Revisit a phase to keep your notes sharp, or polish your capstone project.
                  </p>
                </div>
              </CardBody>
            </Card>
          )}

          <Card>
            <CardHeader
              title="Today's plan"
              description={`${formatMinutes(data.todays_completed_minutes)} of ${formatMinutes(
                data.todays_goal_minutes,
              )} goal`}
              action={
                <Link
                  to="/planner"
                  className="inline-flex items-center gap-1 text-xs font-medium text-accent transition hover:text-accent-hover"
                >
                  Open planner <ArrowRight className="h-3 w-3" aria-hidden="true" />
                </Link>
              }
            />
            <CardBody className="pt-1">
              <ProgressBar
                value={data.todays_goal_percentage}
                tone={data.todays_goal_percentage >= 100 ? 'success' : 'accent'}
                className="mb-2"
                showValue
              />
              {data.todays_tasks.length === 0 ? (
                <EmptyState
                  icon={CalendarCheck2}
                  title="Nothing scheduled for today"
                  description="Plan one focused task so the day has a clear outcome."
                  action={
                    <Link
                      to="/planner"
                      className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-accent-fg transition hover:bg-accent-hover"
                    >
                      Plan today's study <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                    </Link>
                  }
                />
              ) : (
                <ul className="divide-y divide-line">
                  {data.todays_tasks.map((task) => (
                    <TodayTask key={task.id} task={task} />
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader
              title="Current phase"
              description={
                data.current_phase.title
                  ? `${data.current_phase.month_label ?? ''} · ${
                      data.current_phase.completed_topics ?? 0}/${data.current_phase.total_topics ?? 0} topics`
                  : undefined
              }
              action={<Layers className="h-4 w-4 text-faint" aria-hidden="true" />}
            />
            <CardBody>
              {data.current_phase.title ? (
                <>
                  <p className="text-sm font-semibold text-text">{data.current_phase.title}</p>
                  <p className="mt-1 line-clamp-3 text-xs leading-relaxed text-muted">
                    {data.current_phase.project_brief}
                  </p>
                  <ProgressBar
                    className="mt-3"
                    value={data.current_phase.completion_percentage ?? 0}
                    showValue
                    label={`${phasesComplete} of ${data.phase_progress.length} phases complete`}
                  />
                  <Link
                    to="/roadmap"
                    className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-accent transition hover:text-accent-hover"
                  >
                    View roadmap <ArrowRight className="h-3 w-3" aria-hidden="true" />
                  </Link>
                </>
              ) : (
                <p className="text-xs text-muted">The roadmap is still loading.</p>
              )}
            </CardBody>
          </Card>

          {data.dsa ? (
            <Card className={cn(data.dsa.paused ? 'border-warning/40' : '')}>
              <CardHeader
                title="DSA track"
                description={
                  data.dsa.paused
                    ? `Paused${data.dsa.paused_until ? ` until ${data.dsa.paused_until}` : ''}`
                    : `${data.dsa.completed_topics}/${data.dsa.total_topics} topics`
                }
                action={
                  data.dsa.paused ? (
                    <Badge tone="warning">Paused</Badge>
                  ) : (
                    <Badge tone="accent">Parallel</Badge>
                  )
                }
              />
              <CardBody className="space-y-3">
                <ProgressBar
                  value={data.dsa.completion_percentage}
                  showValue
                  tone={data.dsa.paused ? 'warning' : 'accent'}
                />
                {data.dsa.paused ? (
                  <p className="text-xs text-muted">
                    Pausing during exams removes DSA from active targets. Progress is kept.
                  </p>
                ) : data.dsa.next_recommended_topic?.id ? (
                  <div className="rounded-lg border border-line bg-surface-2 p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-faint">
                      Next up
                    </p>
                    <Link
                      to={`/roadmap/topics/${data.dsa.next_recommended_topic.id}?track=dsa`}
                      className="mt-1 block text-sm font-medium text-text transition hover:text-accent"
                    >
                      {data.dsa.next_recommended_topic.title}
                    </Link>
                    <p className="mt-1 text-xs text-muted">
                      {data.dsa.next_recommended_topic.category}
                      {data.dsa.next_recommended_topic.estimated_minutes
                        ? ` · ${formatMinutes(data.dsa.next_recommended_topic.estimated_minutes)}`
                        : ''}
                    </p>
                  </div>
                ) : (
                  <p className="text-xs text-muted">Complete your next DSA problem to see progress here.</p>
                )}
                <Link
                  to="/roadmap?track=dsa"
                  className="inline-flex items-center gap-1 text-xs font-medium text-accent transition hover:text-accent-hover"
                >
                  Manage DSA track <ArrowRight className="h-3 w-3" aria-hidden="true" />
                </Link>
              </CardBody>
            </Card>
          ) : null}

          <Card>
            <CardHeader title="Phase progress" action={<span className="text-[11px] text-muted">{data.phase_progress.length} phases</span>} />
            <CardBody className="space-y-3 pt-2">
              {data.phase_progress.map((phase) => (
                <div key={phase.key}>
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <span className="flex min-w-0 items-center gap-1.5 text-xs text-text">
                      <span
                        className="h-1.5 w-1.5 shrink-0 rounded-full"
                        style={{
                          background:
                            phase.status === 'completed'
                              ? 'var(--success)'
                              : phase.status === 'in_progress'
                                ? 'var(--accent)'
                                : 'var(--line-strong)',
                        }}
                      />
                      <span className="truncate">{phase.title}</span>
                    </span>
                    <span className="tabular shrink-0 text-[11px] text-muted">
                      {phase.completed_topics}/{phase.total_topics}
                    </span>
                  </div>
                  <ProgressBar
                    value={phase.completion_percentage}
                    size="sm"
                    tone={phase.status === 'completed' ? 'success' : 'accent'}
                  />
                </div>
              ))}
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Projects"
              action={
                <Link to="/projects" className="text-xs font-medium text-accent hover:text-accent-hover">
                  All projects
                </Link>
              }
            />
            <CardBody className="space-y-3 pt-2">
              {data.projects.length === 0 ? (
                <p className="text-xs text-muted">No projects yet.</p>
              ) : (
                data.projects.map((project) => (
                  <Link
                    key={project.id}
                    to="/projects"
                    className="block rounded-lg border border-line bg-surface-2 p-3 transition hover:bg-surface-hover"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-medium leading-snug text-text">{project.name}</p>
                      <Badge tone={statusTone(project.status)}>{statusLabel(project.status)}</Badge>
                    </div>
                    <ProgressBar
                      className="mt-2"
                      value={project.completion_percentage}
                      size="sm"
                      tone={project.status === 'completed' ? 'success' : 'accent'}
                    />
                    <p className="mt-1 text-[10px] text-muted">
                      {project.completed_milestones}/{project.milestone_count} milestones
                    </p>
                  </Link>
                ))
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Upcoming milestones" />
            <CardBody className="pt-2">
              {data.upcoming_milestones.length === 0 ? (
                <p className="text-xs text-muted">Nothing due soon. Keep building.</p>
              ) : (
                <ul className="space-y-2.5">
                  {data.upcoming_milestones.map((milestone) => {
                    const Icon = milestone.kind === 'project' ? FolderKanban : BookOpen;
                    return (
                      <li key={`${milestone.kind}-${milestone.id}`} className="flex items-start gap-2">
                        <span
                          className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md ${
                            milestone.completed
                              ? 'bg-success-soft text-success'
                              : 'bg-surface-2 text-muted'
                          }`}
                        >
                          {milestone.completed ? (
                            <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                          ) : (
                            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                          )}
                        </span>
                        <div className="min-w-0">
                          <p className="truncate text-xs font-medium text-text">{milestone.title}</p>
                          <p className="truncate text-[10px] text-muted">
                            {milestone.subtitle}
                            {milestone.due_label ? ` · ${milestone.due_label}` : ''}
                          </p>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Recent activity" />
            <CardBody className="pt-2">
              {data.recent_activity.length === 0 ? (
                <p className="text-xs text-muted">Complete a topic or log a session to start your history.</p>
              ) : (
                <ul className="space-y-3">
                  {data.recent_activity.slice(0, 6).map((activity) => (
                    <li key={activity.id} className="flex items-start gap-2">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                      <div className="min-w-0">
                        <p className="text-xs leading-snug text-text">{activity.title}</p>
                        <p className="text-[10px] text-muted">
                          {activity.detail ? `${activity.detail} · ` : ''}
                          {relativeTime(activity.occurred_at)}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>
        </div>
      </div>

    </div>
  );
}
