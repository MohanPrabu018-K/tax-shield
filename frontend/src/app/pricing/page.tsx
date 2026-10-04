'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export default function PricingPage() {
  const [plans, setPlans] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getPlans().then((r) => setPlans(r.plans || [])).catch(() => setError('Could not load plans'));
  }, []);

  const price = (p: any) =>
    p.price_inr === 0 ? 'Free' : `${formatCurrency(p.price_inr / 100)} / ${p.interval === 'monthly' ? 'month' : p.interval}`;

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
          <Link href="/register" className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg">Get started</Link>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-14">
        <h1 className="text-3xl font-bold text-center">Pricing that scales with you</h1>
        <p className="text-center text-gray-500 mt-2">Configuration-driven plans. Cancel anytime — your data stays exportable. 14-day trials on paid plans, no auto-billing.</p>
        {error && <p className="text-center text-red-600 mt-4" role="alert">{error}</p>}
        <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {plans.map((p) => (
            <div key={p.id} className="border border-gray-200 rounded-xl p-6 flex flex-col">
              <h2 className="text-lg font-bold">{p.name}</h2>
              <p className="mt-1 text-2xl font-bold">{price(p)}</p>
              <ul className="mt-4 space-y-1 text-sm text-gray-600 flex-1">
                {p.features.map((f: string) => (
                  <li key={f}>✓ {f.replace(/_/g, ' ')}</li>
                ))}
                <li className="pt-2 text-gray-500">
                  {p.limits.transactions.toLocaleString('en-IN')} transactions · {p.limits.invoices.toLocaleString('en-IN')} invoices · {p.limits.documents.toLocaleString('en-IN')} documents
                </li>
              </ul>
              <Link href="/register" className="mt-6 text-center px-4 py-2 font-medium text-white bg-primary-600 rounded-lg">Choose {p.name}</Link>
            </div>
          ))}
        </div>
        <p className="text-center text-sm text-gray-500 mt-8">Prices in INR, exclusive of taxes where applicable. Payment processing (when enabled) uses provider-hosted flows — TaxShield never stores card numbers or CVVs.</p>
      </main>
    </div>
  );
}
