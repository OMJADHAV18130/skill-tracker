import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { api, clearSession, loadSession, saveSession, sessionFromTokenPair } from '@/api/client';
import type { TokenPair, User } from '@/types/api';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (patch: Partial<Pick<User, 'full_name' | 'email' | 'username'>>) => Promise<User>;
}

export interface RegisterInput {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function persist(pair: TokenPair): User {
  const session = sessionFromTokenPair(pair);
  saveSession(session);
  return pair.user;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => loadSession()?.user ?? null);
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(loadSession()));

  // Revalidate a stored session once on mount. The API client transparently
  // refreshes the token if it has expired.
  useEffect(() => {
    if (!loadSession()) {
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    api
      .get<User>('/auth/me')
      .then((me) => {
        if (cancelled) return;
        setUser(me);
        const session = loadSession();
        if (session) saveSession({ ...session, user: me });
      })
      .catch(() => {
        if (cancelled) return;
        clearSession();
        setUser(null);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // The API client emits this when a refresh fails.
  useEffect(() => {
    const handler = () => {
      clearSession();
      setUser(null);
    };
    window.addEventListener('devpath:unauthorized', handler);
    return () => window.removeEventListener('devpath:unauthorized', handler);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const pair = await api.post<TokenPair>(
      '/auth/login',
      { email, password },
      { anonymous: true },
    );
    setUser(persist(pair));
  }, []);

  const register = useCallback(async (input: RegisterInput) => {
    const pair = await api.post<TokenPair>('/auth/register', input, { anonymous: true });
    setUser(persist(pair));
  }, []);

  const logout = useCallback(async () => {
    const session = loadSession();
    try {
      if (session) {
        await api.post('/auth/logout', { refresh_token: session.refreshToken });
      }
    } catch {
      // Signing out locally must always succeed.
    } finally {
      clearSession();
      setUser(null);
    }
  }, []);

  const updateUser = useCallback(async (patch: Partial<Pick<User, 'full_name' | 'email' | 'username'>>) => {
    const updated = await api.patch<User>('/auth/me', patch);
    setUser(updated);
    const session = loadSession();
    if (session) saveSession({ ...session, user: updated });
    return updated;
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      register,
      logout,
      updateUser,
    }),
    [user, isLoading, login, register, logout, updateUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
