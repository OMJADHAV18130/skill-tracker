import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between', className)}>
      <div className="min-w-0">
        {eyebrow ? (
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-faint">
            {eyebrow}
          </p>
        ) : null}
        <h1 className="text-[22px] font-semibold leading-tight tracking-tight text-text sm:text-2xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-muted">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

export function SectionHeading({
  title,
  action,
}: {
  title: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="text-sm font-semibold text-text">{title}</h2>
      {action}
    </div>
  );
}

export function StatCard({
  label,
  value,
  hint,
  icon,
  tone = 'default',
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: ReactNode;
  tone?: 'default' | 'accent' | 'success';
}) {
  return (
    <div className="rounded-card border border-line bg-surface p-4 shadow-card">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-medium text-muted">{label}</p>
        {icon ? (
          <span
            className={cn(
              'flex h-7 w-7 items-center justify-center rounded-lg',
              tone === 'accent' && 'bg-accent-soft text-accent',
              tone === 'success' && 'bg-success-soft text-success',
              tone === 'default' && 'bg-surface-2 text-muted',
            )}
          >
            {icon}
          </span>
        ) : null}
      </div>
      <p className="tabular mt-2 text-2xl font-semibold tracking-tight text-text">{value}</p>
      {hint ? <p className="mt-1 text-[11px] leading-relaxed text-muted">{hint}</p> : null}
    </div>
  );
}
