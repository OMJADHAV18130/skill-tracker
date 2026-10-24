import { useEffect, useMemo, useState } from 'react';
import {
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Circle,
  Clock,
  Flame,
  Plus,
  Timer,
  Trash2,
  Pencil,
  Play,
  RotateCcw,
} from 'lucide-react';
import {
  useCalendar,
  useCarryForward,
  useCreateSession,
  useCreateTask,
  useDay,
  useDeleteSession,
  useDeleteTask,
  useLogTaskTime,
  useSetTaskCompletion,
  useStreak,
  useUpdateTask,
  useWeek,
} from '@/api/hooks';
import type { TaskInput } from '@/api/endpoints';
import { Badge, priorityTone, statusLabel } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Field, Input, Select, Textarea } from '@/components/ui/Field';
import { Modal } from '@/components/ui/Modal';
import { PageHeader, StatCard } from '@/components/ui/PageHeader';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { CardSkeleton, Skeleton } from '@/components/ui/Skeleton';
import { Checkbox } from '@/components/ui/Toggle';
import { useToast } from '@/contexts/ToastContext';
import { cn } from '@/lib/cn';
import { TASK_CATEGORIES, WEEKDAYS } from '@/lib/constants';
import { errorMessage } from '@/lib/errors';
import {
  addDays,
  formatDate,
  formatDayLabel,
  formatMinutes,
  monthLabel,
  parseDate,
  startOfWeek,
  toISODate,
  todayISO,
} from '@/lib/format';
import { usePageTitle } from '@/lib/usePageTitle';
import type { DailyTask, Priority } from '@/types/api';

/* ------------------------------------------------------------------ tasks */

interface TaskFormState {
  title: string;
  description: string;
  category: string;
  estimated_minutes: string;
  priority: Priority;
  task_date: string;
}

function TaskFormModal({
  open,
  onClose,
  task,
  date,
}: {
  open: boolean;
  onClose: () => void;
  task: DailyTask | null;
  date: string;
}) {
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const { notify } = useToast();
  const [form, setForm] = useState<TaskFormState>({
    title: '',
    description: '',
    category: 'General',
    estimated_minutes: '45',
    priority: 'medium',
    task_date: date,
  });
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setFormError(null);
    setForm(
      task
        ? {
            title: task.title,
            description: task.description ?? '',
            category: task.category,
            estimated_minutes: String(task.estimated_minutes),
            priority: task.priority,
            task_date: task.task_date,
          }
        : {
            title: '',
            description: '',
            category: 'General',
            estimated_minutes: '45',
            priority: 'medium',
            task_date: date,
          },
    );
  }, [open, task, date]);

  const set = <K extends keyof TaskFormState>(key: K, value: TaskFormState[K]) =>
    setForm((current) => ({ ...current, [key]: value }));

  const submit = async () => {
    const title = form.title.trim();
    if (!title) {
      setFormError('Give the task a clear title.');
      return;
    }
    const minutes = Number(form.estimated_minutes);
    if (!Number.isFinite(minutes) || minutes < 0 || minutes > 1440) {
      setFormError('Estimated time must be between 0 and 1440 minutes.');
      return;
    }
    const payload: TaskInput = {
      title,
      description: form.description.trim() || null,
      category: form.category.trim() || 'General',
      estimated_minutes: Math.round(minutes),
      priority: form.priority,
      task_date: form.task_date,
    };
    try {
      if (task) {
        await updateTask.mutateAsync({ id: task.id, body: payload });
        notify('Task updated', 'success');
      } else {
        await createTask.mutateAsync(payload);
        notify('Task added to your plan', 'success');
      }
      onClose();
    } catch (error) {
      setFormError(errorMessage(error, 'Could not save the task.'));
    }
  };

  const busy = createTask.isPending || updateTask.isPending;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={task ? 'Edit task' : 'Plan a task'}
      description="Keep tasks small enough to finish in one focused session."
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose} disabled={busy}>
            Cancel
          </Button>
          <Button size="sm" onClick={() => void submit()} loading={busy}>
            {task ? 'Save changes' : 'Add task'}
          </Button>
        </>
      }
    >
      <div className="space-y-3">
        {formError ? (
          <p className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger" role="alert">
            {formError}
          </p>
        ) : null}
        <Field label="Title" htmlFor="task-title">
          <Input
            id="task-title"
            value={form.title}
            onChange={(event) => set('title', event.target.value)}
            placeholder="e.g. Finish the JPA relationships chapter"
            autoFocus
            maxLength={240}
          />
        </Field>
        <Field label="Description" htmlFor="task-description" hint="Optional — what exactly will you do?">
          <Textarea
            id="task-description"
            value={form.description}
            onChange={(event) => set('description', event.target.value)}
            placeholder="A concrete outcome for this session…"
            rows={2}
          />
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Date" htmlFor="task-date">
            <Input
              id="task-date"
              type="date"
              value={form.task_date}
              onChange={(event) => set('task_date', event.target.value)}
            />
          </Field>
          <Field label="Estimated minutes" htmlFor="task-minutes">
            <Input
              id="task-minutes"
              type="number"
              min={0}
              max={1440}
              step={5}
              value={form.estimated_minutes}
              onChange={(event) => set('estimated_minutes', event.target.value)}
            />
          </Field>
          <Field label="Category" htmlFor="task-category">
            <Input
              id="task-category"
              list="task-category-options"
              value={form.category}
              onChange={(event) => set('category', event.target.value)}
              placeholder="General"
            />
            <datalist id="task-category-options">
              {TASK_CATEGORIES.map((category) => (
                <option key={category} value={category} />
              ))}
            </datalist>
          </Field>
          <Field label="Priority" htmlFor="task-priority">
            <Select
              id="task-priority"
              value={form.priority}
              onChange={(event) => set('priority', event.target.value as Priority)}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </Select>
          </Field>
        </div>
      </div>
    </Modal>
  );
}

