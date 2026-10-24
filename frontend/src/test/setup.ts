import '@testing-library/jest-dom/vitest';

// jsdom does not implement matchMedia, which the theme provider relies on.
if (!window.matchMedia) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }),
  });
}

// Keep tests quiet about jsdom's missing scroll implementation.
if (!window.scrollTo) {
  Object.defineProperty(window, 'scrollTo', { writable: true, value: () => undefined });
}
