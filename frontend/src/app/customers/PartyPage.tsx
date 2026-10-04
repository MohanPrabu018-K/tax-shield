'use client';

import { Fragment, useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Party } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { Pager } from '@/components/ui/Pager';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { formatCurrency } from '@/lib/utils';
import { Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export function PartyPage({ kind, title, subtitle }: { kind: 'customer' | 'vendor'; title: string; subtitle: string }) {
  const [parties, setParties] = useState<Party[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', gstin: '', phone: '', address: '' });
  const PAGE_SIZE = 20;

  const load = async (p = page) => {
    setLoading(true);
    setError(null);
    try {
      const [ps, inv] = await Promise.all([api.getParties(kind), api.getInvoices()]);
      setParties(ps);
      setInvoices(inv);
    } catch (e: any) {
      setError(e?.response?.data?.error || `Failed to load ${title.toLowerCase()}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    if (typeof window !== 'undefined' && window.location.search.includes('action=new')) setShowModal(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createParty({ kind, ...form });
      toast.success(`${kind === 'customer' ? 'Customer' : 'Vendor'} added`);
      setShowModal(false);
      setForm({ name: '', gstin: '', phone: '', address: '' });
      load(0);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Failed to save');
    }
  };

  const remove = async (id: string, name: string) => {
    if (!window.confirm(`Delete ${name}?`)) return;
    try {
      await api.deleteParty(id);
      toast.success('Deleted');
      load(page);
    } catch {
      toast.error('Delete failed');
    }
  };

  const partyInvoices = (name: string) =>
    invoices.filter((i) => (i.customer_name || '').toLowerCase() === name.toLowerCase());
  const outstanding = (name: string) =>
    partyInvoices(name).reduce((s, i) => s + parseFloat(i.balance || 0), 0);

  const visible = parties.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
            <p className="text-gray-500 mt-1">{subtitle}</p>
          </div>
          <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-2" />Add {kind === 'customer' ? 'Customer' : 'Vendor'}</Button>
        </div>

        <Card>
          <CardHeader><CardTitle>All ({parties.length})</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={() => load()} />
            : parties.length === 0 ? (
              <EmptyState title={`No ${title.toLowerCase()} yet`} body={`Add your first ${kind} to track invoices, payments and outstanding amounts.`} action={<Button onClick={() => setShowModal(true)}>Add {kind}</Button>} />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>GSTIN</TableHead>
                    <TableHead className="text-right">Outstanding</TableHead>
                    <TableHead>Invoices</TableHead>
                    <TableHead><span className="sr-only">Actions</span></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {visible.map((p) => (
                    <Fragment key={p.id}>
                      <TableRow>
                        <TableCell>
                          <button className="font-medium text-primary-700 hover:underline" onClick={() => setExpanded(expanded === p.id ? null : p.id)} aria-expanded={expanded === p.id}>
                            {p.name}
                          </button>
                          {p.phone && <p className="text-xs text-gray-500">{p.phone}</p>}
                        </TableCell>
                        <TableCell className="font-mono text-xs">{p.gstin || '—'}</TableCell>
                        <TableCell className="text-right font-medium">{formatCurrency(outstanding(p.name))}</TableCell>
                        <TableCell>{partyInvoices(p.name).length}</TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm" onClick={() => remove(p.id, p.name)} aria-label={`Delete ${p.name}`}>
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                      {expanded === p.id && (
                        <TableRow>
                          <TableCell colSpan={5}>
                            <div className="bg-gray-50 rounded-lg p-3 text-sm">
                              <p className="font-medium mb-2">How much does {p.name} {kind === 'customer' ? 'owe' : 'get'}? {formatCurrency(outstanding(p.name))}</p>
                              {partyInvoices(p.name).length === 0 ? (
                                <p className="text-gray-500">No invoices linked yet.</p>
                              ) : (
                                <ul className="space-y-1">
                                  {partyInvoices(p.name).slice(0, 10).map((i: any) => (
                                    <li key={i.id} className="flex justify-between">
                                      <span>{i.number} · {i.status}</span>
                                      <span>{formatCurrency(i.balance)} due {String(i.due_date).slice(0, 10)}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </Fragment>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
          <div className="px-4 border-t border-gray-100">
            <Pager page={page} pageSize={PAGE_SIZE} hasMore={(page + 1) * PAGE_SIZE < parties.length} count={visible.length} onPage={setPage} />
          </div>
        </Card>

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={`Add ${kind}`}>
          <form onSubmit={create} className="space-y-4">
            <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            <Input label="GSTIN (optional)" value={form.gstin} onChange={(e) => setForm({ ...form, gstin: e.target.value })} placeholder="27AAPFU0939F1ZV" />
            <Input label="Phone (optional)" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <Input label="Address (optional)" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setShowModal(false)}>Cancel</Button>
              <Button type="submit">Save</Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