function LogTimeModal({
  task,
  onClose,
}: {
  task: DailyTask | null;
  onClose: () => void;
}) {
  const logTime = useLogTaskTime();
  const { notify } = useToast();
  const [minutes, setMinutes] = useState('45');
  const [note, setNote] = useState('');
  const [complete, setComplete] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!task) return;
    setMinutes(String(task.estimated_minutes || 45));
    setNote(task.session_note ?? '');
    setComplete(!task.is_completed);
    setFormError(null);
  }, [task]);

  if (!task) return null;

  const submit = async () => {
    const value = Number(minutes);
    if (!Number.isFinite(value) || value < 0 || value > 1440) {
      setFormError('Enter between 0 and 1440 minutes.');
      return;
    }
    try {
      await logTime.mutateAsync({
        id: task.id,
        minutes: Math.round(value),
        note: note.trim() || undefined,
        completed: complete,
      });
      notify('Study time logged', 'success');
      onClose();
    } catch (error) {
      setFormError(errorMessage(error, 'Could not log the time.'));
    }
  };

  return (
    <Modal
      open={Boolean(task)}
      onClose={onClose}
      title="Log study time"
      description={task.title}
      size="sm"
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose} disabled={logTime.isPending}>
            Cancel
          </Button>
          <Button size="sm" onClick={() => void submit()} loading={logTime.isPending}>
            Save session
          </Button>
        </>
      }
    >
      <div className="space-y-3">
        {formError ? (
          <p className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger" role="alert">
            {formError}
          </p>
        ) : null}
        <Field label="Minutes studied" htmlFor="log-minutes">
          <Input
            id="log-minutes"
            type="number"
            min={0}
            max={1440}
            step={5}
            value={minutes}
            onChange={(event) => setMinutes(event.target.value)}
            autoFocus
          />
        </Field>
        <Field label="Session note" htmlFor="log-note" hint="What did you work through?">
          <Textarea
            id="log-note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            rows={2}
            placeholder="e.g. Implemented pagination and added two tests"
          />
        </Field>
        <label className="flex items-center gap-2 text-xs text-text">
          <Checkbox checked={complete} onChange={(event) => setComplete(event.target.checked)} />
          Mark this task complete
        </label>
      </div>
    </Modal>
  );
}

