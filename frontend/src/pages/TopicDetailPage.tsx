import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  CalendarPlus,
  Check,
  Circle,
  ExternalLink,
  ListChecks,
  NotebookPen,
  Pencil,
  Plus,
  Save,
  Sparkles,
  Star,
  Trash2,
  X,
} from 'lucide-react';
import {
  useCreateChecklist,
  useCreateNote,
  useCreateTask,
  useDeleteChecklist,
  useDeleteNote,
  useTopic,
  useTopicNavigation,
  useUpdateChecklist,
  useUpdateNote,
  useUpdateTopicProgress,
} from '@/api/hooks';
import { Badge, priorityTone, statusLabel, statusTone } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Field, Input, Select, Textarea } from '@/components/ui/Field';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Skeleton } from '@/components/ui/Skeleton';
import { Checkbox } from '@/components/ui/Toggle';
import { useToast } from '@/contexts/ToastContext';
import { errorMessage } from '@/lib/errors';
import { formatDate, formatMinutes, todayISO } from '@/lib/format';
import { usePageTitle } from '@/lib/usePageTitle';
import type { Priority, TopicStatus } from '@/types/api';

const statusOptions: Array<{ value: TopicStatus; label: string }> = [
  { value: 'not_started', label: 'Not started' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
];

export default function TopicDetailPage() {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  const { notify } = useToast();
  const topicQuery = useTopic(topicId);
  const navigationQuery = useTopicNavigation(topicId);
  const progressMutation = useUpdateTopicProgress(topicId ?? '');
  const createNote = useCreateNote(topicId ?? '');
  const updateNote = useUpdateNote(topicId ?? '');
  const deleteNote = useDeleteNote(topicId ?? '');
  const createChecklist = useCreateChecklist(topicId ?? '');
  const updateChecklist = useUpdateChecklist(topicId ?? '');
  const deleteChecklist = useDeleteChecklist(topicId ?? '');
  const createTask = useCreateTask();

  const [noteDraft, setNoteDraft] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState('');
  const [checklistDraft, setChecklistDraft] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  const topic = topicQuery.data;
  usePageTitle(topic?.title ?? 'Topic');

  const updateProgress = async (body: Parameters<typeof progressMutation.mutateAsync>[0]) => {
    setActionError(null);
    try {
      await progressMutation.mutateAsync(body);
      notify('Progress saved', 'success');
    } catch (error) {
      setActionError(errorMessage(error));
    }
  };

  const addNote = async () => {
    const content = noteDraft.trim();
    if (!content) return;
    try {
      await createNote.mutateAsync(content);
      setNoteDraft('');
      notify('Note added', 'success');
    } catch (error) {
      setActionError(errorMessage(error));
    }
  };

  const saveNote = async (id: string) => {
    const content = editDraft.trim();
    if (!content) return;
    try {
      await updateNote.mutateAsync({ id, content });
      setEditingNoteId(null);
      setEditDraft('');
      notify('Note updated', 'success');
    } catch (error) {
      setActionError(errorMessage(error));
    }
  };

  const removeNote = async (id: string) => {
    try {
      await deleteNote.mutateAsync(id);
      notify('Note deleted', 'success');
    } catch (error) {
      setActionError(errorMessage(error));
    }
  };

  const addChecklist = async () => {
    const title = checklistDraft.trim();
    if (!title) return;
    try {
      await createChecklist.mutateAsync(title);
      setChecklistDraft('');
    } catch (error) {
      setActionError(errorMessage(error));
    }
  };

  const addToToday = async () => {
    if (!topic) return;
    try {
      await createTask.mutateAsync({
        title: topic.title,
        task_date: todayISO(),
        description: topic.description,
        category: topic.category,
        estimated_minutes: Math.min(120, Math.max(15, topic.estimated_minutes)),
        priority: topic.progress.priority,
        topic_id: topic.id,
      });
      notify('Added to today’s plan', 'success');
    } catch (error) {
      notify(errorMessage(error, 'Could not add the task'), 'error');
    }
  };

  if (topicQuery.isLoading) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-3 w-40" />
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-full max-w-2xl" />
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <Skeleton className="h-56 w-full" />
            <Skeleton className="h-44 w-full" />
          </div>
          <Skeleton className="h-80 w-full" />
        </div>
      </div>
    );
  }

  if (topicQuery.isError || !topic) {
    return (
      <div className="space-y-5">
        <Button variant="ghost" size="sm" onClick={() => navigate('/roadmap')}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Back to roadmap
        </Button>
        <ErrorState
          title="Topic not found"
          description="This topic may have been removed, or the link is incorrect."
          onRetry={() => void topicQuery.refetch()}
        />
      </div>
    );
  }

  const checklistDone = topic.progress.checklist.filter((item) => item.is_done).length;
  const navigation = navigationQuery.data;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
        <Link to="/roadmap" className="inline-flex items-center gap-1 font-medium text-accent hover:text-accent-hover">
          <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" /> Roadmap
        </Link>
        <span className="text-faint">/</span>
        <span>{topic.category}</span>
        {navigation ? (
          <>
            <span className="text-faint">/</span>
            <span className="tabular">
              Topic {navigation.position} of {navigation.total}
            </span>
          </>
        ) : null}
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge tone={statusTone(topic.progress.status)}>{statusLabel(topic.progress.status)}</Badge>
            <Badge>{topic.category}</Badge>
            <Badge tone={priorityTone(topic.progress.priority)}>
              {statusLabel(topic.progress.priority)} priority
            </Badge>
            {topic.is_key_topic ? (
              <Badge tone="warning">
                <Star className="h-3 w-3 fill-warning" aria-hidden="true" /> Key topic
              </Badge>
            ) : null}
          </div>
          <h1 className="text-2xl font-semibold leading-tight tracking-tight text-text">{topic.title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted">{topic.description}</p>
          <p className="mt-2 inline-flex items-center gap-1.5 text-xs text-muted">
            <BookOpen className="h-3.5 w-3.5" aria-hidden="true" />
            Estimated {formatMinutes(topic.estimated_minutes)} · {topic.subtopics.length} subtopics
          </p>
        </div>
        <Button onClick={() => void addToToday()} loading={createTask.isPending} className="shrink-0">
          <CalendarPlus className="h-4 w-4" aria-hidden="true" />
          Add to today
        </Button>
      </div>

      {actionError ? (
        <div className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger" role="alert">
          {actionError}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardHeader title="What you will learn" description="Work through these subtopics before marking the topic complete." />
            <CardBody className="pt-3">
              {topic.subtopics.length === 0 ? (
                <p className="text-xs text-muted">No subtopics listed for this topic.</p>
              ) : (
                <ol className="grid gap-2 sm:grid-cols-2">
                  {topic.subtopics.map((subtopic, index) => (
                    <li
                      key={subtopic}
                      className="flex items-start gap-2.5 rounded-lg border border-line bg-surface-2 px-3 py-2 text-xs leading-relaxed text-text"
                    >
                      <span className="tabular mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded bg-surface text-[10px] font-semibold text-muted">
                        {index + 1}
                      </span>
                      {subtopic}
                    </li>
                  ))}
                </ol>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Notes"
              description="Write the explanations you want to remember. Notes stay private to your account."
              action={<span className="text-[11px] text-muted">{topic.progress.notes.length} notes</span>}
            />
            <CardBody className="space-y-3">
              <Textarea
                value={noteDraft}
                onChange={(event) => setNoteDraft(event.target.value)}
                placeholder="e.g. The difference between checked and unchecked exceptions…"
                aria-label="New note"
                rows={3}
              />
              <div className="flex justify-end">
                <Button
                  size="sm"
                  onClick={() => void addNote()}
                  loading={createNote.isPending}
                  disabled={!noteDraft.trim()}
                >
                  <Plus className="h-3.5 w-3.5" aria-hidden="true" /> Add note
                </Button>
              </div>

              {topic.progress.notes.length === 0 ? (
                <EmptyState
                  icon={NotebookPen}
                  title="No notes yet"
                  description="Capture one useful idea from this topic while it is fresh."
                  className="py-8"
                />
              ) : (
                <ul className="space-y-2">
                  {topic.progress.notes.map((note) => (
                    <li key={note.id} className="rounded-lg border border-line bg-surface-2 p-3">
                      {editingNoteId === note.id ? (
                        <div className="space-y-2">
                          <Textarea
                            value={editDraft}
                            onChange={(event) => setEditDraft(event.target.value)}
                            aria-label="Edit note"
                            rows={3}
                          />
                          <div className="flex justify-end gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                setEditingNoteId(null);
                                setEditDraft('');
                              }}
                            >
                              <X className="h-3.5 w-3.5" aria-hidden="true" /> Cancel
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => void saveNote(note.id)}
                              loading={updateNote.isPending}
                              disabled={!editDraft.trim()}
                            >
                              <Save className="h-3.5 w-3.5" aria-hidden="true" /> Save
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <p className="whitespace-pre-wrap text-xs leading-relaxed text-text">{note.content}</p>
                            <p className="mt-1 text-[10px] text-faint">
                              {formatDate(note.updated_at, {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </p>
                          </div>
                          <div className="flex shrink-0 items-center gap-0.5">
                            <button
                              type="button"
                              onClick={() => {
                                setEditingNoteId(note.id);
                                setEditDraft(note.content);
                              }}
                              className="rounded-md p-1.5 text-faint transition hover:bg-surface hover:text-accent"
                              aria-label="Edit note"
                            >
                              <Pencil className="h-3.5 w-3.5" />
                            </button>
                            <button
                              type="button"
                              onClick={() => void removeNote(note.id)}
                              className="rounded-md p-1.5 text-faint transition hover:bg-surface hover:text-danger"
                              aria-label="Delete note"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Recommended resources"
              description="Official documentation selected for this topic."
              action={<span className="text-[11px] text-muted">{topic.resources.length} links</span>}
            />
            <CardBody className="pt-3">
              {topic.resources.length === 0 ? (
                <p className="text-xs text-muted">
                  No curated resources yet. Add your own from the{' '}
                  <Link to="/resources" className="font-medium text-accent hover:text-accent-hover">
                    resource library
                  </Link>
                  .
                </p>
              ) : (
                <ul className="space-y-2">
                  {topic.resources.map((resource) => (
                    <li key={resource.id}>
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="group flex items-start justify-between gap-3 rounded-lg border border-line bg-surface-2 px-3 py-2.5 transition hover:border-line-strong hover:bg-surface-hover"
                      >
                        <div className="min-w-0">
                          <p className="flex items-center gap-1.5 text-xs font-medium text-text group-hover:text-accent">
                            {resource.title}
                            <ExternalLink className="h-3 w-3 text-faint" aria-hidden="true" />
                          </p>
                          <p className="mt-0.5 line-clamp-2 text-[11px] leading-relaxed text-muted">
                            {resource.description}
                          </p>
                        </div>
                        <Badge className="shrink-0">{resource.category}</Badge>
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </CardBody>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader title="Your progress" description="Changes are saved instantly and update every view." />
            <CardBody className="space-y-4">
              <div>
                <p className="mb-1.5 text-xs font-medium text-text">Status</p>
                <div className="grid grid-cols-1 gap-1.5">
                  {statusOptions.map((option) => {
                    const active = topic.progress.status === option.value;
                    return (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => void updateProgress({ status: option.value })}
                        disabled={progressMutation.isPending}
                        className={`flex items-center justify-between rounded-lg border px-3 py-2 text-xs font-medium transition ${
                          active
                            ? 'border-accent bg-accent-soft text-accent-soft-fg'
                            : 'border-line bg-surface text-muted hover:bg-surface-hover hover:text-text'
                        }`}
                      >
                        {option.label}
                        {active ? <Check className="h-3.5 w-3.5" aria-hidden="true" /> : null}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Field label="Priority" htmlFor="topic-priority">
                  <Select
                    id="topic-priority"
                    value={topic.progress.priority}
                    disabled={progressMutation.isPending}
                    onChange={(event) =>
                      void updateProgress({ priority: event.target.value as Priority })
                    }
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </Select>
                </Field>
                <div>
                  <p className="mb-1.5 text-xs font-medium text-text">Confidence</p>
                  <div className="flex items-center gap-0.5 pt-1.5" role="group" aria-label="Rate your confidence">
                    {[1, 2, 3, 4, 5].map((value) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() =>
                          void updateProgress({
                            rating: topic.progress.rating === value ? null : value,
                          })
                        }
                        className="rounded p-1 transition hover:bg-surface-hover"
                        aria-label={`Rate ${value} out of 5`}
                        aria-pressed={topic.progress.rating === value}
                      >
                        <Star
                          className={`h-4 w-4 ${
                            topic.progress.rating && value <= topic.progress.rating
                              ? 'fill-warning text-warning'
                              : 'text-faint'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {topic.progress.completed_at ? (
                <p className="rounded-lg bg-success-soft px-3 py-2 text-[11px] text-success">
                  Completed {formatDate(topic.progress.completed_at)}
                </p>
              ) : topic.progress.started_at ? (
                <p className="rounded-lg bg-accent-soft px-3 py-2 text-[11px] text-accent-soft-fg">
                  Started {formatDate(topic.progress.started_at)}
                </p>
              ) : null}

              <ProgressBar value={topic.progress.status === 'completed' ? 100 : topic.progress.status === 'in_progress' ? 50 : 0} />
            </CardBody>
          </Card>

          <Card>
            <CardHeader
              title="Checklist"
              description={`${checklistDone} of ${topic.progress.checklist.length} complete`}
            />
            <CardBody className="space-y-3">
              <ul className="space-y-2">
                {topic.progress.checklist.length === 0 ? (
                  <li className="text-xs text-muted">Add your own steps for this topic.</li>
                ) : (
                  topic.progress.checklist.map((item) => (
                    <li key={item.id} className="flex items-start gap-2">
                      <Checkbox
                        checked={item.is_done}
                        onChange={(event) =>
                          void updateChecklist.mutateAsync({
                            id: item.id,
                            body: { is_done: event.target.checked },
                          })
                        }
                        aria-label={item.title}
                        className="mt-0.5"
                      />
                      <span
                        className={`flex-1 text-xs leading-relaxed ${
                          item.is_done ? 'text-faint line-through' : 'text-text'
                        }`}
                      >
                        {item.title}
                      </span>
                      <button
                        type="button"
                        onClick={() => void deleteChecklist.mutateAsync(item.id)}
                        className="rounded p-0.5 text-faint transition hover:text-danger"
                        aria-label={`Delete ${item.title}`}
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </li>
                  ))
                )}
              </ul>
              <form
                className="flex gap-2"
                onSubmit={(event) => {
                  event.preventDefault();
                  void addChecklist();
                }}
              >
                <Input
                  value={checklistDraft}
                  onChange={(event) => setChecklistDraft(event.target.value)}
                  placeholder="Add a step…"
                  aria-label="New checklist item"
                  className="h-8 text-xs"
                />
                <Button type="submit" size="sm" variant="secondary" disabled={!checklistDraft.trim()}>
                  <Plus className="h-3.5 w-3.5" aria-hidden="true" />
                </Button>
              </form>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Keep moving" />
            <CardBody className="space-y-2">
              {navigation?.previous ? (
                <Link
                  to={`/roadmap/topics/${navigation.previous.id}`}
                  className="flex items-start gap-2 rounded-lg border border-line bg-surface-2 px-3 py-2.5 transition hover:bg-surface-hover"
                >
                  <ArrowLeft className="mt-0.5 h-3.5 w-3.5 shrink-0 text-faint" aria-hidden="true" />
                  <span className="min-w-0">
                    <span className="block text-[10px] uppercase tracking-[0.1em] text-faint">Previous</span>
                    <span className="block truncate text-xs font-medium text-text">{navigation.previous.title}</span>
                  </span>
                </Link>
              ) : null}
              {navigation?.next ? (
                <Link
                  to={`/roadmap/topics/${navigation.next.id}`}
                  className="flex items-start justify-between gap-2 rounded-lg border border-accent/25 bg-accent-soft px-3 py-2.5 transition hover:bg-accent-soft/70"
                >
                  <span className="min-w-0">
                    <span className="block text-[10px] uppercase tracking-[0.1em] text-accent-soft-fg/70">Next up</span>
                    <span className="block truncate text-xs font-medium text-text">{navigation.next.title}</span>
                  </span>
                  <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" aria-hidden="true" />
                </Link>
              ) : null}
              {!navigation?.previous && !navigation?.next ? (
                <p className="flex items-center gap-1.5 text-xs text-muted">
                  <Sparkles className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
                  This is the only topic in the roadmap.
                </p>
              ) : null}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Resources on hand" />
            <CardBody className="pt-2">
              <p className="flex items-start gap-2 text-xs leading-relaxed text-muted">
                <ListChecks className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" aria-hidden="true" />
                Work through the subtopics, write one note in your own words, then complete the
                checklist before marking this topic done.
              </p>
              <p className="mt-2 flex items-start gap-2 text-xs leading-relaxed text-muted">
                <Circle className="mt-1 h-2.5 w-2.5 shrink-0 text-faint" aria-hidden="true" />
                A topic counts once, no matter how many times you re-open and complete it.
              </p>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
