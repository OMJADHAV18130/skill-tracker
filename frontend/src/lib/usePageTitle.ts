import { useEffect } from 'react';

/** Keep the browser tab title in sync with the current page. */
export function usePageTitle(title?: string): void {
  useEffect(() => {
    document.title = title ? `${title} · DevPath` : 'DevPath — Learning Roadmap';
  }, [title]);
}
