import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Download,
  FileJson,
  KeyRound,
  Monitor,
  Moon,
  RefreshCcw,
  Save,
  Sun,
  Upload,
  UserRound,
} from 'lucide-react';
import { profileApi, settingsApi, type PreferenceInput, type ProfileInput } from '@/api/endpoints';
import {
  usePreferences,
  useUpdatePreferences,
} from '@/api/hooks';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { ErrorState } from '@/components/ui/EmptyState';
import { Field, Input, Select } from '@/components/ui/Field';
import { PageHeader } from '@/components/ui/PageHeader';
import { Skeleton } from '@/components/ui/Skeleton';
import { Toggle } from '@/components/ui/Toggle';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useToast } from '@/contexts/ToastContext';
import { cn } from '@/lib/cn';
import { errorMessage, fieldErrors } from '@/lib/errors';
import { formatDate } from '@/lib/format';
import { usePageTitle } from '@/lib/usePageTitle';
import type { ImportPreview, Theme } from '@/types/api';

interface ProfileState {
  full_name: string;
  username: string;
  email: string;
}

interface PasswordState {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface PreferenceState {
  daily_goal_minutes: string;
  roadmap_start_date: string;
  theme: Theme;
  reminders_enabled: boolean;
  reminder_time: string;
  timezone: string;
}

const THEME_OPTIONS: Array<{ value: Theme; label: string; icon: typeof Sun }> = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
];

function SectionCard({
  icon,
  title,
  description,
  children,
  className,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent-soft text-accent">
              {icon}
            </span>
            {title}
          </span>
        }
        description={description}
      />
      <CardBody className="pt-4">{children}</CardBody>
    </Card>
  );
}

function ProfileSection() {
  const { user, updateUser } = useAuth();
  const { notify } = useToast();
  const [form, setForm] = useState<ProfileState>({ full_name: '', username: '', email: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!user) return;
    setForm({
      full_name: user.full_name ?? '',
      username: user.username,
      email: user.email,
    });
  }, [user]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setErrors({});
    setFormError(null);

    const email = form.email.trim();
    const username = form.username.trim();
    if (!email.includes('@')) {
      setErrors({ email: 'Enter a valid email address.' });
      return;
    }
    if (username.length < 3) {
      setErrors({ username: 'Username must be at least 3 characters.' });
      return;
    }

    const payload: ProfileInput = {
      full_name: form.full_name.trim() || null,
      username,
      email,
    };

    setSaving(true);
    try {
      await updateUser(payload);
      notify('Profile updated', 'success');
    } catch (error) {
      setErrors(fieldErrors(error));
      setFormError(errorMessage(error, 'Could not update your profile.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <SectionCard
      icon={<UserRound className="h-4 w-4" aria-hidden="true" />}
      title="Profile"
      description="The name and contact details attached to your learning progress."
    >
      <form className="space-y-4" onSubmit={(event) => void submit(event)}>
        {formError ? (
          <div
            className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger"
            role="alert"
          >
            {formError}
          </div>
        ) : null}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Full name" htmlFor="profile-name" error={errors.full_name}>
            <Input
              id="profile-name"
              value={form.full_name}
              onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
              placeholder="Your name"
              autoComplete="name"
            />
          </Field>
          <Field label="Username" htmlFor="profile-username" error={errors.username}>
            <Input
              id="profile-username"
              value={form.username}
              onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))}
              placeholder="your.handle"
              autoComplete="username"
              invalid={Boolean(errors.username)}
            />
          </Field>
        </div>

        <Field label="Email" htmlFor="profile-email" error={errors.email}>
          <Input
            id="profile-email"
            type="email"
            value={form.email}
            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            placeholder="you@example.com"
            autoComplete="email"
            invalid={Boolean(errors.email)}
          />
        </Field>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
          <p className="text-[11px] text-muted">
            {user ? `Member since ${formatDate(user.created_at)}` : null}
          </p>
          <Button type="submit" size="sm" loading={saving}>
            <Save className="h-3.5 w-3.5" aria-hidden="true" />
            Save profile
          </Button>
        </div>
      </form>
    </SectionCard>
  );
}

