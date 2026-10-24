import { useEffect } from 'react';
import { Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom';
import { AppShell, RequireAuth } from '@/components/layout/AppShell';
import { FullPageLoader } from '@/components/ui/Spinner';
import { useAuth } from '@/contexts/AuthContext';
import DashboardPage from '@/pages/DashboardPage';
import LoginPage from '@/pages/LoginPage';
import NotFoundPage from '@/pages/NotFoundPage';
import PlannerPage from '@/pages/PlannerPage';
import ProjectsPage from '@/pages/ProjectsPage';
import RegisterPage from '@/pages/RegisterPage';
import ResourcesPage from '@/pages/ResourcesPage';
import RoadmapPage from '@/pages/RoadmapPage';
import SettingsPage from '@/pages/SettingsPage';
import TopicDetailPage from '@/pages/TopicDetailPage';

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
  }, [pathname]);
  return null;
}

/** Redirect signed-in users away from the auth pages. */
function PublicOnly({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <FullPageLoader label="Checking your session…" />;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route
          path="/login"
          element={
            <PublicOnly>
              <LoginPage />
            </PublicOnly>
          }
        />
        <Route
          path="/register"
          element={
            <PublicOnly>
              <RegisterPage />
            </PublicOnly>
          }
        />

        <Route
          element={
            <RequireAuth>
              <AppShell>
                <Outlet />
              </AppShell>
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/roadmap/topics/:topicId" element={<TopicDetailPage />} />
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}
