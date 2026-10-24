import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

export function Spinner({ className }: { className?: string }) {
  return (
    <Loader2
      className={cn('h-5 w-5 animate-spin text-accent', className)}
      aria-label="Loading"
      role="status"
    />
  );
}

export function FullPageLoader({ label = 'Loading DevPath…' }: { label?: string }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3">
      <Spinner className="h-6 w-6" />
      <p className="text-sm text-muted">{label}</p>
    </div>
  );
}
