import { useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  BookOpenCheck,
  CheckCircle2,
  Eye,
  EyeOff,
  Flame,
  LockKeyhole,
  Mail,
  Moon,
  Sparkles,
  Sun,
  Target,
} from 'lucide-react';
import { Brand } from '@/components/layout/Sidebar';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { Field, Input } from '@/components/ui/Field';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useToast } from '@/contexts/ToastContext';
import { DEMO_EMAIL, DEMO_PASSWORD } from '@/lib/constants';
import { errorMessage, fieldErrors } from '@/lib/errors';
import { usePageTitle } from '@/lib/usePageTitle';

const highlights = [
  {
    icon: Target,
    title: 'A deliberate 12-month path',
    description: 'Seven phases, 69 topics and six portfolio projects — from Java basics to Kubernetes.',
  },
  {
    icon: Flame,
    title: 'Momentum you can see',
    description: 'Daily planning, study streaks and honest hours logged against your own goal.',
  },
  {
    icon: BookOpenCheck,
    title: 'One place for everything',
    description: 'Notes, checklists, official docs and project milestones stay attached to the roadmap.',
  },
];

export default function LoginPage() {
  usePageTitle('Sign in');
  const { login } = useAuth();
  const { notify } = useToast();
  const { resolved, toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const from = (() => {
    const state = location.state as { from?: unknown } | null;
    const target = state?.from;
    return typeof target === 'string' && target.startsWith('/') && !target.startsWith('/login')
      ? target
      : '/';
  })();

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setErrors({});

    if (!email.trim()) {
      setErrors({ email: 'Enter your email address.' });
      return;
    }
    if (!password) {
      setErrors({ password: 'Enter your password.' });
      return;
    }

    setSubmitting(true);
    try {
      await login(email.trim(), password);
      notify('Welcome back', 'success');
      navigate(from, { replace: true });
    } catch (caught) {
      setErrors(fieldErrors(caught));
      setError(errorMessage(caught, 'We could not sign you in.'));
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemo = () => {
    setEmail(DEMO_EMAIL);
    setPassword(DEMO_PASSWORD);
    setError(null);
    setErrors({});
  };

  return (
    <div className="relative flex min-h-screen bg-bg">
      <div className="relative hidden w-[46%] flex-col justify-between overflow-hidden bg-[#0e0e13] px-10 py-9 text-white lg:flex xl:px-14">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full bg-indigo-500/25 blur-3xl"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-emerald-500/15 blur-3xl"
          aria-hidden="true"
        />

        <div className="relative">
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 text-base font-bold backdrop-blur">
              D
            </span>
            <div>
              <p className="text-sm font-semibold tracking-tight">DevPath</p>
              <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-white/50">
                Backend + DevOps
              </p>
            </div>
          </div>
        </div>

        <div className="relative max-w-md">
          <Badge className="border-white/15 bg-white/10 text-white/80">
            <Sparkles className="h-3 w-3" aria-hidden="true" />
            A 12-month learning system
          </Badge>
          <h1 className="mt-5 text-[34px] font-semibold leading-[1.12] tracking-tight">
            Become the backend engineer who can ship and operate it.
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-white/60">
            Java, Spring Boot, PostgreSQL, Docker and Kubernetes — planned week by week, measured
            honestly, and kept in one calm workspace.
          </p>

          <ul className="mt-8 space-y-4">
            {highlights.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.title} className="flex gap-3">
                  <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/10 text-white/80">
                    <Icon className="h-4 w-4" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-white/55">
                      {item.description}
                    </p>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <p className="relative text-[11px] text-white/35">
          Progress is stored per account. Nothing is shared between learners.
        </p>
      </div>

      <div className="flex flex-1 flex-col">
        <div className="flex items-center justify-between px-4 py-4 sm:px-8">
          <div className="lg:hidden">
            <Brand />
          </div>
          <div className="ml-auto">
            <button
              type="button"
              onClick={toggle}
              className="rounded-lg p-2 text-muted transition hover:bg-surface-hover hover:text-text"
              aria-label={`Switch to ${resolved === 'dark' ? 'light' : 'dark'} theme`}
            >
              {resolved === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center px-4 pb-10 sm:px-8">
          <div className="w-full max-w-[420px]">
            <div className="mb-6 hidden lg:block">
              <h2 className="text-2xl font-semibold tracking-tight text-text">Welcome back</h2>
              <p className="mt-1.5 text-sm text-muted">
                Pick up exactly where your roadmap left off.
              </p>
            </div>
            <div className="mb-6 lg:hidden">
              <h2 className="text-xl font-semibold tracking-tight text-text">Sign in to DevPath</h2>
              <p className="mt-1.5 text-sm text-muted">
                Pick up exactly where your roadmap left off.
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
                  <Field label="Email" htmlFor="login-email" error={errors.email}>
                    <div className="relative">
                      <Mail
                        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
                        aria-hidden="true"
                      />
                      <Input
                        id="login-email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="you@example.com"
                        className="pl-9"
                        autoComplete="email"
                        autoFocus
                        invalid={Boolean(errors.email)}
                      />
                    </div>
                  </Field>

                  <Field label="Password" htmlFor="login-password" error={errors.password}>
                    <div className="relative">
                      <LockKeyhole
                        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-faint"
                        aria-hidden="true"
                      />
                      <Input
                        id="login-password"
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        placeholder="Your password"
                        className="pl-9 pr-10"
                        autoComplete="current-password"
                        invalid={Boolean(errors.password)}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword((value) => !value)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1 text-faint transition hover:text-text"
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

                  <Button type="submit" className="w-full" size="lg" loading={submitting}>
                    Sign in
                    <ArrowRight className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </form>

                <div className="rounded-xl border border-dashed border-line bg-surface-2 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-[11px] font-semibold text-text">Demo account</p>
                    <Badge tone="accent">Try it now</Badge>
                  </div>
                  <div className="mt-1.5 space-y-0.5 font-mono text-[11px] text-muted">
                    <p>{DEMO_EMAIL}</p>
                    <p>{DEMO_PASSWORD}</p>
                  </div>
                  <button
                    type="button"
                    onClick={fillDemo}
                    className="mt-2 inline-flex items-center gap-1 text-[11px] font-medium text-accent transition hover:text-accent-hover"
                  >
                    Fill demo credentials
                    <ArrowRight className="h-3 w-3" aria-hidden="true" />
                  </button>
                </div>

                <p className="text-center text-xs text-muted">
                  New to DevPath?{' '}
                  <Link to="/register" className="font-medium text-accent hover:text-accent-hover">
                    Create an account
                  </Link>
                </p>
              </CardBody>
            </Card>

            <p className="mt-5 flex items-center justify-center gap-1.5 text-[11px] text-faint">
              <CheckCircle2 className="h-3 w-3 text-success" aria-hidden="true" />
              Protected routes · hashed passwords · private progress
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
