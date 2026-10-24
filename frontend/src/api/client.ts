/**
 * Centralised fetch wrapper.
 *
 * - injects the access token
 * - transparently refreshes an expired token once, then retries
 * - normalises every backend error into a typed `ApiError`
 * - emits `devpath:unauthorized` when the session cannot be recovered
 */

import type { ApiErrorBody, TokenPair } from '@/types/api';

const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '/api/v1';

const AUTH_STORAGE_KEY = 'devpath.auth';

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: Record<string, unknown>;
  readonly fieldErrors?: Array<{ field: string; message: string }>;

  constructor(
    message: string,
    options: {
      status: number;
      code?: string;
      details?: Record<string, unknown>;
      fieldErrors?: Array<{ field: string; message: string }>;
    },
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = options.status;
    this.code = options.code ?? 'error';
    this.details = options.details;
    this.fieldErrors = options.fieldErrors;
  }

  get isAuthError(): boolean {
    return this.status === 401;
  }

  get isValidation(): boolean {
    return this.status === 422;
  }
}

export interface StoredSession {
  accessToken: string;
  refreshToken: string;
  user: TokenPair['user'];
  expiresAt: number;
}

/* --------------------------------------------------------------- storage */

export function loadSession(): StoredSession | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredSession;
    if (!parsed?.accessToken || !parsed?.user) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveSession(session: StoredSession): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function sessionFromTokenPair(pair: TokenPair): StoredSession {
  return {
    accessToken: pair.access_token,
    refreshToken: pair.refresh_token,
    user: pair.user,
    expiresAt: Date.now() + pair.expires_in * 1000,
  };
}

function emitUnauthorized(): void {
  window.dispatchEvent(new CustomEvent('devpath:unauthorized'));
}

/* ---------------------------------------------------------------- fetch */

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  /** Skip the Authorization header (login/register). */
  anonymous?: boolean;
  /** Do not attempt a token refresh on 401. */
  noRetry?: boolean;
  query?: Record<string, string | number | boolean | undefined | null>;
}

let refreshInFlight: Promise<StoredSession | null> | null = null;

async function refreshSession(): Promise<StoredSession | null> {
  const session = loadSession();
  if (!session?.refreshToken) return null;

  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const response = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: session.refreshToken }),
        });
        if (!response.ok) {
          clearSession();
          return null;
        }
        const pair = (await response.json()) as TokenPair;
        const next = sessionFromTokenPair(pair);
        saveSession(next);
        return next;
      } catch {
        return null;
      } finally {
        // Allow a new refresh attempt on the next 401.
        setTimeout(() => {
          refreshInFlight = null;
        }, 0);
      }
    })();
  }
  return refreshInFlight;
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`;
  if (!query) return url;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === '') continue;
    params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

async function parseError(response: Response): Promise<ApiError> {
  let body: ApiErrorBody | undefined;
  try {
    body = (await response.json()) as ApiErrorBody;
  } catch {
    body = undefined;
  }

  const details = body?.error?.details as
    | (Record<string, unknown> & { errors?: Array<{ field: string; message: string }> })
    | undefined;

  let message = body?.error?.message ?? response.statusText ?? 'Something went wrong';

  if (response.status === 401) {
    message = body?.error?.message ?? 'Your session has expired. Please sign in again.';
  } else if (response.status === 429) {
    message = 'Too many requests. Please slow down and try again.';
  } else if (response.status >= 500) {
    message = 'The server ran into a problem. Please try again.';
  }

  return new ApiError(message, {
    status: response.status,
    code: body?.error?.code ?? `http_${response.status}`,
    details,
    fieldErrors: details?.errors,
  });
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, anonymous, noRetry, query, headers, ...rest } = options;

  const doFetch = async (): Promise<Response> => {
    const session = anonymous ? null : loadSession();
    const requestHeaders: Record<string, string> = {
      Accept: 'application/json',
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(session?.accessToken ? { Authorization: `Bearer ${session.accessToken}` } : {}),
      ...((headers as Record<string, string>) ?? {}),
    };

    return fetch(buildUrl(path, query), {
      ...rest,
      headers: requestHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  };

  let response = await doFetch();

  if (response.status === 401 && !anonymous && !noRetry) {
    const refreshed = await refreshSession();
    if (refreshed) {
      response = await doFetch();
    } else {
      emitUnauthorized();
      throw await parseError(response);
    }
  }

  if (!response.ok) {
    const error = await parseError(response);
    // A 401 from change-password means the *current* password was wrong, not
    // that the session expired. Do not sign the user out in that case.
    if (error.status === 401 && path !== '/auth/change-password') emitUnauthorized();
    throw error;
  }

  if (response.status === 204) return undefined as T;

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as T;
}

export const api = {
  get: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'POST', body }),
  put: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'PUT', body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'PATCH', body }),
  delete: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'DELETE' }),
  /** Download a file (export) and trigger the browser save dialog. */
  download: async (path: string, filename: string) => {
    const session = loadSession();
    const response = await fetch(buildUrl(path), {
      headers: session ? { Authorization: `Bearer ${session.accessToken}` } : {},
    });
    if (!response.ok) throw await parseError(response);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  },
};

export { API_BASE };
