import { NavLink } from 'react-router-dom';
import {
  CalendarDays,
  FolderKanban,
  LayoutDashboard,
  Library,
  Map,
  Settings,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/cn';

export const navigation = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/roadmap', label: 'Roadmap', icon: Map },
  { to: '/planner', label: 'Daily planner', icon: CalendarDays },
  { to: '/projects', label: 'Projects', icon: FolderKanban },
  { to: '/resources', label: 'Resources', icon: Library },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-accent-fg shadow-card">
        D
      </span>
      {!compact ? (
        <span className="leading-none">
          <span className="block text-sm font-semibold tracking-tight text-text">DevPath</span>
          <span className="mt-0.5 block text-[10px] font-medium uppercase tracking-[0.16em] text-faint">
            Backend + DevOps
          </span>
        </span>
      ) : null}
    </div>
  );
}

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="space-y-1" aria-label="Main navigation">
      {navigation.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-accent-soft text-accent-soft-fg'
                  : 'text-muted hover:bg-surface-hover hover:text-text',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  className={cn('h-4 w-4', isActive ? 'text-accent' : 'text-faint group-hover:text-muted')}
                  aria-hidden="true"
                />
                {item.label}
              </>
            )}
          </NavLink>
        );
      })}
    </nav>
  );
}

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col border-r border-line bg-surface lg:flex">
      <div className="px-4 pb-5 pt-5">
        <Brand />
      </div>
      <div className="flex-1 overflow-y-auto px-3">
        <p className="mb-2 px-2.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-faint">
          Workspace
        </p>
        <SidebarNav />
      </div>
      <div className="m-3 rounded-xl border border-line bg-surface-2 p-3">
        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-text">
          <Sparkles className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
          12-month path
        </div>
        <p className="mt-1 text-[11px] leading-relaxed text-muted">
          Seven phases from Java fundamentals to Kubernetes and production observability.
        </p>
      </div>
      <div className="border-t border-line px-4 py-3 text-[10px] text-faint">
        DevPath v1.0 · your progress is private
      </div>
    </aside>
  );
}
