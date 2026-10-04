'use client';

import { ReactNode } from 'react';
import { AlertCircle, Inbox, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export function PageLoading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3" role="status" aria-live="polite">
      <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent" aria-hidden="true" />
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}

export function EmptyState({ title, body, action }: { title: string; body?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
      <Inbox className="h-10 w-10 text-gray-300" aria-hidden="true" />
      <h3 className="mt-3 text-base font-semibold text-gray-900">{title}</h3>
      {body && <p className="mt-1 text-sm text-gray-500 max-w-md">{body}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center" role="alert">
      <AlertCircle className="h-10 w-10 text-red-400" aria-hidden="true" />
      <h3 className="mt-3 text-base font-semibold text-gray-900">Something went wrong</h3>
      <p className="mt-1 text-sm text-gray-500 max-w-md">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} className="mt-4">
          <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" /> Retry
        </Button>
      )}
    </div>
  );
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-200 rounded ${className}`} aria-hidden="true" />;
}
