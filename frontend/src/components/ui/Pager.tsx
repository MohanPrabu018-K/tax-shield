'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

/** Server-pagination controls. `hasMore` = fetched a full page. */
export function Pager({ page, pageSize, hasMore, count, onPage }: {
  page: number; pageSize: number; hasMore: boolean; count: number;
  onPage: (p: number) => void;
}) {
  return (
    <div className="flex items-center justify-between px-1 py-3" aria-label="Pagination">
      <p className="text-sm text-gray-500" aria-live="polite">
        Page {page + 1} · {count} shown
      </p>
      <div className="flex gap-2">
        <Button variant="secondary" size="sm" disabled={page === 0} onClick={() => onPage(page - 1)} aria-label="Previous page">
          <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        </Button>
        <Button variant="secondary" size="sm" disabled={!hasMore} onClick={() => onPage(page + 1)} aria-label="Next page">
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </Button>
      </div>
    </div>
  );
}
