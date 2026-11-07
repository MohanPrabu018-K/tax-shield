'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { PageLoading, ErrorState } from '@/components/ui/State';
import { useAsync } from '@/lib/useApi';
import { api } from '@/lib/api';
import { useState } from 'react';
import toast from 'react-hot-toast';

const PLAIN: Record<string, string> = {
  sales: 'Sales invoiced this month',
  uncategorised: 'Money movements without a category',
  documents: 'Documents missing or unverified',
  reconciliation: 'Transactions not matched to source',
  high_value_evidence: 'High-value items without a supporting document',
};

export default function ClosePage() {
  const close = useAsync(() => api.getMonthEndClose());
  const [closing, setClosing] = useState(false);

  const steps: any[] = close.data?.steps || [];
  const done = steps.filter((s) => s.status === 'ok').length;
  const pct = steps.length ? Math.round((done / steps.length) * 100) : 0;

  const complete = async () => {
    setClosing(true);
    try {
      const r: any = await api.closeMonthEnd();
      toast.success(`Month ${r.period} closed`);
      close.reload();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Could not close month');
    } finally {
      setClosing(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-3xl">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Month-End Close</h2>
          <p className="text-gray-500 mt-1">Guided checklist computed from your live books — close only when ready</p>
        </div>

        <Card>
          <CardHeader><CardTitle>Month-End Readiness</CardTitle></CardHeader>
          <CardContent>
            {close.loading ? <PageLoading /> : close.error ? <ErrorState message={close.error} onRetry={close.reload} /> : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-4xl font-bold text-primary-600">{pct}%</p>
                  <Badge variant={pct === 100 ? 'success' : 'medium'}>{pct === 100 ? 'Ready' : 'In progress'}</Badge>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: `${pct}%` }} />
                </div>

                <div className="space-y-2">
                  {steps.map((s, i) => (
                    <div key={s.key} className="flex items-center justify-between border-b border-gray-100 py-2">
                      <div>
                        <p className="font-medium text-gray-900">Step {i + 1} — {PLAIN[s.key] || s.label}</p>
                        <p className="text-xs text-gray-500">{s.status === 'ok' ? 'Complete' : 'Action required'}</p>
                      </div>
                      <Badge variant={s.status === 'ok' ? 'success' : 'danger'}>{s.status === 'ok' ? '✓' : '⚠'}</Badge>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  {Object.entries(close.data?.counts || {}).map(([k, v]) => (
                    <p key={k}>{k.replace(/_/g, ' ')}: <strong className="text-gray-900">{String(v)}</strong></p>
                  ))}
                </div>

                <p className="font-medium" role="status">{close.data?.message}</p>

                <div className="flex gap-2 pt-2">
                  <Button onClick={complete} disabled={closing}>{closing ? 'Closing…' : 'Complete Month-End'}</Button>
                </div>
                <p className="text-gray-500 text-xs">Closing records your review in the system. Deterministic checks are recomputed on every load; a formal close-with-lock ships with the audit workflow.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