function PasswordSection() {
  const { logout } = useAuth();
  const { notify } = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState<PasswordState>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setErrors({});
    setFormError(null);

    if (!form.current_password) {
      setErrors({ current_password: 'Enter your current password.' });
      return;
    }
    if (form.new_password.length < 8) {
      setErrors({ new_password: 'Use at least 8 characters.' });
      return;
    }
    if (form.new_password !== form.confirm_password) {
      setErrors({ confirm_password: 'The new passwords do not match.' });
      return;
    }

    setSaving(true);
    try {
      await profileApi.changePassword(form.current_password, form.new_password);
      notify('Password updated. Please sign in again.', 'success');
      await logout();
      navigate('/login', { replace: true });
    } catch (error) {
      setErrors(fieldErrors(error));
      setFormError(errorMessage(error, 'Could not change your password.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <SectionCard
      icon={<KeyRound className="h-4 w-4" aria-hidden="true" />}
      title="Password"
      description="Changing your password signs out every active session."
    >
      <form className="space-y-4" onSubmit={(event) => void submit(event)}>
        {formError ? (
          <div
            className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger"
            role="alert"
          >
            {formError}
          </div>
        ) : null}

        <Field label="Current password" htmlFor="current-password" error={errors.current_password}>
          <Input
            id="current-password"
            type="password"
            value={form.current_password}
            onChange={(event) =>
              setForm((current) => ({ ...current, current_password: event.target.value }))
            }
            autoComplete="current-password"
            invalid={Boolean(errors.current_password)}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="New password"
            htmlFor="new-password"
            error={errors.new_password}
            hint="At least 8 characters."
          >
            <Input
              id="new-password"
              type="password"
              value={form.new_password}
              onChange={(event) =>
                setForm((current) => ({ ...current, new_password: event.target.value }))
              }
              autoComplete="new-password"
              invalid={Boolean(errors.new_password)}
            />
          </Field>
          <Field label="Confirm new password" htmlFor="confirm-password" error={errors.confirm_password}>
            <Input
              id="confirm-password"
              type="password"
              value={form.confirm_password}
              onChange={(event) =>
                setForm((current) => ({ ...current, confirm_password: event.target.value }))
              }
              autoComplete="new-password"
              invalid={Boolean(errors.confirm_password)}
            />
          </Field>
        </div>

        <div className="flex justify-end border-t border-line pt-4">
          <Button type="submit" size="sm" variant="secondary" loading={saving}>
            Update password
          </Button>
        </div>
      </form>
    </SectionCard>
  );
}

function PreferencesSection() {
  const preferences = usePreferences();
  const updatePreferences = useUpdatePreferences();
  const { setTheme } = useTheme();
  const { notify } = useToast();
  const [form, setForm] = useState<PreferenceState | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!preferences.data) return;
    setForm({
      daily_goal_minutes: String(preferences.data.daily_goal_minutes),
      roadmap_start_date: preferences.data.roadmap_start_date,
      theme: preferences.data.theme,
      reminders_enabled: preferences.data.reminders_enabled,
      reminder_time: preferences.data.reminder_time.slice(0, 5),
      timezone: preferences.data.timezone,
    });
    setTheme(preferences.data.theme);
  }, [preferences.data, setTheme]);

  if (preferences.isLoading) {
    return (
      <SectionCard
        icon={<Sun className="h-4 w-4" aria-hidden="true" />}
        title="Study preferences"
        description="Daily goal, roadmap start and appearance."
      >
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-2/3" />
        </div>
      </SectionCard>
    );
  }

  if (preferences.isError || !form) {
    return (
      <ErrorState
        title="Could not load your preferences"
        description={errorMessage(preferences.error)}
        onRetry={() => void preferences.refetch()}
      />
    );
  }

  const save = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);

    const goal = Number(form.daily_goal_minutes);
    if (!Number.isInteger(goal) || goal < 30 || goal > 480) {
      setFormError('Daily goal must be a whole number between 30 and 480 minutes.');
      return;
    }
    if (!form.roadmap_start_date) {
      setFormError('Choose the date your roadmap begins.');
      return;
    }
    if (!form.reminder_time) {
      setFormError('Choose a reminder time.');
      return;
    }

    const payload: PreferenceInput = {
      daily_goal_minutes: goal,
      roadmap_start_date: form.roadmap_start_date,
      theme: form.theme,
      reminders_enabled: form.reminders_enabled,
      reminder_time: form.reminder_time,
      timezone: form.timezone.trim() || 'UTC',
    };

    try {
      await updatePreferences.mutateAsync(payload);
      setTheme(form.theme);
      notify('Preferences saved', 'success');
    } catch (error) {
      setFormError(errorMessage(error, 'Could not save your preferences.'));
    }
  };

  return (
    <SectionCard
      icon={<Sun className="h-4 w-4" aria-hidden="true" />}
      title="Study preferences"
      description="Tune the daily goal, roadmap start and appearance."
    >
      <form className="space-y-5" onSubmit={(event) => void save(event)}>
        {formError ? (
          <div
            className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger"
            role="alert"
          >
            {formError}
          </div>
        ) : null}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Daily study goal"
            htmlFor="daily-goal"
            hint="Between 30 and 480 minutes."
          >
            <div className="relative">
              <Input
                id="daily-goal"
                type="number"
                min={30}
                max={480}
                step={15}
                value={form.daily_goal_minutes}
                onChange={(event) =>
                  setForm((current) =>
                    current ? { ...current, daily_goal_minutes: event.target.value } : current,
                  )
                }
                className="pr-16"
              />
              <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-faint">
                minutes
              </span>
            </div>
          </Field>

          <Field label="Roadmap starts on" htmlFor="roadmap-start">
            <Input
              id="roadmap-start"
              type="date"
              value={form.roadmap_start_date}
              onChange={(event) =>
                setForm((current) =>
                  current ? { ...current, roadmap_start_date: event.target.value } : current,
                )
              }
            />
          </Field>
        </div>

        <Field label="Appearance" htmlFor="theme">
          <div className="grid grid-cols-3 gap-2">
            {THEME_OPTIONS.map((option) => {
              const Icon = option.icon;
              const active = form.theme === option.value;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() =>
                    setForm((current) => (current ? { ...current, theme: option.value } : current))
                  }
                  className={cn(
                    'flex flex-col items-center gap-1.5 rounded-lg border px-2 py-3 text-xs font-medium transition',
                    active
                      ? 'border-accent bg-accent-soft text-accent-soft-fg'
                      : 'border-line bg-surface text-muted hover:bg-surface-hover',
                  )}
                  aria-pressed={active}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {option.label}
                </button>
              );
            })}
          </div>
        </Field>

        <div className="space-y-4 rounded-lg border border-line bg-surface-2 p-3.5">
          <Toggle
            checked={form.reminders_enabled}
            onChange={(value) =>
              setForm((current) => (current ? { ...current, reminders_enabled: value } : current))
            }
            label="Daily study reminder"
            description="Show a nudge at your chosen time."
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Reminder time" htmlFor="reminder-time">
              <Input
                id="reminder-time"
                type="time"
                value={form.reminder_time}
                disabled={!form.reminders_enabled}
                onChange={(event) =>
                  setForm((current) =>
                    current ? { ...current, reminder_time: event.target.value } : current,
                  )
                }
              />
            </Field>
            <Field label="Timezone" htmlFor="timezone" hint="IANA name, e.g. Europe/Berlin">
              <Input
                id="timezone"
                value={form.timezone}
                onChange={(event) =>
                  setForm((current) =>
                    current ? { ...current, timezone: event.target.value } : current,
                  )
                }
                placeholder="UTC"
              />
            </Field>
          </div>
        </div>

        <div className="flex justify-end border-t border-line pt-4">
          <Button type="submit" size="sm" loading={updatePreferences.isPending}>
            <Save className="h-3.5 w-3.5" aria-hidden="true" />
            Save preferences
          </Button>
        </div>
      </form>
    </SectionCard>
  );
}