function SessionModal({
  open,
  onClose,
  date,
}: {
  open: boolean;
  onClose: () => void;
  date: string;
}) {
  const createSession = useCreateSession();
  const { notify } = useToast();
  const [minutes, setMinutes] = useState('30');
  const [note, setNote] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setMinutes('30');
    setNote('');
    setFormError(null);
  }, [open]);

  const submit = async () => {
    const value = Number(minutes);
    if (!Number.isFinite(value) || value < 1 || value > 1440) {
      setFormError('Enter between 1 and 1440 minutes.');
      return;
    }
    try {
      await createSession.mutateAsync({
        minutes: Math.round(value),
        session_date: date,
        note: note.trim() || null,
      });
      notify('Study session recorded', 'success');
      onClose();
    } catch (error) {
      setFormError(errorMessage(error, 'Could not record the session.'));
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Log a study session"
      description="Use this for reading, videos or practice that is not tied to a planned task."
      size="sm"
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose} disabled={createSession.isPending}>
            Cancel
          </Button>
          <Button size="sm" onClick={() => void submit()} loading={createSession.isPending}>
            Record session
          </Button>
        </>
      }
    >
      <div className="space-y-3">
        {formError ? (
          <p className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger" role="alert">
            {formError}
          </p>
        ) : null}
        <Field label="Minutes" htmlFor="session-minutes">
          <Input
            id="session-minutes"
            type="number"
            min={1}
            max={1440}
            step={5}
            value={minutes}
            onChange={(event) => setMinutes(event.target.value)}
            autoFocus
          />
        </Field>
        <Field label="Note" htmlFor="session-note" hint="Optional">
          <Textarea
            id="session-note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            rows={2}
            placeholder="What did you study?"
          />
        </Field>
      </div>
    </Modal>
  );
}

/* ------------------------------------------------------------------- page */

function WeekStrip({
  date,
  dailyMinutes,
  onSelect,
}: {
  date: string;
  dailyMinutes: Record<string, number>;
  onSelect: (date: string) => void;
}) {
  const dateObj = parseDate(date) ?? new Date();
  const start = startOfWeek(dateObj);
  const days = Array.from({ length: 7 }, (_, index) => {
    const day = addDays(start, index);
    const iso = toISODate(day);
    return { iso, day, minutes: dailyMinutes[iso] ?? 0 };
  });

  return (
    <div className="grid grid-cols-7 gap-1">
      {days.map(({ iso, day, minutes }) => {
        const selected = iso === date;
        const isToday = iso === todayISO();
        return (
          <button
            key={iso}
            type="button"
            onClick={() => onSelect(iso)}
            className={cn(
              'flex flex-col items-center gap-0.5 rounded-lg border px-1 py-2 transition',
              selected
                ? 'border-accent bg-accent text-accent-fg'
                : 'border-line bg-surface text-muted hover:bg-surface-hover hover:text-text',
            )}
            aria-pressed={selected}
            aria-label={`${formatDate(iso, { weekday: 'long', month: 'long', day: 'numeric' })}`}
          >
            <span className={cn('text-[10px] font-medium uppercase', selected ? 'text-accent-fg/75' : 'text-faint')}>
              {formatDayLabel(day)}
            </span>
            <span className="tabular text-sm font-semibold">{day.getDate()}</span>
            <span
              className={cn(
                'h-1 w-1 rounded-full',
                minutes > 0 ? (selected ? 'bg-accent-fg' : 'bg-accent') : 'bg-transparent',
              )}
              aria-hidden="true"
            />
            {isToday && !selected ? <span className="sr-only">Today</span> : null}
          </button>
        );
      })}
    </div>
  );
}

