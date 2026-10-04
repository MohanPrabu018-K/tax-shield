'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Modal } from '@/components/ui/Modal';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency } from '@/lib/utils';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

const BLANK_ITEM = { desc: '', hsn: '', qty: 1, rate: 0, discount_pct: 0, gst_rate: 18 };

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [kind, setKind] = useState('sale');
  const [customer, setCustomer] = useState('');
  const [dueDate, setDueDate] = useState(new Date().toISOString().split('T')[0]);
  const [interState, setInterState] = useState(false);
  const [items, setItems] = useState<any[]>([{ ...BLANK_ITEM }]);
  const [detail, setDetail] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setInvoices(await api.getInvoices());
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    if (typeof window !== 'undefined' && window.location.search.includes('action=new')) setShowModal(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setItem = (i: number, patch: any) =>
    setItems((list) => list.map((it, j) => (j === i ? { ...it, ...patch } : it)));

  const preview = () => {
    let taxable = 0, tax = 0;
    items.forEach((it) => {
      const t = it.qty * it.rate * (1 - (it.discount_pct || 0) / 100);
      taxable += t;
      tax += t * (it.gst_rate || 0) / 100;
    });
    return { taxable: Math.round(taxable * 100) / 100, tax: Math.round(tax * 100) / 100, grand: Math.round((taxable + tax) * 100) / 100 };
  };

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const clean = items.filter((it) => it.desc && it.qty > 0);
      if (clean.length === 0) {
        toast.error('Add at least one item');
        return;
      }
      const created = await api.createInvoice({
        kind, customer_name: customer || 'Walk-in', due_date: dueDate,
        items: clean.map((it) => ({ ...it, qty: Number(it.qty), rate: Number(it.rate), discount_pct: Number(it.discount_pct || 0), gst_rate: Number(it.gst_rate || 0) })),
        inter_state: interState,
      });
      toast.success(`Invoice ${created.number} created`);
      setShowModal(false);
      setItems([{ ...BLANK_ITEM }]);
      setCustomer('');
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Failed to create invoice');
    }
  };

  const transition = async (id: string, to: string) => {
    try {
      await api.transitionInvoice(id, to);
      toast.success(`Marked ${to}`);
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Transition failed');
    }
  };

  const p = preview();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Invoices</h2>
            <p className="text-gray-500 mt-1">GST-aware totals are computed by the backend rule engine</p>
          </div>
          <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-2" />Create Invoice</Button>
        </div>

        <Card>
          <CardHeader><CardTitle>All invoices ({invoices.length})</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
            : invoices.length === 0 ? (
              <EmptyState title="No invoices yet" body="Create your first GST invoice — totals, lifecycle and accounting post automatically." action={<Button onClick={() => setShowModal(true)}>Create Invoice</Button>} />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Number</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Due</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                    <TableHead className="text-right">Balance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invoices.map((i: any) => (
                    <TableRow key={i.id}>
                      <TableCell>
                        <button className="font-medium text-primary-700 hover:underline" onClick={() => setDetail(i)}>{i.number}</button>
                        <p className="text-xs text-gray-500">{i.kind}</p>
                      </TableCell>
                      <TableCell>{i.customer_name || '—'}</TableCell>
                      <TableCell>{String(i.due_date).slice(0, 10)}</TableCell>
                      <TableCell><Badge variant={i.status === 'paid' ? 'success' : i.status === 'overdue' ? 'danger' : 'medium'}>{i.status}</Badge></TableCell>
                      <TableCell className="text-right">{formatCurrency(i.grand_total)}</TableCell>
                      <TableCell className="text-right font-medium">{formatCurrency(i.balance)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create Invoice" size="xl">
          <form onSubmit={create} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <Select label="Type" value={kind} onChange={(e) => setKind(e.target.value)} options={[
                { value: 'sale', label: 'Sale invoice' },
                { value: 'purchase', label: 'Purchase bill' },
              ]} />
              <Input label="Customer / vendor" value={customer} onChange={(e) => setCustomer(e.target.value)} placeholder="Customer name" />
              <Input label="Due date" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
              <label className="flex items-center gap-2 text-sm text-gray-700 mt-6">
                <input type="checkbox" checked={interState} onChange={(e) => setInterState(e.target.checked)} className="h-4 w-4" />
                Inter-state supply (IGST instead of CGST+SGST)
              </label>
            </div>
            {items.map((it, i) => (
              <div key={i} className="grid grid-cols-2 sm:grid-cols-6 gap-2 border border-gray-100 rounded-lg p-3">
                <Input label="Description" value={it.desc} onChange={(e) => setItem(i, { desc: e.target.value })} className="col-span-2" />
                <Input label="HSN" value={it.hsn} onChange={(e) => setItem(i, { hsn: e.target.value })} />
                <Input label="Qty" type="number" step="0.01" value={it.qty} onChange={(e) => setItem(i, { qty: e.target.value })} />
                <Input label="Rate (₹)" type="number" step="0.01" value={it.rate} onChange={(e) => setItem(i, { rate: e.target.value })} />
                <Input label="GST %" type="number" step="0.01" value={it.gst_rate} onChange={(e) => setItem(i, { gst_rate: e.target.value })} />
              </div>
            ))}
            <Button variant="secondary" type="button" onClick={() => setItems([...items, { ...BLANK_ITEM }])}>Add item</Button>
            <p className="text-sm text-gray-700" aria-live="polite">
              Taxable {formatCurrency(p.taxable)} · Tax {formatCurrency(p.tax)} · <strong>Total {formatCurrency(p.grand)}</strong>
            </p>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setShowModal(false)}>Cancel</Button>
              <Button type="submit">Create</Button>
            </div>
          </form>
        </Modal>

        <Modal isOpen={!!detail} onClose={() => setDetail(null)} title={detail ? `Invoice ${detail.number}` : ''} size="lg">
          {detail && (
            <div className="space-y-3 text-sm">
              <p>Status <Badge variant={detail.status === 'paid' ? 'success' : 'medium'}>{detail.status}</Badge></p>
              <p>Taxable {formatCurrency(detail.taxable_value)} · Tax {formatCurrency(detail.total_tax)} · <strong>Total {formatCurrency(detail.grand_total)}</strong> · Paid {formatCurrency(detail.paid_total)} · Balance {formatCurrency(detail.balance)}</p>
              <div className="flex flex-wrap gap-2">
                {['sent', 'viewed', 'partially_paid', 'paid', 'overdue', 'cancelled'].filter((s) => s !== detail.status).map((s) => (
                  <Button key={s} variant="secondary" size="sm" onClick={() => { transition(detail.id, s); setDetail(null); }}>
                    Mark {s}
                  </Button>
                ))}
              </div>
              <p className="text-gray-500">Lifecycle: Draft → Sent → Viewed → Partially Paid → Paid (or Overdue). Illegal jumps are rejected by the backend.</p>
            </div>
          )}
        </Modal>
      </div>
    </DashboardLayout>
  );
}
