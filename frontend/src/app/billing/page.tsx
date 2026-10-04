'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function BillingPage() {
  const [sub, setSub] = useState<any>(null);
  const [ent, setEnt] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wantPlan, setWantPlan] = useState('starter');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, e, h, p] = await Promise.all([
        api.getSubscription(), api.getEntitlement(), api.getBillingHistory(), api.getPlans(),
      ]);
      setSub(s);
      setEnt(e);
      setHistory(h.history || []);
      setPlans(p.plans || []);
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Failed to load billing');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const checkout = async () => {
    try {
      const r = await api.checkout(wantPlan, 'manual');
      toast.success(r.message || 'Subscription updated');
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Checkout failed');
    }
  };

  const trial = async () => {
    try {
      const r = await api.startTrial(wantPlan);
      toast.success(r.message);
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || err?.response?.data?.detail || 'Trial failed');
    }
  };

  const cancel = async () => {
    if (!window.confirm('Cancel subscription? Access continues until period end, then Free applies.')) return;
    try {
      await api.cancelSubscription();
      toast.success('Cancelled');
      load();
    } catch {
      toast.error('Cancellation failed');
    }
  };

  const bar = (used: number, limit: number) => {
    const pct = Math.min(100, Math.round((used / Math.max(limit, 1)) * 100));
    return (
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div className="h-full bg-primary-600" style={{ width: `${pct}%` }} />
      </div>
    );
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-4xl">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Billing</h2>
          <p className="text-gray-500 mt-1">Plan, usage, history and subscription controls — no hidden charges</p>
        </div>

        {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} /> : (
          <>
            <div className="grid sm:grid-cols-3 gap-4">
              <Card><CardContent>
                <p className="text-xs uppercase text-gray-500">Current plan</p>
                <p className="text-xl font-bold">{ent?.plan_name} <span className="text-sm font-normal text-gray-500">· {sub?.status}</span></p>
              </CardContent></Card>
              <Card><CardContent>
                <p className="text-xs uppercase text-gray-500">Trial ends</p>
                <p className="text-xl font-bold">{sub?.trial_ends_at ? String(sub.trial_ends_at).slice(0, 10) : '—'}</p>
              </CardContent></Card>
              <Card><CardContent>
                <p className="text-xs uppercase text-gray-500">Period ends</p>
                <p className="text-xl font-bold">{sub?.current_period_end ? String(sub.current_period_end).slice(0, 10) : '—'}</p>
              </CardContent></Card>
            </div>

            <Card>
              <CardHeader><CardTitle>Usage vs limits</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(ent?.limits || {}).filter(([k]) => k !== 'storage_bytes' && k !== 'assistant_per_day').map(([k, limit]) => (
                    <div key={k}>
                      <p className="text-sm flex justify-between"><span className="capitalize">{k}</span><span>{ent?.usage?.[k] ?? 0} / {(limit as number).toLocaleString('en-IN')}</span></p>
                      {bar(ent?.usage?.[k] ?? 0, limit as number)}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Change plan</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Select label="" value={wantPlan} onChange={(e) => setWantPlan(e.target.value)}
                    options={plans.filter((p) => p.id !== 'free').map((p) => ({ value: p.id, label: `${p.name} — ${p.price_inr === 0 ? 'Free' : formatCurrency(p.price_inr / 100) + '/mo'}` }))} className="sm:w-64" />
                  <Button variant="secondary" onClick={trial}>Start 14-day trial</Button>
                  <Button onClick={checkout}>Subscribe (manual activation)</Button>
                  {sub?.status !== 'CANCELLED' && sub?.plan !== 'free' && (
                    <Button variant="danger" onClick={cancel}>Cancel</Button>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-2">Manual provider: checkout creates a pending subscription a human activates — no charge is ever made automatically. Downgrade path: cancel returns you to Free at period end with data retained.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Billing history</CardTitle></CardHeader>
              <CardContent>
                {(history || []).length === 0 ? <EmptyState title="No billing events" body="Checkouts, trials and cancellations appear here." /> : (
                  <ul className="text-sm space-y-1">
                    {history.map((h: any, i: number) => (
                      <li key={i} className="border-b border-gray-100 py-1">{h.event}{h.plan ? ` · ${h.plan}` : ''} <span className="text-gray-400">· {String(h.at).slice(0, 10)}</span></li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