function CalendarHeatmap({
  calendar,
  cursor,
  onShiftMonth,
  selectedDate,
  onSelectDate,
}: {
  calendar: ReturnType<typeof useCalendar>['data'];
  cursor: { year: number; month: number };
  onShiftMonth: (delta: number) => void;
  selectedDate: string;
  onSelectDate: (date: string) => void;
}) {
  const daysInMonth = new Date(cursor.year, cursor.month, 0).getDate();
  const offset = (new Date(cursor.year, cursor.month - 1, 1).getDay() + 6) % 7;
  const byDate = useMemo(
    () => new Map((calendar?.days ?? []).map((day) => [day.date, day])),
    [calendar],
  );
  const cells: Array<{ iso: string; dayNumber: number } | null> = [
    ...Array.from({ length: offset }, () => null),
    ...Array.from({ length: daysInMonth }, (_, index) => ({
      iso: toISODate(new Date(cursor.year, cursor.month - 1, index + 1)),
      dayNumber: index + 1,
    })),
  ];

  return (
    <Card>
      <CardHeader
        title="Study calendar"
        description="Every day you study, at a glance."
        action={
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onShiftMonth(-1)}
              className="rounded-lg p-1.5 text-muted transition hover:bg-surface-hover hover:text-text"
              aria-label="Previous month"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="min-w-[7.5rem] text-center text-xs font-medium text-text">
              {monthLabel(cursor.year, cursor.month)}
            </span>
            <button
              type="button"
              onClick={() => onShiftMonth(1)}
              className="rounded-lg p-1.5 text-muted transition hover:bg-surface-hover hover:text-text"
              aria-label="Next month"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        }
      />
      <CardBody className="pt-3">
        <div className="grid grid-cols-7 gap-1">
          {WEEKDAYS.map((label) => (
            <div key={label} className="pb-1 text-center text-[10px] font-medium uppercase tracking-wide text-faint">
              {label}
            </div>
          ))}
          {cells.map((cell, index) => {
            if (!cell) return <div key={`blank-${index}`} aria-hidden="true" />;
            const activity = byDate.get(cell.iso);
            const minutes = activity?.total_minutes ?? 0;
            const isSelected = cell.iso === selectedDate;
            const isToday = cell.iso === todayISO();
            const heat =
              minutes >= 120
                ? 'bg-accent text-accent-fg'
                : minutes >= 60
                  ? 'bg-accent/55 text-accent-fg'
                  : minutes >= 30
                    ? 'bg-accent/30 text-text'
                    : minutes > 0
                      ? 'bg-accent/15 text-text'
                      : activity?.has_activity
                        ? 'bg-surface-2 text-muted ring-1 ring-inset ring-line-strong'
                        : 'bg-surface-2 text-faint';
            return (
              <button
                key={cell.iso}
                type="button"
                onClick={() => onSelectDate(cell.iso)}
                title={`${formatDate(cell.iso)} — ${formatMinutes(minutes)}${
                  activity?.completed_tasks ? ` · ${activity.completed_tasks} tasks` : ''
                }`}
                className={cn(
                  'tabular flex aspect-square items-center justify-center rounded-md text-[11px] font-medium transition hover:opacity-80',
                  heat,
                  isSelected && 'ring-2 ring-accent ring-offset-1 ring-offset-surface',
                  isToday && !isSelected && 'ring-1 ring-inset ring-accent/60',
                )}
                aria-pressed={isSelected}
                aria-label={`${formatDate(cell.iso)}: ${formatMinutes(minutes)} studied`}
              >
                {cell.dayNumber}
              </button>
            );
          })}
        </div>
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[10px] text-muted">
          <div className="flex items-center gap-1.5">
            <span>Less</span>
            {['bg-surface-2', 'bg-accent/15', 'bg-accent/30', 'bg-accent/55', 'bg-accent'].map((tone) => (
              <span key={tone} className={cn('h-3 w-3 rounded-sm', tone)} />
            ))}
            <span>More</span>
          </div>
          <span className="tabular">
            {formatMinutes(calendar?.total_minutes ?? 0)} across {calendar?.active_days ?? 0} active days
          </span>
        </div>
      </CardBody>
    </Card>
  );
}

