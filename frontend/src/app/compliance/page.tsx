'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { useAsync } from '@/lib/useApi';
import { api } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import Link from 'next/link';

export default function CompliancePage() {
  const obligations = useAsync(() => api.getObligations());
  const deadlines = useAsync(() => api.getDeadlines());

  const now = new Date();
  const groups = (items: any[]) => {
    const urgent = items.filter((d) => new Date(d.due_date) < now && !d.is_completed);
    const soon = items.filter((d) => {
      const t = new Date(d.due_date).getTime() - now.getTime();
      return t >= 0 && t < 14 * 864e5 && !d.is_completed;
    });
    const upcoming = items.filter((d) => new Date(d.due_date).getTime() - now.getTime() >= 14 * 864e5 && !d.is_completed);
    const done = items.filter((d) => d.is_completed);
    return { urgent, soon, upcoming, done };
  };

  const renderDeadline = (d: any) => (
    <div key={d.id} className="border border-gray-100 rounded-lg p-3 text-sm">
      <p className="font-medium">{d.title}</p>
      <p className="text-gray-500">{d.description}</p>
      <p className="text-gray-500 mt-1">
        Due {formatDate(d.due_date)}
        {d.estimated_payment ? ` · ${formatCurrency(d.estimated_payment)}` : ''}
        {(d.required_documents || []).length > 0 && ` · Needs: ${d.required_documents.slice(0, 3).join(', ')}`}
      </p>
    </div>
  );

  const g = deadlines.data ? groups(deadlines.data) : null;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Compliance Center</h2>
          <p className="text-gray-500 mt-1">Every deadline is generated from versioned rules — never a hardcoded list</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Obligations ({(obligations.data || []).length})</CardTitle></CardHeader>
            <CardContent>
              {obligations.loading ? <PageLoading /> : obligations.error ? <ErrorState message={obligations.error} onRetry={obligations.reload} />
              : (obligations.data || []).length === 0 ? <EmptyState title="No obligations" body="Obligations are detected automatically from your data." />
              : (
                <div className="space-y-2">
                  {(obligations.data || []).slice(0, 10).map((o: any) => (
                    <div key={o.id} className="text-sm border-b border-gray-100 pb-2">
                      <p className="font-medium">{o.title} <Badge variant={o.risk_level === 'high' ? 'danger' : o.risk_level === 'medium' ? 'warning' : 'success'}>{o.risk_level}</Badge></p>
                      <p className="text-gray-500">{o.recommended_action}</p>
                    </div>
                  ))}
                  <Link href="/obligations" className="text-sm font-medium text-primary-700 hover:underline">Manage all →</Link>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Deadlines by urgency</CardTitle></CardHeader>
            <CardContent>
              {deadlines.loading ? <PageLoading /> : deadlines.error ? <ErrorState message={deadlines.error} onRetry={deadlines.reload} />
              : !g ? null : (
                <div className="space-y-4">
                  {([['URGENT', g.urgent, 'danger'], ['DUE SOON', g.soon, 'medium'], ['UPCOMING', g.upcoming, 'info'], ['COMPLETED', g.done, 'success']] as const).map(([label, list, variant]) => (
                    <div key={label}>
                      <p className="text-xs font-semibold text-gray-500 mb-2"><Badge variant={variant}>{label} · {list.length}</Badge></p>
                      <div className="space-y-2">{list.slice(0, 5).map(renderDeadline)}</div>
                    </div>
                  ))}
                  <Link href="/deadlines" className="text-sm font-medium text-primary-700 hover:underline">Manage all →</Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
