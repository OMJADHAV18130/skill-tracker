import { describe, expect, it } from 'vitest';
import {
  addDays,
  clamp,
  formatHours,
  formatMinutes,
  formatPercentage,
  formatTimeOfDay,
  initials,
  parseDate,
  pluralize,
  startOfWeek,
  toISODate,
} from '@/lib/format';

describe('formatMinutes', () => {
  it('renders minutes below an hour', () => {
    expect(formatMinutes(0)).toBe('0m');
    expect(formatMinutes(45)).toBe('45m');
  });

  it('renders hours and remaining minutes', () => {
    expect(formatMinutes(60)).toBe('1h');
    expect(formatMinutes(90)).toBe('1h 30m');
    expect(formatMinutes(125)).toBe('2h 5m');
  });

  it('clamps negative and nullish input', () => {
    expect(formatMinutes(-20)).toBe('0m');
    expect(formatMinutes(null)).toBe('0m');
  });
});

describe('formatHours', () => {
  it('converts minutes to trimmed hours', () => {
    expect(formatHours(0)).toBe('0');
    expect(formatHours(60)).toBe('1');
    expect(formatHours(90)).toBe('1.5');
    expect(formatHours(6000)).toBe('100');
  });
});

describe('dates', () => {
  it('parses YYYY-MM-DD as a local date', () => {
    const date = parseDate('2026-03-01');
    expect(date?.getFullYear()).toBe(2026);
    expect(date?.getMonth()).toBe(2);
    expect(date?.getDate()).toBe(1);
  });

  it('round-trips an ISO date without timezone drift', () => {
    expect(toISODate(new Date(2026, 0, 5))).toBe('2026-01-05');
  });

  it('adds days across a month boundary', () => {
    expect(toISODate(addDays(new Date(2026, 0, 31), 1))).toBe('2026-02-01');
  });

  it('finds Monday as the start of the week', () => {
    const start = startOfWeek(new Date(2026, 9, 25)); // Sunday
    expect(toISODate(start)).toBe('2026-10-19');
    expect(start.getDay()).toBe(1);
  });
});

describe('small helpers', () => {
  it('formats percentages safely', () => {
    expect(formatPercentage(42.6)).toBe('43%');
    expect(formatPercentage(null)).toBe('0%');
  });

  it('trims reminder times to HH:MM', () => {
    expect(formatTimeOfDay('07:30:00')).toBe('07:30');
    expect(formatTimeOfDay(null)).toBe('—');
  });

  it('derives initials from names', () => {
    expect(initials('Ada Lovelace')).toBe('AL');
    expect(initials('grace')).toBe('GR');
    expect(initials(null)).toBe('U');
  });

  it('pluralises and clamps', () => {
    expect(pluralize(1, 'topic')).toBe('topic');
    expect(pluralize(2, 'topic')).toBe('topics');
    expect(pluralize(2, 'phase', 'phases')).toBe('phases');
    expect(clamp(120, 30, 90)).toBe(90);
    expect(clamp(10, 30, 90)).toBe(30);
  });
});
