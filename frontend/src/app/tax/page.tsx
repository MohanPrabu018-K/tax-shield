'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function TaxPage() {
  const [regime, setRegime] = useState('old');
  const [detail, setDetail] = useState<any>(null);
  const [planning, setPlanning] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gain, setGain] = useState({ purchase_value: '', sale_value: '', asset_type: 'mutual_fund', buy_date: '2022-05-01', sell_date: '2024-11-10' });
  const [gainResult, setGainResult] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [d, p] = await Promise.all([api.getTaxDetail(regime), api.getPlanning(regime)]);
      setDetail(d);
      setPlanning(p);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load tax workspace');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [regime]);

  const computeGain = async () => {
    try {
      setGainResult(await api.computeGain({
        purchase_value: parseFloat(gain.purchase_value),
        sale_value: parseFloat(gain.sale_value),
        asset_type: gain.asset_type, buy_date: gain.buy_date, sell_date: gain.sell_date,
      }));
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Gain computation failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Income Tax</h2>
            <p className="text-gray-500 mt-1">Every number comes from the deterministic engine — frontend never calculates tax</p>
          </div>
          <Select label="" value={regime} onChange={(e) => setRegime(e.target.value)} options={[
            { value: 'old', label: 'Old regime' },
            { value: 'new', label: 'New regime' },
          ]} className="w-40" />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Tax position ({regime})</CardTitle></CardHeader>
            <CardContent>
              {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} /> : detail ? (
                <div className="text-sm space-y-1">
                  {[
                    ['Taxable income', detail.taxable_income],
                    ['Base tax', detail.base],
                    ['87A rebate', detail.rebate],
                    ['Surcharge', detail.surcharge],
                    ['Cess (4%)', detail.cess],
                    ['Estimated liability', detail.total_liability],
                    ['Tax paid', detail.tax_paid],
                    ['Outstanding', detail.outstanding_tax],
                  ].map(([k, v]) => (
                    <p key={k as string} className="flex justify-between border-b border-gray-100 py-1">
                      <span>{k}</span><strong>{formatCurrency(v as number)}</strong>
                    </p>
                  ))}
                  <details className="pt-2">
                    <summary className="cursor-pointer text-primary-700 font-medium">View calculation details</summary>
                    <p className="text-gray-500 mt-1">Slab tables + 87A + surcharge + 4% cess from the versioned rule registry. Period FY 2024-25. See backend rule v1 (checksum-tracked).</p>
                  </details>
                </div>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Tax planning — explained opportunities</CardTitle></CardHeader>
            <CardContent>
              {(planning?.opportunities || []).length === 0 ? (
                <EmptyState title="No opportunities right now" body="Planning only surfaces rule-backed, evidence-gated savings. Nothing invented." />
              ) : (
                <div className="space-y-3">
                  {(planning?.opportunities || []).map((o: any, i: number) => (
                    <div key={i} className="border border-gray-100 rounded-lg p-3 text-sm">
                      <p className="font-medium">{o.title}</p>
                      <p>Estimated impact: <strong>{formatCurrency(o.estimated_impact)}</strong></p>
                      <p className="text-gray-500">Why: {o.requirement}</p>
                      <p className="text-gray-500">Required evidence: {o.required_evidence}</p>
                      <p className="text-gray-500">Source: {o.rule}</p>
                    </div>
                  ))}
                  <p className="text-xs text-gray-400">{planning?.disclaimer}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Capital gains estimator</CardTitle></CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-3 gap-3">
              <Input label="Purchase value (₹)" type="number" value={gain.purchase_value} onChange={(e) => setGain({ ...gain, purchase_value: e.target.value })} />
              <Input label="Sale value (₹)" type="number" value={gain.sale_value} onChange={(e) => setGain({ ...gain, sale_value: e.target.value })} />
              <Select label="Asset" value={gain.asset_type} onChange={(e) => setGain({ ...gain, asset_type: e.target.value })} options={[
                { value: 'mutual_fund', label: 'Mutual fund / equity' },
                { value: 'stocks', label: 'Stocks' },
                { value: 'property', label: 'Property' },
                { value: 'other', label: 'Other' },
              ]} />
              <Input label="Buy date" type="date" value={gain.buy_date} onChange={(e) => setGain({ ...gain, buy_date: e.target.value })} />
              <Input label="Sell date" type="date" value={gain.sell_date} onChange={(e) => setGain({ ...gain, sell_date: e.target.value })} />
              <div className="flex items-end"><Button variant="secondary" onClick={computeGain}>Compute</Button></div>
            </div>
            {gainResult && (
              <p className="mt-3 text-sm" role="status">
                Gain <strong>{formatCurrency(gainResult.gain)}</strong> · {gainResult.classification} · {gainResult.holding}. {gainResult.note}
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
