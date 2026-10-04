import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Help Center — TaxShield',
  description: 'Getting-started and workflow guides for TaxShield.',
};

const GUIDES: [string, string][] = [
  ['Getting started', 'Register, complete onboarding, add your first transaction and customer, create an invoice, and watch the dashboard come alive. Every step uses real data — try Load Demo Data first to explore safely.'],
  ['Accounting', 'You record business events; TaxShield posts balanced double-entry journals automatically. See Books → Trial Balance (debits must equal credits), P&L, Balance Sheet and Cash Flow.'],
  ['Invoices', 'Create GST-aware invoices (CGST/SGST or IGST). Lifecycle: Draft → Sent → Viewed → Partially Paid → Paid (or Overdue). Illegal jumps are rejected. Record UPI/cash/card payments with references.'],
  ['GST', 'Validate GSTINs, review GSTR-1/GSTR-3B preparation summaries, and reconcile books against portal figures. Preparation only — filing happens officially.'],
  ['TDS', 'Section-wise applicability (thresholds, 20% without PAN), payable tracking and 26AS comparison.'],
  ['Income tax', 'Old vs new regime estimates with full component breakdown. Planning shows only rule-backed, evidence-gated opportunities. Open “View calculation details” for period, rule version and source.'],
  ['AIS / 26AS', 'Each item shows the TaxShield record vs the source record, the difference, an explanation and a suggested action.'],
  ['Reports', 'P&L, balance sheet, trial balance, GST/TDS summaries and readiness — all exportable as CSV/JSON.'],
  ['CA practice', 'Add clients, assign tasks, request documents, and move reviews through auto → needs_review → accountant/ca → approved.'],
  ['Security', 'JWT sessions, bcrypt passwords, rate limits, ownership-checked downloads. Change your password and revoke sessions in Settings → Security.'],
  ['Privacy', 'Consent per purpose, export and deletion workflows in Settings → Data. Training from customer data is always off.'],
  ['Billing', 'Plans are configuration-driven. Trials never auto-bill; cancel returns you to Free with data retained. See /pricing.'],
];

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
          <Link href="/support" className="text-sm font-medium text-primary-700 hover:underline">Contact support →</Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold">Help center</h1>
        <p className="text-gray-500 mt-2">Guides describe what the product actually does — no statutory article here replaces official sources or professional advice.</p>
        <div className="mt-8 space-y-3">
          {GUIDES.map(([t, b]) => (
            <details key={t} className="border border-gray-200 rounded-lg p-4 text-sm">
              <summary className="font-medium cursor-pointer">{t}</summary>
              <p className="mt-2 text-gray-600">{b}</p>
            </details>
          ))}
        </div>
      </main>
    </div>
  );
}