export default function PlannerPage() {
  usePageTitle('Daily planner');
  const [date, setDate] = useState(todayISO());
  const [calendarCursor, setCalendarCursor] = useState(() => {
    const today = parseDate(todayISO()) ?? new Date();
    return { year: today.getFullYear(), month: today.getMonth() + 1 };
  });
  const [taskModal, setTaskModal] = useState<{ open: boolean; task: DailyTask | null }>({
    open: false,
    task: null,
  });
  const [logTask, setLogTask] = useState<DailyTask | null>(null);
  const [sessionModalOpen, setSessionModalOpen] = useState(false);
  const [confirm, setConfirm] = useState<
    { kind: 'task' | 'session'; id: string; title: string } | null
  >(null);

  const dayQuery = useDay(date);
  const weekQuery = useWeek(date);
  const streakQuery = useStreak();
  const calendarQuery = useCalendar(calendarCursor.year, calendarCursor.month);
  const setCompletion = useSetTaskCompletion();
  const carryForward = useCarryForward();
  const deleteTask = useDeleteTask();
  const deleteSession = useDeleteSession();
  const { notify } = useToast();

  useEffect(() => {
    const parsed = parseDate(date);
    if (parsed) setCalendarCursor({ year: parsed.getFullYear(), month: parsed.getMonth() + 1 });
  }, [date]);

  const plan = dayQuery.data;
  const week = weekQuery.data;
  const streak = streakQuery.data;

  const selectedDateObj = parseDate(date) ?? new Date();
  const isToday = date === todayISO();

  const shiftDate = (days: number) => setDate(toISODate(addDays(selectedDateObj, days)));
  const shiftMonth = (delta: number) => {
    setCalendarCursor((current) => {
      const next = new Date(current.year, current.month - 1 + delta, 1);
      return { year: next.getFullYear(), month: next.getMonth() + 1 };
    });
  };

  const tasks = useMemo(() => {
    if (!plan) return [];
    const weight: Record<Priority, number> = { high: 0, medium: 1, low: 2 };
    return [...plan.tasks].sort(
      (a, b) =>
        Number(a.is_completed) - Number(b.is_completed) ||
        weight[a.priority] - weight[b.priority] ||
        a.created_at.localeCompare(b.created_at),
    );
  }, [plan]);

  const toggleTask = async (task: DailyTask) => {
    try {
      await setCompletion.mutateAsync({ id: task.id, is_completed: !task.is_completed });
      notify(task.is_completed ? 'Task re-opened' : 'Task completed', 'success');
    } catch (error) {
      notify(errorMessage(error, 'Could not update the task'), 'error');
    }
  };

  const moveToTomorrow = async (task: DailyTask) => {
    const taskDate = parseDate(task.task_date) ?? new Date();
    try {
      await carryForward.mutateAsync({ id: task.id, target: toISODate(addDays(taskDate, 1)) });
      notify('Task carried forward to tomorrow', 'success');
    } catch (error) {
      notify(errorMessage(error, 'Could not carry the task forward'), 'error');
    }
  };

  const performDelete = async () => {
    if (!confirm) return;
    try {
      if (confirm.kind === 'task') await deleteTask.mutateAsync(confirm.id);
      else await deleteSession.mutateAsync(confirm.id);
      notify(confirm.kind === 'task' ? 'Task deleted' : 'Session deleted', 'success');
      setConfirm(null);
    } catch (error) {
      notify(errorMessage(error, 'Could not delete this item'), 'error');
    }
  };

  if (dayQuery.isLoading) {
    return (
      <div className="space-y-5">
        <div>
          <Skeleton className="h-3 w-24" />
          <Skeleton className="mt-2 h-7 w-60" />
        </div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <CardSkeleton key={index} />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <Skeleton className="h-96 lg:col-span-2" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (dayQuery.isError || !plan) {
    return (
      <div className="space-y-5">
        <PageHeader title="Daily planner" description="Plan focused sessions and log what you actually studied." />
        <ErrorState onRetry={() => void dayQuery.refetch()} />
      </div>
    );
  }

  const categoryEntries = Object.entries(week?.by_category ?? {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);
  const categoryMax = Math.max(1, ...categoryEntries.map(([, minutes]) => minutes));

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow={isToday ? 'Today' : formatDate(date)}
        title="Daily planner"
        description="Plan the next focused session, then log the minutes when you finish. Everything feeds your streak and dashboard."
        actions={
          <>
            <Button variant="secondary" onClick={() => setSessionModalOpen(true)}>
              <Timer className="h-4 w-4" aria-hidden="true" />
              Log session
            </Button>
            <Button onClick={() => setTaskModal({ open: true, task: null })}>
              <Plus className="h-4 w-4" aria-hidden="true" />
              Add task
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Planned today"
          value={formatMinutes(plan.summary.planned_minutes)}
          hint={`${plan.summary.planned_tasks} task${plan.summary.planned_tasks === 1 ? '' : 's'}`}
          icon={<CalendarDays className="h-4 w-4" aria-hidden="true" />}
          tone="accent"
        />
        <StatCard
          label="Logged study"
          value={formatMinutes(plan.summary.logged_minutes)}
          hint={`${plan.sessions.length} session${plan.sessions.length === 1 ? '' : 's'}`}
          icon={<Clock className="h-4 w-4" aria-hidden="true" />}
        />
        <StatCard
          label="Tasks complete"
          value={`${plan.summary.completed_tasks}/${plan.summary.planned_tasks}`}
          hint={`${formatMinutes(plan.summary.completed_minutes)} completed`}
          icon={<CheckCircle2 className="h-4 w-4" aria-hidden="true" />}
          tone={plan.summary.completed_tasks === plan.summary.planned_tasks && plan.summary.planned_tasks > 0 ? 'success' : 'default'}
        />
        <StatCard
          label="Streak"
          value={`${streak?.current_streak ?? 0} days`}
          hint={`Longest: ${streak?.longest_streak ?? 0} · ${streak?.total_active_days ?? 0} active`}
          icon={<Flame className="h-4 w-4" aria-hidden="true" />}
          tone={(streak?.current_streak ?? 0) > 0 ? 'success' : 'default'}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardBody className="space-y-3">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => shiftDate(-1)}
                    className="rounded-lg border border-line p-1.5 text-muted transition hover:bg-surface-hover hover:text-text"
                    aria-label="Previous day"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <div>
                    <p className="text-sm font-semibold text-text">
                      {formatDate(date, { weekday: 'long', month: 'long', day: 'numeric' })}
                    </p>
                    <p className="text-[11px] text-muted">
                      {isToday ? 'Today' : formatDate(date, { year: 'numeric' })}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => shiftDate(1)}
                    className="rounded-lg border border-line p-1.5 text-muted transition hover:bg-surface-hover hover:text-text"
                    aria-label="Next day"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  <Input
                    type="date"
                    value={date}
                    onChange={(event) => event.target.value && setDate(event.target.value)}
                    className="h-8 w-auto text-xs"
                    aria-label="Choose a date"
                  />
                  <Button variant="outline" size="sm" onClick={() => setDate(todayISO())} disabled={isToday}>
                    Today
                  </Button>
                </div>
              </div>
              <WeekStrip
                date={date}
                dailyMinutes={week?.daily_minutes ?? {}}
                onSelect={setDate}
              />
              <div>
                <div className="mb-1 flex items-center justify-between text-[11px]">
                  <span className="text-muted">Daily goal</span>
                  <span className="tabular font-medium text-text">
                    {formatMinutes(plan.summary.logged_minutes)} / {formatMinutes(plan.summary.goal_minutes)}
                  </span>
                </div>
                <ProgressBar
                  value={plan.summary.goal_percentage}
                  tone={plan.summary.goal_percentage >= 100 ? 'success' : 'accent'}
                />
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Tasks"
              description="Complete a task, log the time you spent, or carry it into tomorrow."
              action={
                <Button variant="secondary" size="sm" onClick={() => setTaskModal({ open: true, task: null })}>
                  <Plus className="h-3.5 w-3.5" aria-hidden="true" /> Add
                </Button>
              }
            />
            <CardBody className="pt-1">
              {tasks.length === 0 ? (
                <EmptyState
                  icon={CalendarDays}
                  title="No tasks for this day"
                  description="Plan one concrete outcome so your session has a clear finish line."
                  action={
                    <Button size="sm" onClick={() => setTaskModal({ open: true, task: null })}>
                      <Plus className="h-3.5 w-3.5" aria-hidden="true" /> Plan a task
                    </Button>
                  }
                />
              ) : (
                <ul className="divide-y divide-line">
                  {tasks.map((task) => (
                    <li key={task.id} className="flex flex-col gap-2 py-3 sm:flex-row sm:items-start">
                      <div className="flex min-w-0 flex-1 items-start gap-2.5">
                        <Checkbox
                          checked={task.is_completed}
                          onChange={() => void toggleTask(task)}
                          aria-label={task.is_completed ? `Re-open ${task.title}` : `Complete ${task.title}`}
                          className="mt-0.5"
                        />
                        <div className="min-w-0">
                          <p
                            className={cn(
                              'text-sm leading-snug',
                              task.is_completed ? 'text-faint line-through' : 'font-medium text-text',
                            )}
                          >
                            {task.title}
                          </p>
                          {task.description ? (
                            <p className="mt-0.5 line-clamp-2 text-[11px] leading-relaxed text-muted">
                              {task.description}
                            </p>
                          ) : null}
                          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                            <Badge>{task.category}</Badge>
                            <Badge tone={priorityTone(task.priority)}>{statusLabel(task.priority)}</Badge>
                            <span className="inline-flex items-center gap-1 text-[11px] text-muted">
                              <Clock className="h-3 w-3" aria-hidden="true" />
                              {formatMinutes(task.actual_minutes)} / {formatMinutes(task.estimated_minutes)}
                            </span>
                            {task.carried_from_id ? <Badge tone="info">Carried</Badge> : null}
                          </div>
                          {task.session_note ? (
                            <p className="mt-1 rounded bg-surface-2 px-2 py-1 text-[11px] italic text-muted">
                              {task.session_note}
                            </p>
                          ) : null}
                        </div>
                      </div>
                      <div className="flex shrink-0 items-center gap-0.5 pl-6 sm:pl-0">
                        <button
                          type="button"
                          onClick={() => setLogTask(task)}
                          className="rounded-md p-1.5 text-faint transition hover:bg-surface-2 hover:text-accent"
                          aria-label={`Log time for ${task.title}`}
                          title="Log time"
                        >
                          <Play className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => setTaskModal({ open: true, task })}
                          className="rounded-md p-1.5 text-faint transition hover:bg-surface-2 hover:text-accent"
                          aria-label={`Edit ${task.title}`}
                          title="Edit task"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => void moveToTomorrow(task)}
                          className="rounded-md p-1.5 text-faint transition hover:bg-surface-2 hover:text-accent"
                          aria-label={`Carry ${task.title} to tomorrow`}
                          title="Carry to tomorrow"
                        >
                          <ArrowRight className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => setConfirm({ kind: 'task', id: task.id, title: task.title })}
                          className="rounded-md p-1.5 text-faint transition hover:bg-danger-soft hover:text-danger"
                          aria-label={`Delete ${task.title}`}
                          title="Delete task"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>

          <CalendarHeatmap
            calendar={calendarQuery.data}
            cursor={calendarCursor}
            onShiftMonth={shiftMonth}
            selectedDate={date}
            onSelectDate={setDate}
          />
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader
              title="Study sessions"
              description={`${formatMinutes(plan.summary.logged_minutes)} recorded`}
              action={
                <Button variant="secondary" size="sm" onClick={() => setSessionModalOpen(true)}>
                  <Plus className="h-3.5 w-3.5" aria-hidden="true" /> Log
                </Button>
              }
            />
            <CardBody className="pt-1">
              {plan.sessions.length === 0 ? (
                <p className="py-3 text-xs leading-relaxed text-muted">
                  No sessions recorded for this day. Log one when you finish studying, even if it
                  was only fifteen minutes.
                </p>
              ) : (
                <ul className="divide-y divide-line">
                  {plan.sessions.map((session) => (
                    <li key={session.id} className="flex items-start justify-between gap-2 py-2.5">
                      <div className="min-w-0">
                        <p className="tabular text-xs font-semibold text-text">
                          {formatMinutes(session.minutes)}
                        </p>
                        {session.note ? (
                          <p className="mt-0.5 line-clamp-2 text-[11px] leading-relaxed text-muted">{session.note}</p>
                        ) : (
                          <p className="mt-0.5 text-[11px] text-faint">Study session</p>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() =>
                          setConfirm({
                            kind: 'session',
                            id: session.id,
                            title: `${formatMinutes(session.minutes)} session`,
                          })
                        }
                        className="rounded p-1 text-faint transition hover:bg-danger-soft hover:text-danger"
                        aria-label="Delete study session"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Week summary"
              description={
                week ? `${formatDate(week.week_start, { month: 'short', day: 'numeric' })} – ${formatDate(week.week_end, { month: 'short', day: 'numeric' })}` : undefined
              }
            />
            <CardBody className="space-y-3">
              {!week ? (
                <Skeleton className="h-24 w-full" />
              ) : (
                <>
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="tabular text-2xl font-semibold text-text">{week.total_hours}h</p>
                      <p className="text-[11px] text-muted">recorded this week</p>
                    </div>
                    <div className="text-right text-[11px] text-muted">
                      <p>{week.days_achieved}/7 goal days</p>
                      <p>{week.tasks_completed} tasks completed</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="rounded-lg bg-surface-2 p-2">
                      <p className="text-faint">Daily average</p>
                      <p className="tabular font-medium text-text">{formatMinutes(week.average_minutes_per_day)}</p>
                    </div>
                    <div className="rounded-lg bg-surface-2 p-2">
                      <p className="text-faint">Daily goal</p>
                      <p className="tabular font-medium text-text">{formatMinutes(week.goal_minutes_per_day)}</p>
                    </div>
                  </div>
                  {categoryEntries.length > 0 ? (
                    <div className="space-y-2">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-faint">
                        By category
                      </p>
                      {categoryEntries.map(([category, minutes]) => (
                        <div key={category}>
                          <div className="mb-0.5 flex items-center justify-between text-[11px]">
                            <span className="truncate text-muted">{category}</span>
                            <span className="tabular text-text">{formatMinutes(minutes)}</span>
                          </div>
                          <ProgressBar value={(minutes / categoryMax) * 100} size="sm" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[11px] text-muted">Log a session to see your category split.</p>
                  )}
                </>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Streak" action={<Flame className="h-4 w-4 text-warning" aria-hidden="true" />} />
            <CardBody>
              <div className="flex items-end gap-2">
                <p className="tabular text-3xl font-semibold text-text">{streak?.current_streak ?? 0}</p>
                <p className="pb-1 text-xs text-muted">consecutive active days</p>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
                <div className="rounded-lg bg-surface-2 p-2">
                  <p className="text-faint">Longest</p>
                  <p className="tabular font-medium text-text">{streak?.longest_streak ?? 0} days</p>
                </div>
                <div className="rounded-lg bg-surface-2 p-2">
                  <p className="text-faint">Active days</p>
                  <p className="tabular font-medium text-text">{streak?.total_active_days ?? 0}</p>
                </div>
              </div>
              <p className="mt-3 text-[10px] leading-relaxed text-faint">
                {streak?.rule ??
                  'A day is active with one study session or a completed task that has logged minutes.'}
              </p>
              <Button
                variant="ghost"
                size="sm"
                className="mt-2 px-0"
                onClick={() => void Promise.all([dayQuery.refetch(), weekQuery.refetch(), streakQuery.refetch()])}
              >
                <RotateCcw className="h-3 w-3" aria-hidden="true" /> Refresh stats
              </Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Quick tips" />
            <CardBody className="space-y-2 text-[11px] leading-relaxed text-muted">
              <p className="flex items-start gap-2">
                <Circle className="mt-1 h-2 w-2 shrink-0 text-accent" aria-hidden="true" />
                Sessions are the only source of study hours — completing a task without logging
                minutes keeps your streak safe but adds no hours.
              </p>
              <p className="flex items-start gap-2">
                <Circle className="mt-1 h-2 w-2 shrink-0 text-accent" aria-hidden="true" />
                Carrying a task forward removes the original and keeps a link to its history.
              </p>
            </CardBody>
          </Card>
        </div>
      </div>

      <TaskFormModal
        open={taskModal.open}
        task={taskModal.task}
        date={date}
        onClose={() => setTaskModal({ open: false, task: null })}
      />
      <LogTimeModal task={logTask} onClose={() => setLogTask(null)} />
      <SessionModal open={sessionModalOpen} date={date} onClose={() => setSessionModalOpen(false)} />
      <ConfirmDialog
        open={Boolean(confirm)}
        onClose={() => setConfirm(null)}
        onConfirm={() => void performDelete()}
        title={confirm?.kind === 'session' ? 'Delete study session?' : 'Delete task?'}
        description={
          confirm
            ? `“${confirm.title}” will be removed permanently. Logged study time that is not linked to a task is kept separately.`
            : undefined
        }
        confirmLabel="Delete"
        loading={deleteTask.isPending || deleteSession.isPending}
      />
    </div>
  );
}
