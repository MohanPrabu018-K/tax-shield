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

export default function CreditNotesPage() {
  const [notes, setNotes] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [linkedInvoice, setLinkedInvoice] = useState('');
  const [reason, setReason] = useState('');
  const [customer, setCustomer] = useState('');
  const [items, setItems] = useState<any[]>([{ ...BLANK_ITEM }]);
  const [filterStatus, setFilterStatus] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setNotes(await api.getInvoices('?kind=credit_note'));
      setInvoices(await api.getInvoices());
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load credit notes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const setItem = (i: number, patch: any) =>
    setItems((list) => list.map((it, j) => (j === i ? { ...it, ...patch } : it)));

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const clean = items.filter((it) => it.desc && it.qty > 0);
      if (clean.length === 0) {
        toast.error('Add at least one item');
        return;
      }
      const linked = invoices.find((inv) => inv._id === linkedInvoice);
      if (!linked) {
        toast.error('Select the original invoice');
        return;
      }
      const created = await api.createCreditNote({
        customer_name: customer || linked.customer_name || 'Walk-in',
        customer_id: linked._id,
        reason,
        items: clean.map((it) => ({ ...it, qty: Number(it.qty), rate: Number(it.rate), discount_pct: Number(it.discount_pct || 0), gst_rate: Number(it.gst_rate || 0) })),
        notes: reason,
      });
      toast.success(`Credit note ${created.number} created`);
      setShowModal(false);
      setItems([{ ...BLANK_ITEM }]);
      setReason(''); setCustomer(''); setLinkedInvoice('');
      load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to create credit note');
    }
  };

  const transition = async (id: string, to: string) => {
    try {
      await api.transitionInvoice(id, to);
      toast.success(`Moved to ${to}`);
      load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Transition failed');
    }
  };

  const filtered = filterStatus ? notes.filter((n) => n.status === filterStatus) : notes;
  const linked = invoices.find((inv) => inv._id === linkedInvoice);
  const preview = () => {
    let taxable = 0, tax = 0;
    items.forEach((it) => {
      const t = it.qty * it.rate * (1 - (it.discount_pct || 0) / 100);
      taxable += t; tax += t * (it.gst_rate || 0) / 100;
    });
    return { taxable: Math.round(taxable * 100) / 100, tax: Math.round(tax * 100) / 100, grand: Math.round((taxable + tax) * 100) / 100 };
  };

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Credit Notes</h1>
        <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-1" /> New Credit Note</Button>
      </div>
      <div className="mb-4 flex gap-2">
        {['', 'draft', 'sent', 'paid', 'cancelled'].map((s) => (
          <Button key={s} variant={filterStatus === s ? 'primary' : 'secondary'} onClick={() => setFilterStatus(s)}>{s || 'All'}</Button>
        ))}
      </div>
      {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} /> : filtered.length === 0 ? (
        <EmptyState title="No credit notes" body="Create a credit note from an invoice to reduce what a customer owes." />
      ) : (
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Number</TableHead><TableHead>Customer</TableHead><TableHead>Date</TableHead>
                <TableHead>Amount</TableHead><TableHead>Status</TableHead><TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((n) => (
                <TableRow key={n._id}>
                  <TableCell>{n.number}</TableCell>
                  <TableCell>{n.customer_name}</TableCell>
                  <TableCell>{(n.date || '').slice(0, 10)}</TableCell>
                  <TableCell>{formatCurrency(n.grand_total || 0)}</TableCell>
                  <TableCell><Badge>{n.status}</Badge></TableCell>
                  <TableCell>
                    {n.status === 'draft' && <Button size="sm" onClick={() => transition(n._id, 'sent')}>Send</Button>}
                    {n.status === 'sent' && <Button size="sm" onClick={() => transition(n._id, 'paid')}>Mark paid</Button>}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="New Credit Note">
        <form onSubmit={create} className="space-y-4">
          <Select label="Original invoice" value={linkedInvoice} onChange={(e) => setLinkedInvoice(e.target.value)}
            options={[{ value: '', label: 'Select invoice…' }, ...invoices.map((i) => ({ value: i._id, label: `${i.number} — ${i.customer_name} (${formatCurrency(i.grand_total || 0)})` }))]} />
          <Input label="Reason" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Goods returned" />
          <Input label="Customer" value={customer} onChange={(e) => setCustomer(e.target.value)} placeholder={linked?.customer_name || 'Walk-in'} />
          {items.map((it, i) => (
            <div key={i} className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <Input label="Description" value={it.desc} onChange={(e) => setItem(i, { desc: e.target.value })} />
              <Input label="Qty" type="number" value={it.qty} onChange={(e) => setItem(i, { qty: e.target.value })} />
              <Input label="Rate" type="number" value={it.rate} onChange={(e) => setItem(i, { rate: e.target.value })} />
              <Input label="GST %" type="number" value={it.gst_rate} onChange={(e) => setItem(i, { gst_rate: e.target.value })} />
            </div>
          ))}
          <Button type="button" variant="secondary" onClick={() => setItems([...items, { ...BLANK_ITEM }])}>+ Add item</Button>
          {linked && (
            <p className="text-sm text-gray-600">
              Original invoice: {formatCurrency(linked.grand_total || 0)}. Credit note: {formatCurrency(preview().grand)}.
              Remaining after credit: {formatCurrency((linked.grand_total || 0) - preview().grand)}.
            </p>
          )}
          <Button type="submit">Create Credit Note</Button>
        </form>
      </Modal>
    </DashboardLayout>
  );
}
