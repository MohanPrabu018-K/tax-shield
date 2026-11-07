'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { getWorkspace } from '@/lib/workspace';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { ReadinessScoreGauge } from '@/components/charts/ReadinessScoreGauge';
import { IncomeBreakdownChart } from '@/components/charts/IncomeBreakdownChart';
import { formatCurrency } from '@/lib/utils';
import {
  Plus, FileText, Upload, Users, Receipt, AlertTriangle, TrendingUp, Wallet,
} from 'lucide-react';
import toast from 'react-hot-toast';

const QUICK_ACTIONS = [
  { name: 'Add Transaction', href: '/transactions?action=new', icon: Plus },
  { name: 'Create Invoice', href: '/invoices?action=new', icon: FileText },
  { name: 'Upload Document', href: '/documents?action=upload', icon: Upload },
  { name: 'Add Customer', href: '/customers?action=new', icon: Users },
  { name: 'Record Payment', href: '/receivables', icon: Wallet },
  { name: 'View Tax', href: '/tax', icon: Receipt },
  { name: 'View GST', href: '/gst', icon: Receipt },
  { name: 'Compliance', href: '/compliance', icon: AlertTriangle },
];

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summary, readiness, attention, overdue, rp, health] = await Promise.all([
        api.getDashboard(),
        api.getReadinessScore(),
        api.getAttention(),
        api.getOverdueInvoices(),
        api.getReceivablesPayables(),
        api.getHealth('2024-25'),
      ]);
      setData({ summary, readiness, attention, overdue, rp, health });
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user && !authLoading) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, authLoading]);

  const seedDemo = async () => {
    try {
      await api.seedDemoData();
      toast.success('Demo data loaded');
      load();
    } catch {
      toast.error('Failed to load demo data');
    }
  };

  if (authLoading || loading) {
    return <DashboardLayout><PageLoading label="Loading your financial overview…" /></DashboardLayout>;
  }
  if (error) {
    return <DashboardLayout><ErrorState message={error} onRetry={load} /></DashboardLayout>;
  }

  const { summary, readiness, attention, overdue, rp, health } = data;
  const profile = getWorkspace();
  const greeting = profile?.businessName ? `Good day, ${profile.businessName}` : 'Good day';
  const attentionCount =
    (attention?.high_risk?.length || 0) + (attention?.missing_documents?.length || 0) + (overdue?.overdue?.length || 0);

  const stats = [
    { label: 'Revenue', value: formatCurrency(summary.total_income || 0) },
    { label: 'Taxable Income', value: formatCurrency(summary.taxable_income || 0) },
    { label: 'Estimated Tax Due', value: formatCurrency(summary.estimated_liability || 0) },
    { label: 'Tax Paid', value: formatCurrency(summary.tax_paid || 0) },
    { label: 'Outstanding Tax', value: formatCurrency(summary.outstanding_tax || 0) },
    { label: 'Money Owed to You', value: formatCurrency(rp?.receivable?.total || 0) },
    { label: 'Bills You Owe', value: formatCurrency(rp?.payable?.total || 0) },
    { label: 'Overdue Invoices', value: formatCurrency(overdue?.total || 0) },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{greeting}</h2>
            <p className="text-sm text-gray-500">
              Overall Financial Health: <strong className="text-gray-900">{health?.score ?? '—'}/100</strong>
              {health?.negative?.length > 0 && ` · ${health.negative.join('; ')}`}
            </p>
          </div>
          <Button variant="secondary" onClick={seedDemo}>Load Demo Data</Button>
        </div>

        <section aria-label="Key figures">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats.map((s) => (
              <Card key={s.label}>
                <CardContent>
                  <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{s.label}</p>
                  <p className="mt-1 text-xl font-bold text-gray-900">{s.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section aria-label="Quick actions">
          <Card>
            <CardHeader><CardTitle>Quick actions</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {QUICK_ACTIONS.map((a) => (
                  <Link
                    key={a.name}
                    href={a.href}
                    className="flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300"
                  >
                    <a.icon className="h-4 w-4 text-primary-600" aria-hidden="true" />
                    {a.name}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>

        <section aria-label="What needs attention">
          <Card>
            <CardHeader>
              <CardTitle>What needs attention {attentionCount > 0 && <Badge variant="danger">{attentionCount}</Badge>}</CardTitle>
            </CardHeader>
            <CardContent>
              {attentionCount === 0 ? (
                <EmptyState title="All clear" body="No urgent items. Your books, documents and compliance look healthy." />
              ) : (
                <ul className="space-y-2 text-sm">
                  {(attention?.high_risk || []).slice(0, 5).map((t: string) => (
                    <li key={t} className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-red-500 flex-shrink-0" aria-hidden="true" />
                      <Link href="/obligations" className="text-gray-800 hover:underline">{t}</Link>
                      <Badge variant="high">high risk</Badge>
                    </li>
                  ))}
                  {(overdue?.overdue || []).slice(0, 5).map((o: any) => (
                    <li key={o.number} className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-yellow-600 flex-shrink-0" aria-hidden="true" />
                      <Link href="/receivables" className="text-gray-800 hover:underline">
                        {o.number} · {o.customer} · {formatCurrency(o.balance)} due {o.due_date?.slice(0, 10)}
                      </Link>
                      <Badge variant="medium">overdue</Badge>
                    </li>
                  ))}
                  {(attention?.missing_documents || []).slice(0, 5).map((t: string) => (
                    <li key={t} className="flex items-center gap-2">
                      <Upload className="h-4 w-4 text-blue-500 flex-shrink-0" aria-hidden="true" />
                      <Link href="/documents" className="text-gray-800 hover:underline">{t}</Link>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </section>

        <section className="grid md:grid-cols-2 gap-6" aria-label="Readiness and income">
          <Card>
            <CardHeader><CardTitle>Tax Readiness · {readiness?.score ?? '—'}/100</CardTitle></CardHeader>
            <CardContent>
              {readiness ? <ReadinessScoreGauge score={readiness.score} /> : <EmptyState title="No score yet" body="Add transactions to compute readiness." />}
              {readiness?.explanation && <p className="mt-2 text-sm text-gray-600">{readiness.explanation}</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Income breakdown</CardTitle></CardHeader>
            <CardContent>
              {summary?.income_breakdown && Object.keys(summary.income_breakdown).length > 0 ? (
                <IncomeBreakdownChart data={summary.income_breakdown} />
              ) : (
                <EmptyState title="No income yet" body="Record income or load demo data to see the breakdown." />
              )}
            </CardContent>
          </Card>
        </section>

        <section aria-label="Cash and trends">
          <Card>
            <CardHeader><CardTitle>Cash position & trends</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" aria-hidden="true" />
                Receivables {formatCurrency(rp?.receivable?.total || 0)} · Overdue {formatCurrency(rp?.overdue_receivable || 0)} ·
                Payables {formatCurrency(rp?.payable?.total || 0)} · Overdue {formatCurrency(rp?.overdue_payable || 0)}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link href="/intelligence" className="text-sm font-medium text-primary-700 hover:underline">What changed →</Link>
                <Link href="/intelligence" className="text-sm font-medium text-primary-700 hover:underline">Cash flow forecast →</Link>
                <Link href="/tax" className="text-sm font-medium text-primary-700 hover:underline">Why did my tax change? →</Link>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </DashboardLayout>
  );
}
