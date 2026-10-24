import type { LucideIcon } from 'lucide-react';
import { ArrowRight, Inbox } from 'lucide-react';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/cn';

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: {
  icon?: LucideIcon;
  title: string;
  description?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex flex-col items-center justify-center px-6 py-12 text-center', className)}>
      <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-line bg-surface-2 text-muted">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </div>
      <h3 className="mt-3 text-sm font-semibold text-text">{title}</h3>
      {description ? (
        <p className="mt-1 max-w-sm text-xs leading-relaxed text-muted">{description}</p>
      ) : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function ErrorState({
  title = 'Could not load this page',
  description = 'Check your connection and try again.',
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-card border border-danger/20 bg-danger-soft/40 px-6 py-12 text-center">
      <h3 className="text-sm font-semibold text-text">{title}</h3>
      <p className="mt-1 max-w-sm text-xs leading-relaxed text-muted">{description}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface px-3 py-1.5 text-xs font-medium text-text shadow-card transition hover:bg-surface-hover"
        >
          Try again
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      ) : null}
    </div>
  );
}

export function InlineLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link
      to={to}
      className="inline-flex items-center gap-1 text-xs font-medium text-accent transition hover:text-accent-hover"
    >
      {children}
      <ArrowRight className="h-3 w-3" aria-hidden="true" />
    </Link>
  );
}
