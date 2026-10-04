'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function TdsPage() {
  const [sections, setSections] = useState<any[]>([]);
  const [records, setRecords] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [section, setSection] = useState('194J');
  const [amount, setAmount] = useState('');
  const [pan, setPan] = useState(true);
  const [result, setResult] = useState<any>(null);
  const [deductee, setDeductee] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, r, sum] = await Promise.all([
        api.getTdsSections(),
        api.getTdsRecords(),
        api.getTdsSummary(),
      ]);
      setSections(s.sections || []);
      setRecords(r || []);
      setSummary(sum);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load TDS data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const compute = async () => {
    try {
      const r = await api.computeTds(section, parseFloat(amount), pan);
      setResult(r);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Computation failed');
    }
  };

  const record = async () => {
    if (!result?.applicable) {
      toast.error('Nothing to record — TDS not applicable');
      return;
    }
    try {
      await api.createTdsRecord({
        section, amount: parseFloat(amount), pan_available: pan, deductee,
      });
      toast.success('TDS recorded as payable');
      setResult(null);
      setAmount('');
      load();
    } catch {
      toast.error('Record failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">TDS Workspace</h2>
          <p className="text-gray-500 mt-1">Section-wise applicability from deterministic rules</p>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {[
            ['Payable', summary?.payable],
            ['Paid', summary?.paid],
            ['Records', summary?.count],
          ].map(([k, v]) => (
            <Card key={k as string}><CardContent>
              <p className="text-xs uppercase text-gray-500">{k}</p>
              <p className="text-xl font-bold">{k === 'Records' ? v ?? '—' : formatCurrency(v || 0)}</p>
            </CardContent></Card>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Applicability calculator</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Select label="Section" value={section} onChange={(e) => setSection(e.target.value)} options={sections.map((s) => ({ value: s.code, label: `${s.code} · ${s.label} · ${s.rate}% ≥ ₹${s.threshold.toLocaleString('en-IN')}` }))} />
                <Input label="Amount (₹)" type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} />
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input type="checkbox" checked={pan} onChange={(e) => setPan(e.target.checked)} className="h-4 w-4" />
                  Deductee PAN available (else 20% applies)
                </label>
                <Input label="Deductee (for recording)" value={deductee} onChange={(e) => setDeductee(e.target.value)} placeholder="Name" />
                <div className="flex gap-2">
                  <Button variant="secondary" onClick={compute} disabled={!amount}>Compute</Button>
                  <Button onClick={record} disabled={!result}>Record payable</Button>
                </div>
                {result && (
                  <p className="text-sm" role="status">
                    {result.applicable
                      ? `Deduct ${formatCurrency(result.tds)} at ${result.rate}% under ${result.section}. ${result.note}`
                      : `Not applicable. ${result.note}`}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>TDS records ({records.length})</CardTitle></CardHeader>
            <CardContent className="p-0">
              {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
              : records.length === 0 ? <EmptyState title="No TDS records" body="Compute applicability and record what you deduct." />
              : (
                <Table>
                  <TableHeader><TableRow><TableHead>Deductee</TableHead><TableHead>Section</TableHead><TableHead className="text-right">TDS</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {records.slice(0, 20).map((r: any) => (
                      <TableRow key={r.id}>
                        <TableCell>{r.deductee || '—'}</TableCell>
                        <TableCell className="font-mono text-xs">{r.section} · {r.rate}%</TableCell>
                        <TableCell className="text-right">{formatCurrency(r.tds)}</TableCell>
                        <TableCell>{r.status}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
