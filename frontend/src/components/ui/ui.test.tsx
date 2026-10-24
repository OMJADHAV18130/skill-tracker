import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';

describe('Button', () => {
  it('renders its children and handles clicks', async () => {
    let clicks = 0;
    render(<Button onClick={() => (clicks += 1)}>Save changes</Button>);
    screen.getByRole('button', { name: 'Save changes' }).click();
    expect(clicks).toBe(1);
  });

  it('is disabled while loading', () => {
    render(<Button loading>Saving</Button>);
    expect(screen.getByRole('button', { name: /Saving/ })).toBeDisabled();
  });
});

describe('ProgressBar', () => {
  it('clamps values and exposes accessible progress', () => {
    render(<ProgressBar value={140} label="Roadmap progress" showValue />);
    const bar = screen.getByRole('progressbar', { name: 'Roadmap progress' });
    expect(bar).toHaveAttribute('aria-valuenow', '100');
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('handles invalid values', () => {
    render(<ProgressBar value={Number.NaN} label="Invalid" />);
    expect(screen.getByRole('progressbar', { name: 'Invalid' })).toHaveAttribute(
      'aria-valuenow',
      '0',
    );
  });
});
