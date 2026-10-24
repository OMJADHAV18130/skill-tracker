/** Formatting helpers shared across the app. */

export function formatMinutes(minutes: number | null | undefined): string {
  const total = Math.max(0, Math.round(minutes ?? 0));
  if (total === 0) return '0m';
  const hours = Math.floor(total / 60);
  const rest = total % 60;
  if (hours === 0) return `${rest}m`;
  if (rest === 0) return `${hours}h`;
  return `${hours}h ${rest}m`;
}

export function formatHours(minutes: number | null | undefined, digits = 1): string {
  const hours = (minutes ?? 0) / 60;
  if (hours === 0) return '0';
  if (hours >= 100) return Math.round(hours).toString();
  return hours.toFixed(digits).replace(/\.0$/, '');
}

export function formatPercentage(value: number | null | undefined, digits = 0): string {
  const safe = Number.isFinite(value ?? NaN) ? (value as number) : 0;
  return `${safe.toFixed(digits)}%`;
}

export function formatDate(value: string | Date | null | undefined, opts?: Intl.DateTimeFormatOptions): string {
  if (!value) return '—';
  const date = typeof value === 'string' ? parseDate(value) : value;
  if (!date || Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, opts ?? { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
}

export function formatShortDate(value: string | Date | null | undefined): string {
  return formatDate(value, { month: 'short', day: 'numeric' });
}

export function formatDayLabel(value: string | Date): string {
  const date = typeof value === 'string' ? parseDate(value) : value;
  if (!date) return '';
  return new Intl.DateTimeFormat(undefined, { weekday: 'short' }).format(date);
}

export function formatTimeOfDay(value: string | null | undefined): string {
  if (!value) return '—';
  return value.slice(0, 5);
}

export function relativeTime(value: string | null | undefined): string {
  if (!value) return '';
  const date = parseDate(value);
  if (!date) return '';
  const diff = Date.now() - date.getTime();
  const minutes = Math.round(diff / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days}d ago`;
  return formatShortDate(date);
}

/** Parse a `YYYY-MM-DD` date as a *local* date (avoids UTC off-by-one). */
export function parseDate(value: string): Date | null {
  if (!value) return null;
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (match) {
    return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function toISODate(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function todayISO(): string {
  return toISODate(new Date());
}

export function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

export function startOfWeek(date: Date): Date {
  const copy = new Date(date);
  const day = copy.getDay(); // 0 = Sunday
  const diff = (day + 6) % 7; // Monday-based
  copy.setDate(copy.getDate() - diff);
  copy.setHours(0, 0, 0, 0);
  return copy;
}

export function monthLabel(year: number, month: number): string {
  return new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' }).format(
    new Date(year, month - 1, 1),
  );
}

export function initials(name: string | null | undefined, fallback = 'U'): string {
  if (!name) return fallback;
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return fallback;
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function pluralize(count: number, singular: string, plural?: string): string {
  return count === 1 ? singular : (plural ?? `${singular}s`);
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
