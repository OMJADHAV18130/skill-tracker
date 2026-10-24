import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import LoginPage from '@/pages/LoginPage';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ToastProvider } from '@/contexts/ToastContext';
import { DEMO_EMAIL, DEMO_PASSWORD } from '@/lib/constants';
import type { TokenPair } from '@/types/api';

const tokenPair: TokenPair = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  token_type: 'bearer',
  expires_in: 900,
  user: {
    id: 'user-1',
    email: DEMO_EMAIL,
    username: 'demo',
    full_name: 'Demo Learner',
    role: 'user',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    last_login_at: null,
  },
};

function ProfileProbe() {
  const { user } = useAuth();
  return <p>Signed in as {user?.email ?? 'nobody'}</p>;
}

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/"
                element={
                  <div>
                    <p>Dashboard ready</p>
                    <ProfileProbe />
                  </div>
                }
              />
            </Routes>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('LoginPage', () => {
  it('shows the demo credentials and requires an email', async () => {
    renderLogin();
    expect(screen.getByText(DEMO_EMAIL)).toBeInTheDocument();
    expect(screen.getByText(DEMO_PASSWORD)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Sign in/ }));
    expect(screen.getByText('Enter your email address.')).toBeInTheDocument();
  });

  it('fills the demo account and signs in', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => tokenPair,
      text: async () => '',
    });
    vi.stubGlobal('fetch', fetchMock);

    renderLogin();
    await userEvent.click(screen.getByRole('button', { name: /Fill demo credentials/ }));
    expect(screen.getByLabelText('Email')).toHaveValue(DEMO_EMAIL);
    expect(screen.getByLabelText('Password')).toHaveValue(DEMO_PASSWORD);

    await userEvent.click(screen.getByRole('button', { name: /^Sign in/ }));

    await waitFor(() => expect(screen.getByText('Dashboard ready')).toBeInTheDocument());
    expect(screen.getByText(`Signed in as ${DEMO_EMAIL}`)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/auth/login'),
      expect.objectContaining({ method: 'POST' }),
    );
    expect(localStorage.getItem('devpath.auth')).toContain('access-token');
  });

  it('surfaces API errors without signing in', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        error: { code: 'invalid_credentials', message: 'Invalid email or password' },
      }),
      text: async () => '',
    });
    vi.stubGlobal('fetch', fetchMock);

    renderLogin();
    await userEvent.type(screen.getByLabelText('Email'), 'demo@devpath.dev');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong-password');
    await userEvent.click(screen.getByRole('button', { name: /^Sign in/ }));

    await waitFor(() =>
      expect(screen.getByText('Invalid email or password')).toBeInTheDocument(),
    );
    expect(screen.queryByText('Dashboard ready')).not.toBeInTheDocument();
  });
});
