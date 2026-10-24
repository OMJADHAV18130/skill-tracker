import { useEffect, useMemo, useState } from 'react';
import {
  BadgeCheck,
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  Library,
  Link2,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  Trash2,
} from 'lucide-react';
import {
  useCreateResource,
  useDeleteResource,
  useBookmarkResource,
  useLinkResource,
  usePhases,
  useResources,
  useUpdateResource,
} from '@/api/hooks';
import type { ResourceInput } from '@/api/endpoints';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Field, Input, Select, Textarea } from '@/components/ui/Field';
import { Modal } from '@/components/ui/Modal';
import { PageHeader } from '@/components/ui/PageHeader';
import { CardSkeleton, Skeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/contexts/ToastContext';
import { cn } from '@/lib/cn';
import { RESOURCE_CATEGORIES } from '@/lib/constants';
import { errorMessage, fieldErrors } from '@/lib/errors';
import { usePageTitle } from '@/lib/usePageTitle';
import type { Resource } from '@/types/api';

interface ResourceFormState {
  title: string;
  url: string;
  description: string;
  category: string;
  tags: string;
  linked_topic_id: string;
}

const emptyForm: ResourceFormState = {
  title: '',
  url: '',
  description: '',
  category: 'Java',
  tags: '',
  linked_topic_id: '',
};

function ResourceFormModal({
  open,
  onClose,
  resource,
}: {
  open: boolean;
  onClose: () => void;
  resource: Resource | null;
}) {
  const createResource = useCreateResource();
  const updateResource = useUpdateResource();
  const linkResource = useLinkResource();
  const phases = usePhases();
  const { notify } = useToast();
  const [form, setForm] = useState<ResourceFormState>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!open) return;
    setFormError(null);
    setErrors({});
    setForm(
      resource
        ? {
            title: resource.title,
            url: resource.url,
            description: resource.description,
            category: resource.category,
            tags: resource.tags.join(', '),
            linked_topic_id: resource.linked_topic_id ?? '',
          }
        : emptyForm,
    );
  }, [open, resource]);

  const set = <K extends keyof ResourceFormState>(key: K, value: ResourceFormState[K]) =>
    setForm((current) => ({ ...current, [key]: value }));

  const categories = useMemo(() => {
    const values = new Set(RESOURCE_CATEGORIES);
    if (resource?.category) values.add(resource.category);
    return Array.from(values).sort();
  }, [resource?.category]);

  const submitting = createResource.isPending || updateResource.isPending || linkResource.isPending;

  const submit = async () => {
    const title = form.title.trim();
    const url = form.url.trim();
    const category = form.category.trim();

    if (!title) {
      setFormError('Give the resource a title.');
      return;
    }
    if (!/^https?:\/\/.+/i.test(url)) {
      setFormError('The URL must start with http:// or https://.');
      return;
    }
    if (!category) {
      setFormError('Choose a category for this resource.');
      return;
    }

    setFormError(null);
    setErrors({});
    const tags = form.tags
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean);

    const payload: ResourceInput = {
      title,
      url,
      description: form.description.trim(),
      category,
      tags,
      linked_topic_id: form.linked_topic_id || null,
    };

    try {
      if (resource) {
        const previousTopic = resource.linked_topic_id ?? null;
        const nextTopic = payload.linked_topic_id ?? null;
        await updateResource.mutateAsync({
          id: resource.id,
          body: { ...payload, linked_topic_id: nextTopic ?? undefined },
        });
        if (previousTopic !== nextTopic) {
          await linkResource.mutateAsync({ id: resource.id, topicId: nextTopic });
        }
        notify('Resource updated', 'success');
      } else {
        await createResource.mutateAsync(payload);
        notify('Resource added to your library', 'success');
      }
      onClose();
    } catch (error) {
      setErrors(fieldErrors(error));
      setFormError(errorMessage(error, 'Could not save this resource.'));
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={resource ? 'Edit resource' : 'Add a resource'}
      description={
        resource
          ? 'Update your custom resource and its roadmap link.'
          : 'Save a link that you want to revisit during the roadmap.'
      }
      footer={
        <>
          <Button type="button" variant="secondary" size="sm" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="button" size="sm" loading={submitting} onClick={() => void submit()}>
            {resource ? 'Save changes' : 'Add resource'}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {formError ? (
          <div
            className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger"
            role="alert"
          >
            {formError}
          </div>
        ) : null}

        <Field label="Title" htmlFor="resource-title" error={errors.title}>
          <Input
            id="resource-title"
            value={form.title}
            onChange={(event) => set('title', event.target.value)}
            placeholder="e.g. Spring Boot reference documentation"
            invalid={Boolean(errors.title)}
            autoFocus
          />
        </Field>

        <Field
          label="URL"
          htmlFor="resource-url"
          error={errors.url}
          hint="Only http and https links are accepted."
        >
          <Input
            id="resource-url"
            type="url"
            value={form.url}
            onChange={(event) => set('url', event.target.value)}
            placeholder="https://docs.spring.io/spring-boot/"
            invalid={Boolean(errors.url)}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Category" htmlFor="resource-category" error={errors.category}>
            <Select
              id="resource-category"
              value={form.category}
              onChange={(event) => set('category', event.target.value)}
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </Select>
          </Field>

          <Field label="Tags" htmlFor="resource-tags" hint="Comma separated">
            <Input
              id="resource-tags"
              value={form.tags}
              onChange={(event) => set('tags', event.target.value)}
              placeholder="reference, guide"
            />
          </Field>
        </div>

        <Field label="Linked topic" htmlFor="resource-topic" hint="Optional">
          <Select
            id="resource-topic"
            value={form.linked_topic_id}
            onChange={(event) => set('linked_topic_id', event.target.value)}
          >
            <option value="">No linked topic</option>
            {phases.data?.items.map((phase) => (
              <optgroup key={phase.id} label={`${phase.month_label} — ${phase.title}`}>
                {phase.topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.title}
                  </option>
                ))}
              </optgroup>
            ))}
          </Select>
        </Field>

        <Field label="Why this resource?" htmlFor="resource-description">
          <Textarea
            id="resource-description"
            value={form.description}
            onChange={(event) => set('description', event.target.value)}
            placeholder="A short note about when you want to use it."
            rows={3}
          />
        </Field>
      </div>
    </Modal>
  );
}

