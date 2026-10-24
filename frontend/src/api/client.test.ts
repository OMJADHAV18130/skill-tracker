import { beforeEach, describe, expect, it } from 'vitest';
import {
  ApiError,
  clearSession,
  loadSession,
  saveSession,
  sessionFromTokenPair,
  type StoredSession,
} from '@/api/client';
import type { TokenPair } from '@/types/api';

const pair: TokenPair = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  token_type: 'bearer',
  expires_in: 900,
  user: {
    id: 'user-1',
    email: 'demo@devpath.dev',
    username: 'demo',
    full_name: 'Demo Learner',
    role: 'user',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    last_login_at: null,
  },
};

beforeEach(() => {
  localStorage.clear();
});

describe('ApiError', () => {
  it('exposes validation and auth flags', () => {
    const validation = new ApiError('Invalid input', {
      status: 422,
      code: 'validation_error',
      fieldErrors: [{ field: 'email', message: 'Invalid email' }],
    });
    expect(validation.isValidation).toBe(true);
    expect(validation.isAuthError).toBe(false);
    expect(validation.fieldErrors?.[0].message).toBe('Invalid email');
  });

  it('identifies unauthorised responses', () => {
    const unauthorised = new ApiError('Sign in again', { status: 401 });
    expect(unauthorised.isAuthError).toBe(true);
    expect(unauthorised.code).toBe('error');
  });
});

describe('session storage', () => {
  it('returns null when no session is stored', () => {
    expect(loadSession()).toBeNull();
  });

  it('round-trips a token pair', () => {
    saveSession(sessionFromTokenPair(pair));
    const session = loadSession();
    expect(session?.accessToken).toBe('access-token');
    expect(session?.refreshToken).toBe('refresh-token');
    expect(session?.user.email).toBe('demo@devpath.dev');
    expect(session?.expiresAt).toBeGreaterThan(Date.now());
  });

  it('survives corrupt JSON without throwing', () => {
    localStorage.setItem('devpath.auth', '{not-json');
    expect(loadSession()).toBeNull();
  });

  it('clears the stored session', () => {
    const stored: StoredSession = sessionFromTokenPair(pair);
    saveSession(stored);
    clearSession();
    expect(loadSession()).toBeNull();
  });
});
