import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'TaxShield — Financial & Compliance OS for Indian Small Businesses',
  description: 'Record once. TaxShield handles accounting, invoicing, GST, TDS, reconciliation, documents, compliance and reporting. Deterministic, private, zero-cost to start.',
  alternates: { canonical: '/' },
  openGraph: {
    title: 'TaxShield — Financial & Compliance OS for Indian Small Businesses',
    description: 'Accounting, tax, GST, TDS, reconciliation and compliance for Indian small businesses.',
    type: 'website',
  },
};

const FEATURES = [
  ['Double-entry books', 'Every sale, expense and payment posts balanced journals automatically. Trial balance, P&L, balance sheet and cash flow included.'],
  ['GST-aware invoicing', 'CGST/SGST/IGST computed deterministically. GSTR-1 and GSTR-3B preparation summaries for review — never fake filing.'],
  ['Income tax, explained', 'Old vs new regime estimates with rule, period and evidence shown behind “View calculation details”.'],
  ['TDS + AIS/26AS', 'Section-wise TDS computation and AIS/26AS reconciliation with matched/mismatch/missing states.'],
  ['Evidence vault', 'Every figure links to transactions, documents, rules and evidence. Nothing unexplained.'],
  ['CA collaboration', 'Practices manage clients, tasks, document requests and reviews with enforced chains.'],
];

const FAQS = [
  ['Does TaxShield replace my CA?', 'No. It automates routine books, tax prep and compliance, and escalates disputes, audits and litigation to a qualified professional.'],
  ['Is my financial data used for AI training?', 'Never. AI training from customer data is off by default; the tax engine is deterministic rules, not a model.'],
  ['Is there a free plan?', 'Yes — a usable Free plan, plus trials with no auto-billing. Paid plans unlock scale and practice features.'],
  ['Do you file ITR/GST returns for me?', 'No. TaxShield prepares review-ready summaries and exports; filing happens through official channels with your consent. Anything else would be dishonest to claim.'],
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <p className="text-xl font-bold">TaxShield</p>
          <nav className="hidden sm:flex gap-6 text-sm text-gray-600" aria-label="Marketing">
            <Link href="/pricing" className="hover:text-gray-900">Pricing</Link>
            <Link href="/security" className="hover:text-gray-900">Security</Link>
            <Link href="/help" className="hover:text-gray-900">Help</Link>
            <Link href="/privacy" className="hover:text-gray-900">Privacy</Link>
          </nav>
          <div className="flex gap-2">
            <Link href="/login" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">Sign in</Link>
            <Link href="/register" className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">Get started</Link>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4">
        <section className="py-16 sm:py-24 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">Simplify your business finances, tax and compliance.</h1>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Record once. TaxShield handles the accounting, GST, TDS, reconciliation, documents and reporting around it — for Indian small businesses, freelancers and CA practices.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            <Link href="/register" className="px-6 py-3 font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">Start free</Link>
            <Link href="/pricing" className="px-6 py-3 font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">See pricing</Link>
          </div>
          <p className="mt-3 text-sm text-gray-500">Free plan · No card required · Your data stays yours</p>
        </section>

        <section className="pb-16" aria-label="How it works">
          <h2 className="text-2xl font-bold text-center">How it works</h2>
          <ol className="mt-6 grid sm:grid-cols-4 gap-4 text-sm">
            {['Record income, expenses and invoices', 'TaxShield posts balanced books automatically', 'Review tax, GST and compliance with evidence', 'Share with your CA or export everything'].map((s, i) => (
              <li key={s} className="border border-gray-200 rounded-lg p-4">
                <p className="font-bold text-primary-600">{i + 1}</p>
                <p className="mt-1 text-gray-700">{s}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className="pb-16" aria-label="Features">
          <h2 className="text-2xl font-bold text-center">Everything a small business needs</h2>
          <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map(([t, b]) => (
              <div key={t} className="border border-gray-200 rounded-lg p-5">
                <h3 className="font-semibold">{t}</h3>
                <p className="mt-1 text-sm text-gray-600">{b}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="pb-16" aria-label="Who it is for">
          <h2 className="text-2xl font-bold text-center">Who it is for</h2>
          <p className="mt-4 text-center text-gray-600 max-w-2xl mx-auto text-sm">
            Individuals · Freelancers · Sole proprietors · Small shops · Service businesses ·
            Consultants · Professionals · Accountants · CA practices. The product adapts —
            individuals see a simple workspace, practices get clients, reviews and compliance queues.
          </p>
        </section>

        <section className="pb-20" aria-label="FAQ">
          <h2 className="text-2xl font-bold text-center"> Honest answers</h2>
          <div className="mt-6 max-w-3xl mx-auto space-y-3">
            {FAQS.map(([q, a]) => (
              <details key={q} className="border border-gray-200 rounded-lg p-4 text-sm">
                <summary className="font-medium cursor-pointer">{q}</summary>
                <p className="mt-2 text-gray-600">{a}</p>
              </details>
            ))}
          </div>
          <div className="text-center mt-10">
            <Link href="/register" className="px-6 py-3 font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">Get started free</Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-gray-100">
        <div className="max-w-6xl mx-auto px-4 py-8 flex flex-wrap gap-x-8 gap-y-2 text-sm text-gray-500">
          <Link href="/pricing" className="hover:text-gray-900">Pricing</Link>
          <Link href="/security" className="hover:text-gray-900">Security</Link>
          <Link href="/privacy" className="hover:text-gray-900">Privacy</Link>
          <Link href="/terms" className="hover:text-gray-900">Terms</Link>
          <Link href="/refund-policy" className="hover:text-gray-900">Refunds</Link>
          <Link href="/acceptable-use" className="hover:text-gray-900">Acceptable use</Link>
          <Link href="/disclaimer" className="hover:text-gray-900">Disclaimer</Link>
          <Link href="/cookie-policy" className="hover:text-gray-900">Cookies</Link>
          <Link href="/help" className="hover:text-gray-900">Help center</Link>
          <Link href="/support" className="hover:text-gray-900">Support</Link>
        </div>
      </footer>
    </div>
  );
}
