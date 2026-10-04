import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Cookie Policy — TaxShield' };

export default function CookiePage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12 text-sm text-gray-700 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Cookie Policy</h1>
        <p>Essential: session token in your browser (required to stay signed in). Preferences: workspace setup, alert and AI-explanation choices stored on your device.</p>
        <p>Security: rate-limit counters are server-side and contain no personal data. There are no analytics, advertising or marketing cookies — nothing to accept beyond the essential session, so the consent banner only records an acknowledgement.</p>
        <p>Clearing site data signs you out and resets device preferences; your workspace data stays on the server.</p>
      </main>
    </div>
  );
}
