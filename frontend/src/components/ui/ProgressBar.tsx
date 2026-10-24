import { cn } from '@/lib/cn';

type Tone = 'accent' | 'success' | 'warning' | 'danger';

const tones: Record<Tone, string> = {
  accent: 'bg-accent',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
};

export function ProgressBar({
  value,
  tone = 'accent',
  className,
  label,
  showValue = false,
  size = 'md',
}: {
  value: number;
  tone?: Tone;
  className?: string;
  label?: string;
  showValue?: boolean;
  size?: 'sm' | 'md';
}) {
  const safe = Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0));
  return (
    <div className={cn('w-full', className)}>
      {label || showValue ? (
        <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
          {label ? <span className="text-muted">{label}</span> : <span />}
          {showValue ? <span className="tabular font-medium text-text">{safe.toFixed(0)}%</span> : null}
        </div>
      ) : null}
      <div
        className={cn('w-full overflow-hidden rounded-full bg-bg-subtle', size === 'sm' ? 'h-1' : 'h-2')}
        role="progressbar"
        aria-valuenow={Math.round(safe)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label ?? 'Progress'}
      >
        <div
          className={cn('h-full rounded-full transition-[width] duration-500 ease-out', tones[tone])}
          style={{ width: `${safe}%` }}
        />
      </div>
    </div>
  );
}
