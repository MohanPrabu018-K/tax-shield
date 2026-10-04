import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Acceptable Use — TaxShield' };

export default function AcceptableUsePage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12 text-sm text-gray-700 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Acceptable Use</h1>
        <p>Do not use TaxShield to break the law, evade tax, forge documents, file false returns, harass others, probe other tenants&apos; data, automate abuse (spam registrations, upload flooding, credential stuffing), or misrepresent estimates as statutory filings.</p>
        <p>Plan limits (transactions, invoices, documents, storage, assistant usage) are enforced to keep the service fair; circumventing them may lead to suspension after notice.</p>
        <p>Violations may result in suspension or termination following review. Actions with security impact are audit-logged.</p>
      </main>
    </div>
  );
}
