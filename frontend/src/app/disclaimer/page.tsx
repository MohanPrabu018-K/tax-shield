import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Disclaimer — TaxShield' };

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12 text-sm text-gray-700 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Disclaimer</h1>
        <p>TaxShield provides preliminary analysis based on the information available in the system. It does not provide legal, tax or financial advice and is not a substitute for a qualified tax professional.</p>
        <p>Tax computations are deterministic estimates from versioned rules for the stated tax period — not filings, not assessments, and never guaranteed outcomes. Forecasts are estimates with stated assumptions. Where evidence is missing, figures are marked as needing review.</p>
        <p>For disputes, scrutiny, audits, litigation, international or restructuring matters: professional review is recommended. Nothing on this site claims DPDP/GST/IT certification or “100% accuracy”.</p>
      </main>
    </div>
  );
}
