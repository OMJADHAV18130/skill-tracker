import { useEffect, useMemo, useState } from 'react';
import {
  CalendarClock,
  CheckCircle2,
  ChevronDown,
  ExternalLink,
  FolderKanban,
  Github,
  Plus,
  Search,
  Sparkles,
  Trash2,
  Pencil,
  Flag,
  ListChecks,
} from 'lucide-react';
import {
  useAddMilestone,
  useAddProjectChecklist,
  useCompleteProject,
  useCreateProject,
  useDeleteMilestone,
  useDeleteProject,
  useDeleteProjectChecklist,
  useProjectSummary,
  useProjects,
  useUpdateMilestone,
  useUpdateProject,
  useUpdateProjectChecklist,
} from '@/api/hooks';
import type { ProjectInput } from '@/api/endpoints';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { Badge, priorityTone, statusLabel, statusTone } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Field, Input, Select, Textarea } from '@/components/ui/Field';
import { Modal } from '@/components/ui/Modal';
import { PageHeader, StatCard } from '@/components/ui/PageHeader';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { CardSkeleton, Skeleton } from '@/components/ui/Skeleton';
import { Checkbox } from '@/components/ui/Toggle';
import { useToast } from '@/contexts/ToastContext';
import { errorMessage } from '@/lib/errors';
import { formatDate } from '@/lib/format';
import { usePageTitle } from '@/lib/usePageTitle';
import type { Priority, Project, ProjectStatus } from '@/types/api';

interface ProjectFormState {
  name: string;
  description: string;
  required_skills: string;
  priority: Priority;
  status: ProjectStatus;
  start_date: string;
  target_date: string;
  repo_url: string;
  demo_url: string;
  notes: string;
}

const emptyForm: ProjectFormState = {
  name: '',
  description: '',
  required_skills: '',
  priority: 'medium',
  status: 'not_started',
  start_date: '',
  target_date: '',
  repo_url: '',
  demo_url: '',
  notes: '',
};

