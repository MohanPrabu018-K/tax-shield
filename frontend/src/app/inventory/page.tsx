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
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export default function InventoryPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [low, setLow] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ sku: '', name: '', hsn: '', rate: '', gst_rate: '18', reorder_at: '5', opening_stock: '0' });

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ps, ls] = await Promise.all([api.getProducts(), api.getLowStock()]);
      setProducts(ps);
      setLow(ls.items || []);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load inventory');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createProduct({
        ...form, rate: parseFloat(form.rate), gst_rate: parseFloat(form.gst_rate),
        reorder_at: parseFloat(form.reorder_at), opening_stock: parseFloat(form.opening_stock),
      });
      toast.success('Product added');
      setShowModal(false);
      setForm({ sku: '', name: '', hsn: '', rate: '', gst_rate: '18', reorder_at: '5', opening_stock: '0' });
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Failed to add product');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Inventory</h2>
            <p className="text-gray-500 mt-1">SKUs, stock levels, movements and low-stock alerts</p>
          </div>
          <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-2" />Add Product</Button>
        </div>

        {low.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Low stock ({low.length})</CardTitle></CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {low.map((l: any) => (
                  <Badge key={l.sku} variant="danger">{l.sku} · {l.stock} left</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle>Products ({products.length})</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
            : products.length === 0 ? (
              <EmptyState title="No products" body="Add products with SKUs to track stock and sell via POS." action={<Button onClick={() => setShowModal(true)}>Add Product</Button>} />
            ) : (
              <Table>
                <TableHeader><TableRow><TableHead>SKU</TableHead><TableHead>Name</TableHead><TableHead className="text-right">Rate</TableHead><TableHead className="text-right">Stock</TableHead></TableRow></TableHeader>
                <TableBody>
                  {products.map((p: any) => (
                    <TableRow key={p.id}>
                      <TableCell className="font-mono text-xs">{p.sku}</TableCell>
                      <TableCell className="font-medium">{p.name}</TableCell>
                      <TableCell className="text-right">{formatCurrency(p.rate)}</TableCell>
                      <TableCell className="text-right">{p.stock}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add Product">
          <form onSubmit={create} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <Input label="SKU" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} required />
              <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              <Input label="HSN" value={form.hsn} onChange={(e) => setForm({ ...form, hsn: e.target.value })} />
              <Input label="Rate (₹)" type="number" step="0.01" value={form.rate} onChange={(e) => setForm({ ...form, rate: e.target.value })} required />
              <Input label="GST %" type="number" step="0.01" value={form.gst_rate} onChange={(e) => setForm({ ...form, gst_rate: e.target.value })} />
              <Input label="Reorder at" type="number" value={form.reorder_at} onChange={(e) => setForm({ ...form, reorder_at: e.target.value })} />
              <Input label="Opening stock" type="number" value={form.opening_stock} onChange={(e) => setForm({ ...form, opening_stock: e.target.value })} />
            </div>
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
