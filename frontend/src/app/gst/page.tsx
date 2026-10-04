'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function GstPage() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gstin, setGstin] = useState('');
  const [gstinResult, setGstinResult] = useState<any>(null);
  const [books, setBooks] = useState('');
  const [portal, setPortal] = useState('');
  const [recon, setRecon] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setSummary(await api.getGstSummary());
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load GST summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const validate = async () => {
    try {
      setGstinResult(await api.validateGstin(gstin));
    } catch {
      toast.error('Validation failed');
    }
  };

  const reconcile = async () => {
    try {
      setRecon(await api.gstReconcile(parseFloat(books), parseFloat(portal)));
    } catch {
      toast.error('Reconciliation failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">GST Workspace</h2>
          <p className="text-gray-500 mt-1">Deterministic summaries for review — preparation, never filing</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>GSTR-1 · Outward supplies</CardTitle></CardHeader>
            <CardContent>
              {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
              : !summary ? <EmptyState title="No data" body="Create sale invoices to prepare GSTR-1." />
              : (
                <div className="text-sm space-y-1">
                  {(summary.gstr1?.by_rate || []).map((b: any) => (
                    <p key={b.rate} className="flex justify-between border-b border-gray-100 py-1">
                      <span>{b.rate}% · {b.count} lines · taxable {formatCurrency(b.taxable)}</span>
                      <strong>{formatCurrency(b.cgst + b.sgst + b.igst)}</strong>
                    </p>
                  ))}
                  <p className="flex justify-between pt-2"><span>Total output tax</span><strong>{formatCurrency(summary.gstr1?.total_tax)}</strong></p>
                  <p className="text-gray-500">{summary.gstr1?.disclaimer}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>GSTR-3B · Payment summary</CardTitle></CardHeader>
            <CardContent>
              {summary && (
                <div className="text-sm space-y-1">
                  <p className="flex justify-between border-b border-gray-100 py-1"><span>Output tax</span><strong>{formatCurrency(summary.gstr3b?.output_tax)}</strong></p>
                  <p className="flex justify-between border-b border-gray-100 py-1"><span>ITC available</span><strong>{formatCurrency(summary.gstr3b?.itc_available)}</strong></p>
                  <p className="flex justify-between pt-1"><span>Net payable</span><strong>{formatCurrency(summary.gstr3b?.net_payable)}</strong></p>
                  <p className="text-gray-500">{summary.gstr3b?.disclaimer}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>GSTIN validator</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input value={gstin} onChange={(e) => setGstin(e.target.value)} placeholder="27AAPFU0939F1ZV" aria-label="GSTIN" className="font-mono" />
                <Button variant="secondary" onClick={validate}>Check</Button>
              </div>
              {gstinResult && (
                <p className="mt-2 text-sm" role="status">
                  {gstinResult.valid
                    ? `Valid ✓ · state ${gstinResult.state_code} · PAN ${gstinResult.pan}`
                    : `Invalid ✗ · ${gstinResult.reason}. Verify against the GST portal — checksum passing never proves registration.`}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Books ↔ portal reconciliation</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input type="number" step="0.01" value={books} onChange={(e) => setBooks(e.target.value)} placeholder="Books tax" aria-label="Books tax" />
                <Input type="number" step="0.01" value={portal} onChange={(e) => setPortal(e.target.value)} placeholder="Portal tax" aria-label="Portal tax" />
                <Button variant="secondary" onClick={reconcile}>Compare</Button>
              </div>
              {recon && (
                <p className="mt-2 text-sm" role="status">
                  {recon.status === 'matched' ? 'Matched ✓. ' : `Mismatched: diff ${formatCurrency(recon.difference)}. `}
                  {recon.action}
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