function ProjectFormModal({
  open,
  project,
  onClose,
}: {
  open: boolean;
  project: Project | null;
  onClose: () => void;
}) {
  const createProject = useCreateProject();
  const updateProject = useUpdateProject();
  const { notify } = useToast();
  const [form, setForm] = useState<ProjectFormState>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setFormError(null);
    setForm(
      project
        ? {
            name: project.name,
            description: project.description,
            required_skills: project.required_skills.join(', '),
            priority: project.priority,
            status: project.status,
            start_date: project.start_date ?? '',
            target_date: project.target_date ?? '',
            repo_url: project.repo_url ?? '',
            demo_url: project.demo_url ?? '',
            notes: project.notes ?? '',
          }
        : emptyForm,
    );
  }, [open, project]);

  const set = <K extends keyof ProjectFormState>(key: K, value: ProjectFormState[K]) =>
    setForm((current) => ({ ...current, [key]: value }));

  const submit = async () => {
    const name = form.name.trim();
    if (!name) {
      setFormError('Give the project a name.');
      return;
    }
    for (const [label, url] of [
      ['Repository', form.repo_url],
      ['Demo', form.demo_url],
    ] as const) {
      if (url.trim() && !/^https?:\/\//i.test(url.trim())) {
        setFormError(`${label} URL must start with http:// or https://.`);
        return;
      }
    }
    const payload: ProjectInput = {
      name,
      description: form.description.trim(),
      required_skills: form.required_skills
        .split(',')
        .map((skill) => skill.trim())
        .filter(Boolean),
      priority: form.priority,
      status: form.status,
      start_date: form.start_date || null,
      target_date: form.target_date || null,
      repo_url: form.repo_url.trim() || null,
      demo_url: form.demo_url.trim() || null,
      notes: form.notes.trim() || null,
    };
    try {
      if (project) {
        await updateProject.mutateAsync({ id: project.id, body: payload });
        notify('Project updated', 'success');
      } else {
        await createProject.mutateAsync(payload);
        notify('Project created', 'success');
      }
      onClose();
    } catch (error) {
      setFormError(errorMessage(error, 'Could not save the project.'));
    }
  };

  const busy = createProject.isPending || updateProject.isPending;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={project ? 'Edit project' : 'Create a project'}
      description="Portfolio projects turn each phase into evidence you can show."
      size="lg"
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={onClose} disabled={busy}>
            Cancel
          </Button>
          <Button size="sm" onClick={() => void submit()} loading={busy}>
            {project ? 'Save changes' : 'Create project'}
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
        <Field label="Name" htmlFor="project-name">
          <Input
            id="project-name"
            value={form.name}
            onChange={(event) => set('name', event.target.value)}
            placeholder="e.g. Production-style finance API"
            maxLength={200}
            autoFocus
          />
        </Field>
        <Field label="Description" htmlFor="project-description">
          <Textarea
            id="project-description"
            value={form.description}
            onChange={(event) => set('description', event.target.value)}
            rows={3}
            placeholder="What does this project prove you can do?"
          />
        </Field>
        <Field
          label="Required skills"
          htmlFor="project-skills"
          hint="Comma separated — e.g. Spring Security, PostgreSQL, Docker"
        >
          <Input
            id="project-skills"
            value={form.required_skills}
            onChange={(event) => set('required_skills', event.target.value)}
            placeholder="Java, Spring Boot, PostgreSQL"
          />
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Priority" htmlFor="project-priority">
            <Select
              id="project-priority"
              value={form.priority}
              onChange={(event) => set('priority', event.target.value as Priority)}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </Select>
          </Field>
          <Field label="Status" htmlFor="project-status">
            <Select
              id="project-status"
              value={form.status}
              onChange={(event) => set('status', event.target.value as ProjectStatus)}
            >
              <option value="not_started">Not started</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </Select>
          </Field>
          <Field label="Start date" htmlFor="project-start">
            <Input
              id="project-start"
              type="date"
              value={form.start_date}
              onChange={(event) => set('start_date', event.target.value)}
            />
          </Field>
          <Field label="Target date" htmlFor="project-target">
            <Input
              id="project-target"
              type="date"
              value={form.target_date}
              onChange={(event) => set('target_date', event.target.value)}
            />
          </Field>
          <Field label="Repository URL" htmlFor="project-repo">
            <Input
              id="project-repo"
              type="url"
              value={form.repo_url}
              onChange={(event) => set('repo_url', event.target.value)}
              placeholder="https://github.com/…"
            />
          </Field>
          <Field label="Demo URL" htmlFor="project-demo">
            <Input
              id="project-demo"
              type="url"
              value={form.demo_url}
              onChange={(event) => set('demo_url', event.target.value)}
              placeholder="https://…"
            />
          </Field>
        </div>
        <Field label="Notes" htmlFor="project-notes" hint="Optional architecture decisions, blockers or next steps.">
          <Textarea
            id="project-notes"
            value={form.notes}
            onChange={(event) => set('notes', event.target.value)}
            rows={3}
          />
        </Field>
      </div>
    </Modal>
  );
}

