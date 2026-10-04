'use client';

import { useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { PageLoading, EmptyState } from '@/components/ui/State';
import { useDebouncedValue } from '@/lib/useApi';
import { formatCurrency } from '@/lib/utils';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[] | null>(null);
  const [busy, setBusy] = useState(false);
  const debounced = useDebouncedValue(query);

  const search = async () => {
    const q = debounced.trim().toLowerCase();
    if (q.length < 2) {
      setResults(null);
      return;
    }
    setBusy(true);
    try {
      const [tx, inv, parties, docs, tasks] = await Promise.all([
        api.getTransactionsPaginated(0, 200),
        api.getInvoices(),
        api.getParties(),
        api.getDocuments(),
        api.getTasks().catch(() => []),
      ]);
      const out: any[] = [];
      tx.forEach((t: any) => {
        if (`${t.description} ${t.source} ${t.category}`.toLowerCase().includes(q)) {
          out.push({ kind: 'Transaction', title: t.description, meta: `${formatCurrency(t.amount)} · ${t.category}`, href: '/transactions' });
        }
      });
      inv.forEach((i: any) => {
        if (`${i.number} ${i.customer_name}`.toLowerCase().includes(q)) {
          out.push({ kind: 'Invoice', title: `${i.number} · ${i.customer_name}`, meta: `${formatCurrency(i.grand_total)} · ${i.status}`, href: '/invoices' });
        }
      });
      parties.forEach((p: any) => {
        if (p.name.toLowerCase().includes(q)) {
          out.push({ kind: p.kind === 'customer' ? 'Customer' : 'Vendor', title: p.name, meta: p.gstin || '', href: p.kind === 'customer' ? '/customers' : '/vendors' });
        }
      });
      docs.forEach((d: any) => {
        if (`${d.file_name} ${d.document_type}`.toLowerCase().includes(q)) {
          out.push({ kind: 'Document', title: d.file_name, meta: d.document_type, href: '/documents' });
        }
      });
      tasks.forEach((t: any) => {
        if (`${t.title} ${t.client}`.toLowerCase().includes(q)) {
          out.push({ kind: 'Task', title: t.title, meta: t.client, href: '/practice' });
        }
      });
      setResults(out.slice(0, 50));
    } finally {
      setBusy(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-3xl">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Search</h2>
          <p className="text-gray-500 mt-1">Across transactions, invoices, parties, documents and tasks</p>
        </div>
        <Input
          placeholder="Type at least 2 characters…"
          value={query}
          onChange={(e) => { setQuery(e.target.value); }}
          onKeyDown={(e) => { if (e.key === 'Enter') search(); }}
          aria-label="Global search"
        />
        <button onClick={search} className="sr-only">Search</button>
        <Card>
          <CardHeader><CardTitle>Results {results ? `(${results.length})` : ''}</CardTitle></CardHeader>
          <CardContent>
            {busy ? <PageLoading label="Searching…" /> : !results ? (
              <EmptyState title="Search everything" body="Results link straight to the record's page. Paginated server lists keep this fast." />
            ) : results.length === 0 ? (
              <EmptyState title="No matches" body="Try a customer name, invoice number, amount description or document type." />
            ) : (
              <ul className="space-y-2 text-sm">
                {results.map((r, i) => (
                  <li key={i} className="border-b border-gray-100 pb-2">
                    <span className="text-xs uppercase text-gray-400">{r.kind}</span>{' '}
                    <Link href={r.href} className="font-medium text-primary-700 hover:underline">{r.title}</Link>{' '}
                    <span className="text-gray-500">{r.meta}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
