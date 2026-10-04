'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Badge } from '@/components/ui/Badge';
import { useAsync } from '@/lib/useApi';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function IntelligencePage() {
  const anomalies = useAsync(() => api.getAnomalies());
  const health = useAsync(() => api.getHealth('2024-25'));
  const [opening, setOpening] = useState('100000');
  const [recv, setRecv] = useState('80000');
  const [pay, setPay] = useState('40000');
  const [tax, setTax] = useState('15000');
  const [recurring, setRecurring] = useState('25000');
  const [forecast, setForecast] = useState<any>(null);

  const runForecast = async () => {
    try {
      setForecast(await api.forecastCash({
        opening: parseFloat(opening), receivables_30: parseFloat(recv),
        payables_30: parseFloat(pay), tax_due_30: parseFloat(tax),
        recurring_30: parseFloat(recurring), months: 3,
      }));
    } catch {
      toast.error('Forecast failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Business Intelligence</h2>
          <p className="text-gray-500 mt-1">Rule-based, reproducible — forecasts always show assumptions</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Financial health {health.data && `· ${health.data.score}/100`}</CardTitle></CardHeader>
            <CardContent>
              {health.loading ? <PageLoading /> : health.error ? <ErrorState message={health.error} onRetry={health.reload} /> : (
                <div className="text-sm space-y-1">
                  <p className="text-gray-500">Basis: {health.data?.basis}</p>
                  {(health.data?.negative || []).length === 0
                    ? <p className="text-green-700 font-medium">All factors positive.</p>
                    : health.data.negative.map((n: string) => <p key={n}>⚠ {n}</p>)}
                  <p className="text-xs text-gray-400">Period {health.data?.tax_period} · {health.data?.timestamp?.slice(0, 10)}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Anomalies ({anomalies.data?.count ?? 0})</CardTitle></CardHeader>
            <CardContent>
              {anomalies.loading ? <PageLoading /> : anomalies.error ? <ErrorState message={anomalies.error} onRetry={anomalies.reload} />
              : (anomalies.data?.flags || []).length === 0 ? <EmptyState title="No anomalies" body="Duplicate and high-value checks are clean." />
              : (
                <ul className="space-y-2 text-sm">
                  {(anomalies.data.flags || []).slice(0, 10).map((f: any, i: number) => (
                    <li key={i}><Badge variant="medium">{f.type}</Badge> <span className="text-gray-600">{f.detail}</span></li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Cash-flow forecast (30 / 60 / 90 days)</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              <Input label="Opening (₹)" type="number" value={opening} onChange={(e) => setOpening(e.target.value)} />
              <Input label="Receivables (₹)" type="number" value={recv} onChange={(e) => setRecv(e.target.value)} />
              <Input label="Payables (₹)" type="number" value={pay} onChange={(e) => setPay(e.target.value)} />
              <Input label="Tax due (₹)" type="number" value={tax} onChange={(e) => setTax(e.target.value)} />
              <Input label="Recurring (₹)" type="number" value={recurring} onChange={(e) => setRecurring(e.target.value)} />
            </div>
            <Button variant="secondary" onClick={runForecast} className="mt-3">Project</Button>
            {forecast && (
              <div className="mt-3 text-sm">
                {(forecast.projection || []).map((p: any) => (
                  <p key={p.month} className="flex justify-between border-b border-gray-100 py-1">
                    <span>Month {p.month}</span><strong>{formatCurrency(p.projected_balance)}</strong>
                  </p>
                ))}
                <p className="text-xs text-gray-400 mt-2">
                  Assumptions: {forecast.assumptions?.method}, monthly net {formatCurrency(forecast.assumptions?.monthly_net)}. {forecast.assumptions?.guarantee}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