function ProjectCard({
  project,
  onEdit,
  onDelete,
}: {
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
}) {
  const { notify } = useToast();
  const completeProject = useCompleteProject();
  const addMilestone = useAddMilestone();
  const updateMilestone = useUpdateMilestone();
  const deleteMilestone = useDeleteMilestone();
  const addChecklist = useAddProjectChecklist();
  const updateChecklist = useUpdateProjectChecklist();
  const deleteChecklist = useDeleteProjectChecklist();

  const [expanded, setExpanded] = useState(false);
  const [milestoneTitle, setMilestoneTitle] = useState('');
  const [milestoneDue, setMilestoneDue] = useState('');
  const [checklistTitle, setChecklistTitle] = useState('');
  const [completeOpen, setCompleteOpen] = useState(false);

  const addMilestoneSubmit = async () => {
    const title = milestoneTitle.trim();
    if (!title) return;
    try {
      await addMilestone.mutateAsync({
        projectId: project.id,
        title,
        due_date: milestoneDue || null,
      });
      setMilestoneTitle('');
      setMilestoneDue('');
      notify('Milestone added', 'success');
    } catch (error) {
      notify(errorMessage(error, 'Could not add the milestone'), 'error');
    }
  };

  const addChecklistSubmit = async () => {
    const title = checklistTitle.trim();
    if (!title) return;
    try {
      await addChecklist.mutateAsync({ projectId: project.id, title });
      setChecklistTitle('');
    } catch (error) {
      notify(errorMessage(error, 'Could not add the checklist item'), 'error');
    }
  };

  const markComplete = async () => {
    try {
      await completeProject.mutateAsync(project.id);
      notify('Project marked complete', 'success');
      setCompleteOpen(false);
    } catch (error) {
      notify(errorMessage(error, 'Could not complete the project'), 'error');
    }
  };

  const dueLabel = (() => {
    if (project.days_remaining === null) return 'No target date';
    if (project.days_remaining === 0) return 'Due today';
    if (project.days_remaining < 0) return `${Math.abs(project.days_remaining)} days overdue`;
    return `${project.days_remaining} days left`;
  })();

  return (
    <Card className="overflow-hidden">
      <CardBody className="space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5">
              <Badge tone={statusTone(project.status)}>{statusLabel(project.status)}</Badge>
              <Badge tone={priorityTone(project.priority)}>{statusLabel(project.priority)} priority</Badge>
              {project.days_remaining !== null && project.days_remaining < 0 && project.status !== 'completed' ? (
                <Badge tone="danger">Overdue</Badge>
              ) : null}
            </div>
            <h2 className="mt-1.5 text-base font-semibold leading-snug text-text">{project.name}</h2>
            <p className="mt-1 line-clamp-2 max-w-3xl text-xs leading-relaxed text-muted">{project.description}</p>
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <button
              type="button"
              onClick={() => onEdit(project)}
              className="rounded-lg p-2 text-faint transition hover:bg-surface-2 hover:text-accent"
              aria-label={`Edit ${project.name}`}
              title="Edit project"
            >
              <Pencil className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => onDelete(project)}
              className="rounded-lg p-2 text-faint transition hover:bg-danger-soft hover:text-danger"
              aria-label={`Delete ${project.name}`}
              title="Delete project"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {project.required_skills.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {project.required_skills.map((skill) => (
              <Badge key={skill}>{skill}</Badge>
            ))}
          </div>
        ) : null}

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-line bg-surface-2 p-3">
            <div className="mb-1 flex items-center justify-between text-[11px]">
              <span className="text-muted">Milestones</span>
              <span className="tabular font-medium text-text">
                {project.completed_milestones}/{project.milestone_count}
              </span>
            </div>
            <ProgressBar
              value={project.completion_percentage}
              size="sm"
              tone={project.status === 'completed' ? 'success' : 'accent'}
            />
          </div>
          <div className="rounded-lg border border-line bg-surface-2 p-3">
            <div className="mb-1 flex items-center justify-between text-[11px]">
              <span className="text-muted">Checklist</span>
              <span className="tabular font-medium text-text">
                {project.completed_checklist_items}/{project.checklist_count}
              </span>
            </div>
            <ProgressBar
              value={project.checklist_percentage}
              size="sm"
              tone={project.status === 'completed' ? 'success' : 'accent'}
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[11px] text-muted">
          <span className="inline-flex items-center gap-1">
            <CalendarClock className="h-3.5 w-3.5" aria-hidden="true" />
            {project.start_date ? formatDate(project.start_date, { month: 'short', day: 'numeric' }) : '—'} →{' '}
            {project.target_date ? formatDate(project.target_date, { month: 'short', day: 'numeric' }) : '—'}
          </span>
          <span className={project.days_remaining !== null && project.days_remaining < 0 && project.status !== 'completed' ? 'font-medium text-danger' : ''}>
            {dueLabel}
          </span>
          {project.repo_url ? (
            <a
              href={project.repo_url}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-1 font-medium text-accent transition hover:text-accent-hover"
            >
              <Github className="h-3.5 w-3.5" aria-hidden="true" /> Repository
            </a>
          ) : null}
          {project.demo_url ? (
            <a
              href={project.demo_url}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-1 font-medium text-accent transition hover:text-accent-hover"
            >
              <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" /> Live demo
            </a>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2 border-t border-line pt-3">
          <Button variant="secondary" size="sm" onClick={() => setExpanded((value) => !value)}>
            <ChevronDown
              className={`h-3.5 w-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
              aria-hidden="true"
            />
            {expanded ? 'Hide details' : 'Milestones & checklist'}
          </Button>
          {project.status !== 'completed' ? (
            <Button variant="outline" size="sm" onClick={() => setCompleteOpen(true)}>
              <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" /> Mark complete
            </Button>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-success">
              <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" /> Completed
            </span>
          )}
          {project.notes ? (
            <span className="ml-auto hidden max-w-sm truncate text-[11px] italic text-faint sm:block" title={project.notes}>
              {project.notes}
            </span>
          ) : null}
        </div>
      </CardBody>

      {expanded ? (
        <div className="animate-in grid gap-5 border-t border-line bg-surface-2/40 p-4 sm:p-5 md:grid-cols-2">
          <section>
            <h3 className="flex items-center gap-1.5 text-xs font-semibold text-text">
              <Flag className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
              Milestones
            </h3>
            <ul className="mt-2 space-y-2">
              {project.milestones.length === 0 ? (
                <li className="text-[11px] text-muted">Break the project into three or four milestones.</li>
              ) : (
                project.milestones.map((milestone) => (
                  <li key={milestone.id} className="flex items-start gap-2 rounded-lg border border-line bg-surface p-2.5">
                    <Checkbox
                      checked={milestone.is_completed}
                      onChange={(event) =>
                        void updateMilestone.mutateAsync({
                          id: milestone.id,
                          body: { is_completed: event.target.checked },
                        })
                      }
                      aria-label={milestone.title}
                      className="mt-0.5"
                    />
                    <div className="min-w-0 flex-1">
                      <p
                        className={`text-xs leading-relaxed ${
                          milestone.is_completed ? 'text-faint line-through' : 'text-text'
                        }`}
                      >
                        {milestone.title}
                      </p>
                      {milestone.due_date ? (
                        <p className="mt-0.5 text-[10px] text-faint">
                          Due {formatDate(milestone.due_date, { month: 'short', day: 'numeric' })}
                        </p>
                      ) : null}
                    </div>
                    <button
                      type="button"
                      onClick={() => void deleteMilestone.mutateAsync(milestone.id)}
                      className="rounded p-0.5 text-faint transition hover:text-danger"
                      aria-label={`Delete milestone ${milestone.title}`}
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </li>
                ))
              )}
            </ul>
            <form
              className="mt-2 flex flex-wrap gap-1.5"
              onSubmit={(event) => {
                event.preventDefault();
                void addMilestoneSubmit();
              }}
            >
              <Input
                value={milestoneTitle}
                onChange={(event) => setMilestoneTitle(event.target.value)}
                placeholder="New milestone…"
                aria-label="New milestone title"
                className="h-8 min-w-0 flex-1 text-xs"
              />
              <Input
                type="date"
                value={milestoneDue}
                onChange={(event) => setMilestoneDue(event.target.value)}
                aria-label="Milestone due date"
                className="h-8 w-36 text-xs"
              />
              <Button type="submit" size="sm" variant="secondary" disabled={!milestoneTitle.trim()}>
                <Plus className="h-3.5 w-3.5" aria-hidden="true" />
              </Button>
            </form>
          </section>

          <section>
            <h3 className="flex items-center gap-1.5 text-xs font-semibold text-text">
              <ListChecks className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
              Checklist
            </h3>
            <ul className="mt-2 space-y-2">
              {project.checklist_items.length === 0 ? (
                <li className="text-[11px] text-muted">Track the concrete deliverables for this project.</li>
              ) : (
                project.checklist_items.map((item) => (
                  <li key={item.id} className="flex items-start gap-2 rounded-lg border border-line bg-surface p-2.5">
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
                      aria-label={`Delete checklist item ${item.title}`}
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </li>
                ))
              )}
            </ul>
            <form
              className="mt-2 flex gap-1.5"
              onSubmit={(event) => {
                event.preventDefault();
                void addChecklistSubmit();
              }}
            >
              <Input
                value={checklistTitle}
                onChange={(event) => setChecklistTitle(event.target.value)}
                placeholder="New checklist item…"
                aria-label="New checklist item"
                className="h-8 flex-1 text-xs"
              />
              <Button type="submit" size="sm" variant="secondary" disabled={!checklistTitle.trim()}>
                <Plus className="h-3.5 w-3.5" aria-hidden="true" />
              </Button>
            </form>
          </section>
        </div>
      ) : null}

      <ConfirmDialog
        open={completeOpen}
        onClose={() => setCompleteOpen(false)}
        onConfirm={() => void markComplete()}
        title="Mark project complete?"
        description="Every milestone will be marked complete and the project will move to your completed portfolio."
        confirmLabel="Mark complete"
        tone="primary"
        loading={completeProject.isPending}
      />
    </Card>
  );
}

export default function ProjectsPage() {
  usePageTitle('Projects');
  const projectsQuery = useProjects();
  const summaryQuery = useProjectSummary();
  const deleteProject = useDeleteProject();
  const { notify } = useToast();

  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<'all' | ProjectStatus>('all');
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

  const projects = projectsQuery.data ?? [];
  const visible = useMemo(() => {
    const query = search.trim().toLowerCase();
    return projects.filter((project) => {
      const matchesStatus = status === 'all' || project.status === status;
      const matchesSearch =
        !query ||
        [project.name, project.description, ...project.required_skills].some((value) =>
          value.toLowerCase().includes(query),
        );
      return matchesStatus && matchesSearch;
    });
  }, [projects, search, status]);

  const summary = summaryQuery.data;

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteProject.mutateAsync(deleteTarget.id);
      notify('Project deleted', 'success');
      setDeleteTarget(null);
    } catch (error) {
      notify(errorMessage(error, 'Could not delete the project'), 'error');
    }
  };

  if (projectsQuery.isLoading) {
    return (
      <div className="space-y-5">
        <div>
          <Skeleton className="h-3 w-24" />
          <Skeleton className="mt-2 h-7 w-56" />
        </div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <CardSkeleton key={index} />
          ))}
        </div>
        <Skeleton className="h-52 w-full" />
        <Skeleton className="h-52 w-full" />
      </div>
    );
  }

  if (projectsQuery.isError) {
    return (
      <div className="space-y-5">
        <PageHeader title="Projects" description="Turn every phase into a portfolio artefact." />
        <ErrorState onRetry={() => void projectsQuery.refetch()} />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Portfolio"
        title="Project tracker"
        description="Six projects map directly to the roadmap phases. Track milestones and deliverables so each phase ends with something real."
        actions={
          <Button
            onClick={() => {
              setEditing(null);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            New project
          </Button>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Total projects"
          value={summary?.total ?? projects.length}
          hint="Including archived"
          icon={<FolderKanban className="h-4 w-4" aria-hidden="true" />}
        />
        <StatCard
          label="In progress"
          value={summary?.in_progress ?? projects.filter((p) => p.status === 'in_progress').length}
          hint="Currently building"
          icon={<Sparkles className="h-4 w-4" aria-hidden="true" />}
          tone="accent"
        />
        <StatCard
          label="Completed"
          value={summary?.completed ?? projects.filter((p) => p.status === 'completed').length}
          hint={`${summary?.not_started ?? 0} not started`}
          icon={<CheckCircle2 className="h-4 w-4" aria-hidden="true" />}
          tone="success"
        />
        <StatCard
          label="Average completion"
          value={`${Math.round(summary?.average_completion ?? 0)}%`}
          hint="Across all milestones"
          icon={<Flag className="h-4 w-4" aria-hidden="true" />}
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
              placeholder="Search projects or skills…"
              aria-label="Search projects"
              className="pl-9"
            />
          </div>
          <Select
            value={status}
            onChange={(event) => setStatus(event.target.value as 'all' | ProjectStatus)}
            aria-label="Filter projects by status"
            className="sm:w-44"
          >
            <option value="all">All statuses</option>
            <option value="not_started">Not started</option>
            <option value="in_progress">In progress</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </Select>
        </CardBody>
      </Card>

      {visible.length === 0 ? (
        <Card>
          <EmptyState
            icon={FolderKanban}
            title={projects.length === 0 ? 'No projects yet' : 'No projects match those filters'}
            description={
              projects.length === 0
                ? 'Create your first project or reset the default portfolio from Settings.'
                : 'Try a different search term or status.'
            }
            action={
              projects.length === 0 ? (
                <Button
                  size="sm"
                  onClick={() => {
                    setEditing(null);
                    setFormOpen(true);
                  }}
                >
                  <Plus className="h-3.5 w-3.5" aria-hidden="true" /> Create project
                </Button>
              ) : (
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
              )
            }
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {visible.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onEdit={(target) => {
                setEditing(target);
                setFormOpen(true);
              }}
              onDelete={setDeleteTarget}
            />
          ))}
        </div>
      )}

      <ProjectFormModal
        open={formOpen}
        project={editing}
        onClose={() => {
          setFormOpen(false);
          setEditing(null);
        }}
      />
      <ConfirmDialog
        open={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => void confirmDelete()}
        title="Delete project?"
        description={
          deleteTarget
            ? `“${deleteTarget.name}”, its milestones and checklist will be removed permanently.`
            : undefined
        }
        confirmLabel="Delete project"
        loading={deleteProject.isPending}
      />
    </div>
  );
}
