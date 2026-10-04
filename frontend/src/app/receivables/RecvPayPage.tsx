'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

export function RecvPayPage({ kind, title, subtitle }: { kind: 'sale' | 'purchase'; title: string; subtitle: string }) {
  const [summary, setSummary] = useState<any>(null);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paying, setPaying] = useState<any>(null);
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('manual');
  const [reference, setReference] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [rp, inv] = await Promise.all([api.getReceivablesPayables(), api.getInvoices()]);
      setSummary(rp);
      setInvoices(inv.filter((i: any) => (i.kind || 'sale') === kind && i.status !== 'paid' && i.status !== 'cancelled'));
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const record = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.payInvoice(paying.id, { amount: parseFloat(amount), method, reference });
      toast.success('Payment recorded');
      setPaying(null);
      setAmount('');
      setReference('');
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Payment failed');
    }
  };

  const bucket = kind === 'sale' ? summary?.receivable : summary?.payable;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="text-gray-500 mt-1">{subtitle}</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {bucket ? Object.entries(bucket).filter(([k]) => k !== 'total').map(([k, v]) => (
            <Card key={k}>
              <CardContent>
                <p className="text-xs uppercase text-gray-500">{k.replace('d', '').replace('_', '-')}</p>
                <p className="text-lg font-bold">{formatCurrency(v as number)}</p>
              </CardContent>
            </Card>
          )) : null}
        </div>

        <Card>
          <CardHeader><CardTitle>Open items ({invoices.length})</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
            : invoices.length === 0 ? (
              <EmptyState title="Nothing outstanding" body="All invoices are settled." />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Invoice</TableHead>
                    <TableHead>{kind === 'sale' ? 'Customer' : 'Vendor'}</TableHead>
                    <TableHead>Due</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Balance</TableHead>
                    <TableHead><span className="sr-only">Actions</span></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invoices.map((i: any) => (
                    <TableRow key={i.id}>
                      <TableCell className="font-medium">{i.number}</TableCell>
                      <TableCell>{i.customer_name || '—'}</TableCell>
                      <TableCell>{String(i.due_date).slice(0, 10)}</TableCell>
                      <TableCell><Badge variant={i.status === 'overdue' ? 'danger' : i.status === 'paid' ? 'success' : 'medium'}>{i.status}</Badge></TableCell>
                      <TableCell className="text-right font-medium">{formatCurrency(i.balance)}</TableCell>
                      <TableCell>
                        <Button variant="secondary" size="sm" onClick={() => { setPaying(i); setAmount(String(i.balance)); }}>
                          Record payment
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Modal isOpen={!!paying} onClose={() => setPaying(null)} title={`Record payment · ${paying?.number}`}>
          <form onSubmit={record} className="space-y-4">
            <Input label="Amount (₹)" type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            <Input label="Method" value={method} onChange={(e) => setMethod(e.target.value)} placeholder="manual / UPI / cash / card" />
            <Input label="Reference (UPI ref / proof)" value={reference} onChange={(e) => setReference(e.target.value)} placeholder="UPI transaction reference" />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setPaying(null)}>Cancel</Button>
              <Button type="submit">Save payment</Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