function DataSection() {
  const { notify } = useToast();
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState<'json' | 'csv' | 'validate' | 'import' | 'reset' | null>(null);
  const [fileName, setFileName] = useState('');
  const [payload, setPayload] = useState<unknown>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [importMode, setImportMode] = useState<'replace' | 'merge'>('merge');
  const [importError, setImportError] = useState<string | null>(null);
  const [confirmImport, setConfirmImport] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const [resetText, setResetText] = useState('');
  const [resetError, setResetError] = useState<string | null>(null);
  const navigate = useNavigate();

  const download = async (kind: 'json' | 'csv') => {
    setBusy(kind);
    try {
      if (kind === 'json') await settingsApi.exportJson();
      else await settingsApi.exportCsv();
      notify(`Your ${kind.toUpperCase()} backup is downloading`, 'success');
    } catch (error) {
      notify(errorMessage(error, 'Could not export your data'), 'error');
    } finally {
      setBusy(null);
    }
  };

  const readFile = async (file: File | undefined) => {
    if (!file) return;
    setImportError(null);
    setPreview(null);
    setPayload(null);
    setFileName(file.name);
    setBusy('validate');
    try {
      const text = await file.text();
      const parsed: unknown = JSON.parse(text);
      const result = await settingsApi.validateImport(parsed);
      setPayload(parsed);
      setPreview(result);
    } catch (error) {
      setImportError(
        error instanceof SyntaxError
          ? 'That file is not valid JSON.'
          : errorMessage(error, 'Could not validate this backup.'),
      );
    } finally {
      setBusy(null);
      if (fileInput.current) fileInput.current.value = '';
    }
  };

  const applyImport = async () => {
    if (!payload) return;
    setBusy('import');
    setImportError(null);
    try {
      const result = await settingsApi.import(payload, importMode);
      notify(result.message, 'success');
      setConfirmImport(false);
      setPreview(null);
      setPayload(null);
      setFileName('');
      await queryClient.invalidateQueries();
    } catch (error) {
      setImportError(errorMessage(error, 'Could not import this backup.'));
      setConfirmImport(false);
    } finally {
      setBusy(null);
    }
  };

  const reset = async () => {
    if (resetText !== 'RESET') {
      setResetError('Type RESET exactly to confirm.');
      return;
    }
    setBusy('reset');
    setResetError(null);
    try {
      await settingsApi.reset();
      setConfirmReset(false);
      setResetText('');
      notify('All progress was reset', 'success');
      queryClient.clear();
      navigate('/', { replace: true });
    } catch (error) {
      setResetError(errorMessage(error, 'Could not reset your progress.'));
    } finally {
      setBusy(null);
    }
  };

  return (
    <SectionCard
      icon={<FileJson className="h-4 w-4" aria-hidden="true" />}
      title="Your data"
      description="Export a backup, restore one, or start the roadmap from scratch."
    >
      <div className="space-y-5">
        <div>
          <h3 className="text-xs font-semibold text-text">Export</h3>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            Download every note, task, session, project and bookmark. JSON is a complete backup;
            CSV is a flat topic-progress summary.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              loading={busy === 'json'}
              onClick={() => void download('json')}
            >
              <Download className="h-3.5 w-3.5" aria-hidden="true" />
              Export JSON
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              loading={busy === 'csv'}
              onClick={() => void download('csv')}
            >
              <Download className="h-3.5 w-3.5" aria-hidden="true" />
              Export CSV
            </Button>
          </div>
        </div>

        <div className="border-t border-line pt-5">
          <h3 className="text-xs font-semibold text-text">Import a backup</h3>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            Validate the file first, then choose whether to merge it with your current progress or
            replace everything.
          </p>

          <input
            ref={fileInput}
            type="file"
            accept="application/json,.json"
            className="sr-only"
            onChange={(event) => void readFile(event.target.files?.[0])}
          />

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              loading={busy === 'validate'}
              onClick={() => fileInput.current?.click()}
            >
              <Upload className="h-3.5 w-3.5" aria-hidden="true" />
              Choose JSON file
            </Button>
            {fileName ? <span className="text-[11px] text-muted">{fileName}</span> : null}
          </div>

          {importError ? (
            <div
              className="mt-3 rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger"
              role="alert"
            >
              {importError}
            </div>
          ) : null}

          {preview ? (
            <div className="mt-3 rounded-lg border border-line bg-surface-2 p-3.5">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={preview.valid ? 'success' : 'danger'}>
                  {preview.valid ? 'Valid backup' : 'Invalid backup'}
                </Badge>
                {preview.schema_version ? (
                  <span className="text-[11px] text-muted">Schema {preview.schema_version}</span>
                ) : null}
              </div>

              {Object.keys(preview.counts).length > 0 ? (
                <dl className="mt-3 grid grid-cols-2 gap-2 text-[11px] sm:grid-cols-4">
                  {Object.entries(preview.counts).map(([key, value]) => (
                    <div key={key} className="rounded-md bg-surface px-2 py-1.5">
                      <dt className="truncate capitalize text-faint">{key.replace(/_/g, ' ')}</dt>
                      <dd className="tabular mt-0.5 font-semibold text-text">{value}</dd>
                    </div>
                  ))}
                </dl>
              ) : null}

              {preview.errors.length > 0 ? (
                <ul className="mt-3 space-y-1 text-[11px] text-danger" role="alert">
                  {preview.errors.map((error) => (
                    <li key={error}>• {error}</li>
                  ))}
                </ul>
              ) : null}

              {preview.warnings.length > 0 ? (
                <ul className="mt-3 space-y-1 text-[11px] text-warning">
                  {preview.warnings.map((warning) => (
                    <li key={warning}>• {warning}</li>
                  ))}
                </ul>
              ) : null}

              {preview.valid ? (
                <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-end">
                  <Field label="Import mode" htmlFor="import-mode" className="sm:w-52">
                    <Select
                      id="import-mode"
                      value={importMode}
                      onChange={(event) =>
                        setImportMode(event.target.value === 'replace' ? 'replace' : 'merge')
                      }
                    >
                      <option value="merge">Merge with existing progress</option>
                      <option value="replace">Replace existing progress</option>
                    </Select>
                  </Field>
                  <Button
                    type="button"
                    size="sm"
                    onClick={() => setConfirmImport(true)}
                    loading={busy === 'import'}
                  >
                    Apply import
                  </Button>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>

        <div className="border-t border-line pt-5">
          <h3 className="flex items-center gap-1.5 text-xs font-semibold text-danger">
            <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
            Danger zone
          </h3>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            Reset deletes every note, task, session and progress record, then restores the six
            starter projects. Your account stays active.
          </p>
          <Button
            type="button"
            variant="danger"
            size="sm"
            className="mt-3"
            onClick={() => {
              setResetText('');
              setResetError(null);
              setConfirmReset(true);
            }}
          >
            <RefreshCcw className="h-3.5 w-3.5" aria-hidden="true" />
            Reset all progress
          </Button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmImport}
        onClose={() => setConfirmImport(false)}
        onConfirm={() => void applyImport()}
        title={importMode === 'replace' ? 'Replace all progress?' : 'Merge this backup?'}
        description={
          importMode === 'replace'
            ? 'Replace removes your current notes, tasks, sessions and projects before restoring this backup.'
            : 'Merge keeps your current records and adds anything new from this backup.'
        }
        confirmLabel={importMode === 'replace' ? 'Replace and import' : 'Merge and import'}
        loading={busy === 'import'}
        tone={importMode === 'replace' ? 'danger' : 'primary'}
      />

      <ConfirmDialog
        open={confirmReset}
        onClose={() => {
          setConfirmReset(false);
          setResetError(null);
        }}
        onConfirm={() => void reset()}
        title="Reset all progress?"
        description="This cannot be undone. Export a backup first if you might want this data later."
        confirmLabel="Reset everything"
        loading={busy === 'reset'}
      >
        <div className="mt-3">
          <Field
            label={
              <span>
                Type <span className="font-mono font-semibold text-danger">RESET</span> to confirm
              </span>
            }
            htmlFor="reset-confirm"
            error={resetError}
          >
            <Input
              id="reset-confirm"
              value={resetText}
              onChange={(event) => {
                setResetText(event.target.value);
                setResetError(null);
              }}
              placeholder="RESET"
              autoComplete="off"
            />
          </Field>
        </div>
      </ConfirmDialog>
    </SectionCard>
  );
}

export default function SettingsPage() {
  usePageTitle('Settings');
  const { user } = useAuth();

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Account"
        title="Settings"
        description="Manage your account, daily study rhythm and the data behind your progress."
        actions={
          user ? (
            <Badge tone="accent" className="h-7 px-2.5">
              {user.role === 'admin' ? 'Administrator' : 'Learner'}
            </Badge>
          ) : null
        }
      />

      <ProfileSection />
      <PreferencesSection />
      <PasswordSection />
      <DataSection />
    </div>
  );
}
