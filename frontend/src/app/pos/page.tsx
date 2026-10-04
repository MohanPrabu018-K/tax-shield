'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { formatCurrency } from '@/lib/utils';
import { Plus, Minus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function PosPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [cart, setCart] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [method, setMethod] = useState('cash');
  const [reference, setReference] = useState('');
  const [busy, setBusy] = useState(false);
  const [lastBill, setLastBill] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setProducts(await api.getProducts());
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const add = (sku: string, delta: number) =>
    setCart((c) => {
      const next = (c[sku] || 0) + delta;
      if (next <= 0) {
        const { [sku]: _dropped, ...rest } = c;
        return rest;
      }
      return { ...c, [sku]: next };
    });

  const items = Object.entries(cart)
    .map(([sku, qty]) => ({ ...products.find((p) => p.sku === sku), qty }))
    .filter((i) => i.sku);
  const subtotal = items.reduce((s, i) => s + i.qty * parseFloat(i.rate || 0), 0);

  const charge = async () => {
    if (items.length === 0) return;
    setBusy(true);
    try {
      const bill = await api.createPosBill(
        items.map((i) => ({ sku: i.sku, qty: i.qty })),
        { payment_method: method, payment_reference: reference }
      );
      setLastBill(bill);
      setCart({});
      setReference('');
      toast.success(`Bill ${bill.number} · ${formatCurrency(bill.grand_total)} — stock, invoice and books updated`);
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Billing failed (stock checked first)');
    } finally {
      setBusy(false);
    }
  };

  const matches = products.filter(
    (p) => !query || p.name.toLowerCase().includes(query.toLowerCase()) || p.sku.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Point of Sale</h2>
          <p className="text-gray-500 mt-1">Fast billing — product → cart → tax → payment → invoice, books and stock</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Products</CardTitle></CardHeader>
            <CardContent>
              <Input placeholder="Search by name or SKU…" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search products" />
              {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
              : matches.length === 0 ? <EmptyState title="No products" body="Add products in Inventory first." />
              : (
                <ul className="mt-3 space-y-2 max-h-96 overflow-y-auto">
                  {matches.slice(0, 50).map((p) => (
                    <li key={p.id} className="flex items-center justify-between border border-gray-100 rounded-lg p-2 text-sm">
                      <div>
                        <p className="font-medium">{p.name} <span className="text-gray-400 font-mono text-xs">{p.sku}</span></p>
                        <p className="text-gray-500">{formatCurrency(p.rate)} · stock {p.stock}</p>
                      </div>
                      <Button variant="secondary" size="sm" onClick={() => add(p.sku, 1)} aria-label={`Add ${p.name}`}>
                        <Plus className="h-4 w-4" />
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Cart ({items.length})</CardTitle></CardHeader>
            <CardContent>
              {items.length === 0 ? (
                <EmptyState title="Cart is empty" body="Tap + on a product to add it." />
              ) : (
                <div className="space-y-2 text-sm">
                  {items.map((i) => (
                    <div key={i.sku} className="flex items-center justify-between border-b border-gray-100 pb-2">
                      <p className="font-medium">{i.name} × {i.qty}</p>
                      <div className="flex items-center gap-1">
                        <button onClick={() => add(i.sku, -1)} className="p-1 border rounded" aria-label={`Decrease ${i.name}`}><Minus className="h-3 w-3" /></button>
                        <button onClick={() => add(i.sku, 1)} className="p-1 border rounded" aria-label={`Increase ${i.name}`}><Plus className="h-3 w-3" /></button>
                        <button onClick={() => add(i.sku, -i.qty)} className="p-1 border rounded text-red-600" aria-label={`Remove ${i.name}`}><Trash2 className="h-3 w-3" /></button>
                      </div>
                    </div>
                  ))}
                  <p className="flex justify-between pt-2"><span>Subtotal (excl. GST)</span><strong>{formatCurrency(subtotal)}</strong></p>
                  <div className="grid grid-cols-2 gap-2">
                    <Input label="Payment" value={method} onChange={(e) => setMethod(e.target.value)} placeholder="cash / UPI / card" />
                    <Input label="Reference" value={reference} onChange={(e) => setReference(e.target.value)} placeholder="UPI ref (optional)" />
                  </div>
                  <Button onClick={charge} loading={busy} className="w-full">Charge · invoice + books + stock</Button>
                  {lastBill && (
                    <p className="text-green-700" role="status">Last bill {lastBill.number} · {formatCurrency(lastBill.grand_total)} · paid</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
