import { ApiError } from '@/api/client';

export function errorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

/** Map backend validation errors onto form fields. */
export function fieldErrors(error: unknown): Record<string, string> {
  const result: Record<string, string> = {};
  if (!(error instanceof ApiError) || !error.fieldErrors) return result;
  for (const item of error.fieldErrors) {
    if (!result[item.field]) result[item.field] = item.message;
  }
  return result;
}