function ResourceCard({
  resource,
  onEdit,
  onDelete,
}: {
  resource: Resource;
  onEdit: (resource: Resource) => void;
  onDelete: (resource: Resource) => void;
}) {
  const bookmark = useBookmarkResource();
  const { notify } = useToast();

  const toggleBookmark = async () => {
    try {
      await bookmark.mutateAsync({ id: resource.id, bookmarked: !resource.is_bookmarked });
      notify(resource.is_bookmarked ? 'Bookmark removed' : 'Resource bookmarked', 'success');
    } catch {
      notify('Could not update the bookmark', 'error');
    }
  };

  return (
    <article className="group flex h-full flex-col rounded-card border border-line bg-surface p-4 shadow-card transition hover:border-line-strong">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <Badge tone="accent">{resource.category}</Badge>
          {resource.is_official ? (
            <Badge tone="success">
              <BadgeCheck className="h-3 w-3" aria-hidden="true" />
              Official
            </Badge>
          ) : (
            <Badge>Custom</Badge>
          )}
        </div>
        <button
          type="button"
          onClick={() => void toggleBookmark()}
          disabled={bookmark.isPending}
          className={cn(
            'rounded-lg p-1.5 transition disabled:opacity-50',
            resource.is_bookmarked
              ? 'text-accent hover:bg-accent-soft'
              : 'text-faint hover:bg-surface-hover hover:text-text',
          )}
          aria-label={
            resource.is_bookmarked
              ? `Remove bookmark from ${resource.title}`
              : `Bookmark ${resource.title}`
          }
          aria-pressed={resource.is_bookmarked}
        >
          {resource.is_bookmarked ? (
            <BookmarkCheck className="h-4 w-4" />
          ) : (
            <Bookmark className="h-4 w-4" />
          )}
        </button>
      </div>

      <a
        href={resource.url}
        target="_blank"
        rel="noreferrer noopener"
        className="mt-3 flex items-start gap-1.5 text-sm font-semibold leading-snug text-text transition hover:text-accent"
      >
        <span className="line-clamp-2">{resource.title}</span>
        <ExternalLink className="mt-0.5 h-3.5 w-3.5 shrink-0 text-faint" aria-hidden="true" />
      </a>

      {resource.description ? (
        <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-muted">
          {resource.description}
        </p>
      ) : null}

      {resource.tags.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-1">
          {resource.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-md bg-surface-2 px-1.5 py-0.5 text-[10px] font-medium text-muted"
            >
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      {resource.linked_topic_title ? (
        <p className="mt-3 inline-flex items-center gap-1 text-[11px] text-muted">
          <Link2 className="h-3 w-3 text-faint" aria-hidden="true" />
          <span className="truncate">{resource.linked_topic_title}</span>
        </p>
      ) : null}

      <div className="mt-auto flex items-center justify-between gap-2 border-t border-line pt-3">
        <a
          href={resource.url}
          target="_blank"
          rel="noreferrer noopener"
          className="inline-flex items-center gap-1 text-xs font-medium text-accent transition hover:text-accent-hover"
        >
          Open resource
          <ExternalLink className="h-3 w-3" aria-hidden="true" />
        </a>
        {resource.is_official ? (
          <span className="inline-flex items-center gap-1 text-[10px] text-faint" title="Official resources are read-only">
            <ShieldCheck className="h-3 w-3" aria-hidden="true" />
            Read-only
          </span>
        ) : (
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onEdit(resource)}
              className="rounded-lg p-1.5 text-muted transition hover:bg-surface-hover hover:text-text"
              aria-label={`Edit ${resource.title}`}
            >
              <Pencil className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onDelete(resource)}
              className="rounded-lg p-1.5 text-muted transition hover:bg-danger-soft hover:text-danger"
              aria-label={`Delete ${resource.title}`}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>
    </article>
  );
}

function ResourcesSkeleton() {
  return (
    <div className="space-y-5">
      <div>
        <Skeleton className="h-3 w-24" />
        <Skeleton className="mt-2 h-7 w-56" />
        <Skeleton className="mt-2 h-4 w-96 max-w-full" />
      </div>
      <Skeleton className="h-[72px] w-full" />
      <div className="grid gap-4 md:grid-cols-2">
        {Array.from({ length: 6 }).map((_, index) => (
          <CardSkeleton key={index} />
        ))}
      </div>
    </div>
  );
}

export default function ResourcesPage() {
  usePageTitle('Resources');

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Resource | null>(null);
  const [deleting, setDeleting] = useState<Resource | null>(null);

  const deleteResource = useDeleteResource();
  const { notify } = useToast();

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedSearch(search.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [search]);

  const filters = useMemo(
    () => ({
      q: debouncedSearch || undefined,
      category: category === 'All' ? undefined : category,
      bookmarked: bookmarkedOnly || undefined,
    }),
    [debouncedSearch, category, bookmarkedOnly],
  );

  const resources = useResources(filters);

  const categories = useMemo(() => {
    const values = new Set(RESOURCE_CATEGORIES);
    for (const item of resources.data?.items ?? []) values.add(item.category);
    return ['All', ...Array.from(values).sort()];
  }, [resources.data?.items]);

  const openCreate = () => {
    setEditing(null);
    setFormOpen(true);
  };

  const openEdit = (resource: Resource) => {
    setEditing(resource);
    setFormOpen(true);
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    try {
      await deleteResource.mutateAsync(deleting.id);
      notify('Resource deleted', 'success');
      setDeleting(null);
    } catch (error) {
      notify(errorMessage(error, 'Could not delete this resource'), 'error');
    }
  };

  if (resources.isLoading) return <ResourcesSkeleton />;
  if (resources.isError) {
    return (
      <div className="space-y-5">
        <PageHeader title="Resources" description="Verified documentation and your own bookmarks." />
        <ErrorState
          title="Could not load the resource library"
          description={errorMessage(resources.error)}
          onRetry={() => void resources.refetch()}
        />
      </div>
    );
  }

  const data = resources.data;
  const items = data?.items ?? [];
  const officialCount = items.filter((item) => item.is_official).length;
  const customCount = items.length - officialCount;

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Library"
        title="Resources"
        description="Official documentation for every phase, plus a private shelf for the links you discover."
        actions={
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            Add resource
          </Button>
        }
      />

      <Card>
        <CardBody className="space-y-3">
          <div className="flex flex-col gap-3 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
                aria-hidden="true"
              />
              <Input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search titles, tags and descriptions…"
                className="pl-9"
                aria-label="Search resources"
              />
            </div>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Select
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                className="sm:w-48"
                aria-label="Filter by category"
              >
                {categories.map((option) => (
                  <option key={option} value={option}>
                    {option === 'All' ? 'All categories' : option}
                  </option>
                ))}
              </Select>
              <Button
                type="button"
                variant={bookmarkedOnly ? 'primary' : 'secondary'}
                onClick={() => setBookmarkedOnly((value) => !value)}
                aria-pressed={bookmarkedOnly}
              >
                <Bookmark className="h-4 w-4" aria-hidden="true" />
                Bookmarked
                {data?.bookmarked_count ? (
                  <span className="tabular rounded-full bg-black/10 px-1.5 text-[10px] dark:bg-white/10">
                    {data.bookmarked_count}
                  </span>
                ) : null}
              </Button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted">
            <span>{data?.total ?? 0} shown</span>
            <span className="inline-flex items-center gap-1">
              <BadgeCheck className="h-3 w-3 text-success" aria-hidden="true" />
              {officialCount} official
            </span>
            <span>{customCount} custom</span>
            {debouncedSearch ? <span>Matching “{debouncedSearch}”</span> : null}
          </div>
        </CardBody>
      </Card>

      {items.length === 0 ? (
        <EmptyState
          icon={bookmarkedOnly ? Bookmark : Library}
          title={bookmarkedOnly ? 'No bookmarks yet' : 'No resources match your filters'}
          description={
            bookmarkedOnly
              ? 'Bookmark a resource and it will appear here for quick access.'
              : 'Try a different search term or category, or add your own resource.'
          }
          action={
            bookmarkedOnly ? (
              <Button variant="secondary" size="sm" onClick={() => setBookmarkedOnly(false)}>
                Show all resources
              </Button>
            ) : (
              <Button size="sm" onClick={openCreate}>
                <Plus className="h-3.5 w-3.5" aria-hidden="true" />
                Add resource
              </Button>
            )
          }
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              onEdit={openEdit}
              onDelete={setDeleting}
            />
          ))}
        </div>
      )}

      <ResourceFormModal open={formOpen} onClose={() => setFormOpen(false)} resource={editing} />

      <ConfirmDialog
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={() => void confirmDelete()}
        title="Delete this resource?"
        description={
          deleting
            ? `“${deleting.title}” will be removed from your library. Official resources cannot be deleted.`
            : undefined
        }
        confirmLabel="Delete resource"
        loading={deleteResource.isPending}
      />
    </div>
  );
}
