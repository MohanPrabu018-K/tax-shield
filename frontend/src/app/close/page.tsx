'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { PageLoading, ErrorState } from '@/components/ui/State';
import { useAsync } from '@/lib/useApi';
import { api } from '@/lib/api';

export default function ClosePage() {
  const close = useAsync(() => api.getMonthEndClose());

  const label: Record<string, string> = { ok: 'PASS', attention: 'ACTION REQUIRED', review: 'WARNING' };
  const variant = (s: string) => (s === 'ok' ? 'success' : s === 'attention' ? 'danger' : 'medium') as any;

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-3xl">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Month-End Close</h2>
          <p className="text-gray-500 mt-1">Guided checklist computed from your live books — close only when ready</p>
        </div>

        <Card>
          <CardHeader><CardTitle>Status</CardTitle></CardHeader>
          <CardContent>
            {close.loading ? <PageLoading /> : close.error ? <ErrorState message={close.error} onRetry={close.reload} /> : (
              <div className="space-y-2 text-sm">
                {Object.entries(close.data?.checks || {}).map(([k, v]) => (
                  <p key={k} className="flex justify-between border-b border-gray-100 py-2">
                    <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                    <Badge variant={variant(String(v))}>{label[String(v)] || String(v)}</Badge>
                  </p>
                ))}
                <div className="grid grid-cols-2 gap-2 pt-2 text-gray-600">
                  {Object.entries(close.data?.counts || {}).map(([k, v]) => (
                    <p key={k}>{k.replace(/_/g, ' ')}: <strong className="text-gray-900">{String(v)}</strong></p>
                  ))}
                </div>
                <p className="pt-2 font-medium" role="status">{close.data?.message}</p>
                <p className="text-gray-500 text-xs">Closing is advisory in this release: resolve the items above (or explicitly override in your books) before treating the month as closed. A formal close-with-lock ships with the audit workflow.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
