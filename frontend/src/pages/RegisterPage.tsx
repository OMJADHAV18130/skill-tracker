import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  Layers,
  LockKeyhole,
  Mail,
  Moon,
  ShieldCheck,
  Sun,
  UserRound,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { Field, Input } from '@/components/ui/Field';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useToast } from '@/contexts/ToastContext';
import { errorMessage, fieldErrors } from '@/lib/errors';
import { usePageTitle } from '@/lib/usePageTitle';

const benefits = [
  'Seven phases and 69 curated topics',
  'Daily planner with streaks and study hours',
  'Six portfolio projects with milestones',
  'Notes, checklists and official docs',
];

export default function RegisterPage() {
  usePageTitle('Create account');
  const { register } = useAuth();
  const { notify } = useToast();
  const { resolved, toggle } = useTheme();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirm_password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const set = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setErrors({});

    const nextErrors: Record<string, string> = {};
    if (!form.email.trim().includes('@')) nextErrors.email = 'Enter a valid email address.';
    if (!/^[a-zA-Z0-9_.-]{3,64}$/.test(form.username.trim())) {
      nextErrors.username = 'Use 3–64 letters, numbers, dots, dashes or underscores.';
    }
    if (form.password.length < 8) nextErrors.password = 'Use at least 8 characters.';
    if (form.password !== form.confirm_password) {
      nextErrors.confirm_password = 'The passwords do not match.';
    }
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setSubmitting(true);
    try {
      await register({
        email: form.email.trim(),
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        password: form.password,
      });
      notify('Your roadmap is ready', 'success');
      navigate('/', { replace: true });
    } catch (caught) {
      setErrors(fieldErrors(caught));
      setError(errorMessage(caught, 'We could not create your account.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-screen bg-bg">
      <div className="flex flex-1 flex-col">
        <div className="flex items-center justify-between px-4 py-4 sm:px-8">
          <Link
            to="/login"
            className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-medium text-muted transition hover:bg-surface-hover hover:text-text"
          >
            <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
            Back to sign in
          </Link>
          <button
            type="button"
            onClick={toggle}
            className="rounded-lg p-2 text-muted transition hover:bg-surface-hover hover:text-text"
            aria-label={`Switch to ${resolved === 'dark' ? 'light' : 'dark'} theme`}
          >
            {resolved === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </div>

        <div className="flex flex-1 items-center justify-center px-4 pb-10 sm:px-8">
          <div className="w-full max-w-[440px]">
            <div className="mb-6">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-accent-fg shadow-card">
                  D
                </span>
                <span className="text-sm font-semibold tracking-tight text-text">DevPath</span>
              </div>
              <h1 className="mt-5 text-2xl font-semibold tracking-tight text-text">
                Start your backend path
              </h1>
              <p className="mt-1.5 text-sm leading-relaxed text-muted">
                Your account gets the full roadmap and six starter projects, ready to shape around
                your schedule.
              </p>
            </div>

            <Card>
              <CardBody className="space-y-5">
                {error ? (
                  <div
                    className="rounded-lg border border-danger/25 bg-danger-soft px-3 py-2 text-xs text-danger"
                    role="alert"
                  >
                    {error}
                  </div>
                ) : null}

                <form className="space-y-4" onSubmit={(event) => void submit(event)} noValidate>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <Field label="Full name" htmlFor="register-name" error={errors.full_name}>
                      <div className="relative">
                        <UserRound
                          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
                          aria-hidden="true"
                        />
                        <Input
                          id="register-name"
                          value={form.full_name}
                          onChange={(event) => set('full_name', event.target.value)}
                          placeholder="Ada Lovelace"
                          className="pl-9"
                          autoComplete="name"
                        />
                      </div>
                    </Field>

                    <Field label="Username" htmlFor="register-username" error={errors.username}>
                      <Input
                        id="register-username"
                        value={form.username}
                        onChange={(event) => set('username', event.target.value)}
                        placeholder="ada.dev"
                        autoComplete="username"
                        invalid={Boolean(errors.username)}
                      />
                    </Field>
                  </div>

                  <Field label="Email" htmlFor="register-email" error={errors.email}>
                    <div className="relative">
                      <Mail
                        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
                        aria-hidden="true"
                      />
                      <Input
                        id="register-email"
                        type="email"
                        value={form.email}
                        onChange={(event) => set('email', event.target.value)}
                        placeholder="you@example.com"
                        className="pl-9"
                        autoComplete="email"
                        invalid={Boolean(errors.email)}
                      />
                    </div>
                  </Field>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <Field
                      label="Password"
                      htmlFor="register-password"
                      error={errors.password}
                      hint="At least 8 characters."
                    >
                      <div className="relative">
                        <LockKeyhole
                          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
                          aria-hidden="true"
                        />
                        <Input
                          id="register-password"
                          type={showPassword ? 'text' : 'password'}
                          value={form.password}
                          onChange={(event) => set('password', event.target.value)}
                          className="pl-9 pr-9"
                          autoComplete="new-password"
                          invalid={Boolean(errors.password)}
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword((value) => !value)}
                          className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-md p-1 text-faint transition hover:text-text"
                          aria-label={showPassword ? 'Hide password' : 'Show password'}
                        >
                          {showPassword ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </Field>

                    <Field
                      label="Confirm password"
                      htmlFor="register-confirm"
                      error={errors.confirm_password}
                    >
                      <Input
                        id="register-confirm"
                        type={showPassword ? 'text' : 'password'}
                        value={form.confirm_password}
                        onChange={(event) => set('confirm_password', event.target.value)}
                        autoComplete="new-password"
                        invalid={Boolean(errors.confirm_password)}
                      />
                    </Field>
                  </div>

                  <Button type="submit" className="w-full" size="lg" loading={submitting}>
                    Create my account
                    <ArrowRight className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </form>

                <p className="text-center text-xs text-muted">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-accent hover:text-accent-hover">
                    Sign in
                  </Link>
                </p>
              </CardBody>
            </Card>

            <p className="mt-5 flex items-center justify-center gap-1.5 text-[11px] text-faint">
              <ShieldCheck className="h-3 w-3 text-success" aria-hidden="true" />
              Your progress is private to this account
            </p>
          </div>
        </div>
      </div>

      <div className="relative hidden w-[42%] flex-col justify-center overflow-hidden border-l border-line bg-surface-2 px-10 xl:flex">
        <div
          className="pointer-events-none absolute -right-20 top-1/4 h-72 w-72 rounded-full bg-accent/10 blur-3xl"
          aria-hidden="true"
        />
        <div className="relative max-w-sm">
          <Badge tone="accent">
            <Layers className="h-3 w-3" aria-hidden="true" />
            Backend + DevOps track
          </Badge>
          <h2 className="mt-4 text-2xl font-semibold leading-tight tracking-tight text-text">
            A complete path, not a pile of links.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-muted">
            Every phase connects theory, hands-on practice and a project that belongs in your
            portfolio.
          </p>
          <ul className="mt-7 space-y-3">
            {benefits.map((benefit) => (
              <li key={benefit} className="flex items-start gap-2.5 text-sm text-text">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-success-soft text-success">
                  <Check className="h-3 w-3" aria-hidden="true" />
                </span>
                {benefit}
              </li>
            ))}
          </ul>
          <div className="mt-8 rounded-xl border border-line bg-surface p-4 shadow-card">
            <p className="text-xs font-semibold text-text">Month 1 → Month 12</p>
            <p className="mt-1 text-xs leading-relaxed text-muted">
              Java fundamentals → Spring Boot APIs → databases → Docker → CI/CD → Kubernetes →
              production observability.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
