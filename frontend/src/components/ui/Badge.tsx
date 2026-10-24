import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/cn';

type Tone = 'neutral' | 'accent' | 'success' | 'warning' | 'danger' | 'info';

const tones: Record<Tone, string> = {
  neutral: 'border-line bg-surface-2 text-muted',
  accent: 'border-accent/25 bg-accent-soft text-accent-soft-fg',
  success: 'border-success/25 bg-success-soft text-success',
  warning: 'border-warning/25 bg-warning-soft text-warning',
  danger: 'border-danger/25 bg-danger-soft text-danger',
  info: 'border-info/25 bg-info-soft text-info',
};

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

export function Badge({ tone = 'neutral', className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium leading-4',
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}

export function statusTone(status: string): Tone {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'accent';
    case 'archived':
      return 'neutral';
    default:
      return 'neutral';
  }
}

export function priorityTone(priority: string): Tone {
  switch (priority) {
    case 'high':
      return 'danger';
    case 'medium':
      return 'warning';
    default:
      return 'neutral';
  }
}

export function statusLabel(status: string): string {
  return status.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}
