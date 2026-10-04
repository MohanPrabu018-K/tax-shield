'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { useAsync } from '@/lib/useApi';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export default function AisPage() {
  const recon = useAsync(() => api.getReconciliation());
  const tdsStatus = useAsync(async () => {
    const r = await api.getReconciliation();
    return { tds_internal: r.tds_internal, tds_26as: r.tds_26as, tds_difference: r.tds_difference, tds_status: r.tds_status };
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AIS / Form 26AS</h2>
          <p className="text-gray-500 mt-1">Every item shows TaxShield record vs source record, difference and action</p>
        </div>

        <Card>
          <CardHeader><CardTitle>Income matching</CardTitle></CardHeader>
          <CardContent>
            {recon.loading ? <PageLoading /> : recon.error ? <ErrorState message={recon.error} onRetry={recon.reload} />
            : !recon.data?.items?.length ? <EmptyState title="No AIS records" body="Add AIS records via API or demo data to compare against your books." />
            : (
              <div className="space-y-3">
                {(recon.data.items || []).map((it: any, i: number) => (
                  <div key={i} className="border border-gray-100 rounded-lg p-3 text-sm">
                    <p className="font-medium">{it.source} · {it.income_type} · <Badge variant={it.status === 'matched' ? 'success' : it.status === 'missing' ? 'danger' : 'medium'}>{it.status}</Badge></p>
                    <div className="grid sm:grid-cols-3 gap-2 mt-2 text-gray-600">
                      <p>TaxShield: <strong className="text-gray-900">{formatCurrency(it.internal_match)}</strong></p>
                      <p>Source (AIS): <strong className="text-gray-900">{formatCurrency(it.ais_amount)}</strong></p>
                      <p>Difference: <strong className="text-gray-900">{formatCurrency(it.difference)}</strong></p>
                    </div>
                    <p className="text-gray-500 mt-1">Suggested action: {it.action}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>TDS credit (26AS)</CardTitle></CardHeader>
          <CardContent>
            {tdsStatus.loading ? <PageLoading /> : tdsStatus.data ? (
              <p className="text-sm">
                Books TDS <strong>{formatCurrency(tdsStatus.data.tds_internal)}</strong> · 26AS TDS <strong>{formatCurrency(tdsStatus.data.tds_26as)}</strong> ·
                Diff <strong>{formatCurrency(tdsStatus.data.tds_difference)}</strong> · <Badge variant={tdsStatus.data.tds_status === 'matched' ? 'success' : 'danger'}>{tdsStatus.data.tds_status}</Badge>
              </p>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
