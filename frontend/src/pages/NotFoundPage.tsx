import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Compass, LayoutDashboard, Map } from 'lucide-react';
import { Brand } from '@/components/layout/Sidebar';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { usePageTitle } from '@/lib/usePageTitle';

export default function NotFoundPage() {
  usePageTitle('Page not found');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <header className="flex items-center justify-between px-4 py-4 sm:px-8">
        <Link to="/" aria-label="DevPath home">
          <Brand />
        </Link>
      </header>

      <main className="flex flex-1 items-center justify-center px-4 pb-16">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-line bg-surface text-accent shadow-card">
            <Compass className="h-6 w-6" aria-hidden="true" />
          </div>
          <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.18em] text-faint">
            404 · Off the map
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-text">
            This page isn&apos;t on the roadmap
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-muted">
            The link may be outdated, or the page may have moved. Your progress is untouched — head
            back to the dashboard and keep going.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            {isAuthenticated ? (
              <>
                <Button onClick={() => navigate('/')}>
                  <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
                  Go to dashboard
                </Button>
                <Button variant="secondary" onClick={() => navigate('/roadmap')}>
                  <Map className="h-4 w-4" aria-hidden="true" />
                  Open roadmap
                </Button>
              </>
            ) : (
              <Button onClick={() => navigate('/login')}>
                <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                Back to sign in
              </Button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
