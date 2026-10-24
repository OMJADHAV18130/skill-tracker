import { useEffect, useRef, useState } from 'react';
import { Navigate, NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  ChevronDown,
  LogOut,
  Menu,
  Moon,
  Settings,
  Sun,
  X,
} from 'lucide-react';
import { Brand, Sidebar, SidebarNav, navigation } from '@/components/layout/Sidebar';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { cn } from '@/lib/cn';
import { initials } from '@/lib/format';

const titles: Record<string, string> = {
  '/': 'Dashboard',
  '/roadmap': 'Roadmap',
  '/planner': 'Daily planner',
  '/projects': 'Projects',
  '/resources': 'Resources',
  '/settings': 'Settings',
};

function currentTitle(pathname: string): string {
  if (pathname.startsWith('/roadmap/topics/')) return 'Topic details';
  return titles[pathname] ?? 'DevPath';
}

function UserMenu() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!open) return;
    const onClick = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  if (!user) return null;

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-2 rounded-lg px-1.5 py-1 transition hover:bg-surface-hover"
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-accent-soft text-[11px] font-semibold text-accent-soft-fg">
          {initials(user.full_name || user.username)}
        </span>
        <span className="hidden text-left sm:block">
          <span className="block max-w-32 truncate text-xs font-medium leading-tight text-text">
            {user.full_name || user.username}
          </span>
          <span className="block max-w-32 truncate text-[10px] leading-tight text-muted">
            {user.email}
          </span>
        </span>
        <ChevronDown className="h-3.5 w-3.5 text-faint" aria-hidden="true" />
      </button>
      {open ? (
        <div
          role="menu"
          className="animate-in absolute right-0 top-full z-50 mt-1.5 w-52 overflow-hidden rounded-xl border border-line bg-surface p-1 shadow-overlay"
        >
          <div className="border-b border-line px-2.5 py-2">
            <p className="truncate text-xs font-medium text-text">{user.full_name || user.username}</p>
            <p className="truncate text-[11px] text-muted">{user.email}</p>
          </div>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setOpen(false);
              navigate('/settings');
            }}
            className="mt-1 flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-muted transition hover:bg-surface-hover hover:text-text"
          >
            <Settings className="h-3.5 w-3.5" aria-hidden="true" />
            Settings
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setOpen(false);
              void logout();
            }}
            className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-danger transition hover:bg-danger-soft"
          >
            <LogOut className="h-3.5 w-3.5" aria-hidden="true" />
            Sign out
          </button>
        </div>
      ) : null}
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  const { resolved, toggle } = useTheme();
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    setDrawerOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = drawerOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [drawerOpen]);

  return (
    <div className="min-h-full bg-bg">
      <Sidebar />

      {drawerOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/45 backdrop-blur-[2px]"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />
          <div className="animate-in absolute inset-y-0 left-0 flex w-72 flex-col border-r border-line bg-surface shadow-overlay">
            <div className="flex items-center justify-between px-4 pb-5 pt-5">
              <Brand />
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                className="-m-1 rounded-lg p-1.5 text-muted transition hover:bg-surface-hover"
                aria-label="Close navigation"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="px-3">
              <SidebarNav onNavigate={() => setDrawerOpen(false)} />
            </div>
          </div>
        </div>
      ) : null}

      <div className="lg:pl-60">
        <header className="sticky top-0 z-40 border-b border-line bg-bg/85 backdrop-blur-md">
          <div className="flex h-14 items-center justify-between gap-3 px-4 sm:px-6">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setDrawerOpen(true)}
                className="-ml-1 rounded-lg p-2 text-muted transition hover:bg-surface-hover hover:text-text lg:hidden"
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div className="lg:hidden">
                <Brand compact />
              </div>
              <p className="hidden text-sm font-medium text-text lg:block">{currentTitle(pathname)}</p>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={toggle}
                className="rounded-lg p-2 text-muted transition hover:bg-surface-hover hover:text-text"
                aria-label={`Switch to ${resolved === 'dark' ? 'light' : 'dark'} theme`}
              >
                {resolved === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>
              <UserMenu />
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1180px] px-4 pb-24 pt-6 sm:px-6 lg:pb-10">
          {children}
        </main>
      </div>

      {/* Mobile bottom navigation */}
      <nav
        className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface/95 backdrop-blur-md lg:hidden"
        aria-label="Mobile navigation"
      >
        <div className="flex items-stretch justify-around px-1 pb-[env(safe-area-inset-bottom)]">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  cn(
                    'flex flex-1 flex-col items-center gap-1 py-2 text-[10px] font-medium transition-colors',
                    isActive ? 'text-accent' : 'text-faint',
                  )
                }
              >
                <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
                {item.label.split(' ')[0]}
              </NavLink>
            );
          })}
        </div>
      </nav>
    </div>
  );
}

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg">
        <div className="flex flex-col items-center gap-3">
          <span className="h-8 w-8 animate-spin rounded-full border-2 border-line border-t-accent" />
          <p className="text-sm text-muted">Restoring your session…</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
}
