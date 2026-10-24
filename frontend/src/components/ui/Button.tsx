import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg' | 'icon';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children?: ReactNode;
}

const variants: Record<Variant, string> = {
  primary:
    'bg-accent text-accent-fg hover:bg-accent-hover shadow-card disabled:hover:bg-accent',
  secondary:
    'bg-surface text-text border border-line hover:bg-surface-hover shadow-card disabled:hover:bg-surface',
  outline:
    'border border-line-strong bg-transparent text-text hover:bg-surface-hover disabled:hover:bg-transparent',
  ghost: 'bg-transparent text-muted hover:bg-surface-hover hover:text-text',
  danger: 'bg-danger text-white hover:opacity-90 shadow-card',
};

const sizes: Record<Size, string> = {
  sm: 'h-8 gap-1.5 rounded-lg px-3 text-xs font-medium',
  md: 'h-[38px] gap-2 rounded-lg px-3.5 text-sm font-medium',
  lg: 'h-11 gap-2 rounded-xl px-5 text-sm font-semibold',
  icon: 'h-9 w-9 rounded-lg',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = 'primary', size = 'md', loading = false, disabled, children, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        'inline-flex select-none items-center justify-center whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-55',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : null}
      {children}
    </button>
  );
});
