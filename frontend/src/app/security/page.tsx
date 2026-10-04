import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Security — TaxShield',
  description: 'How TaxShield protects your financial data.',
};

const ROWS: [string, string][] = [
  ['Authentication', 'JWT bearer sessions, bcrypt-hashed passwords, rate-limited login/register/password-reset, single-use expiring reset tokens.'],
  ['Authorization', 'Every data request is tenant-scoped server-side. Admin console requires an admin account; attempts are audited.'],
  ['Transport', 'HTTPS in deployment, single-origin CORS, security headers (nosniff, referrer-policy, permissions-policy, framing protection).'],
  ['Files', '10 MB / type-allowlisted uploads, filename sanitization, ownership-checked authenticated downloads — never public URLs.'],
  ['Secrets', 'Only the public API URL reaches the browser. Signing keys stay server-side; production refuses to boot without one.'],
  ['Audit', 'Logins, mutations, billing, rule activations and incidents carry actor, object, request ID and timestamp.'],
  ['Backups', 'Manifest + SHA-256 + HMAC-sealed backups with verified restore drills and an over-production guard.'],
  ['Honest gaps', 'No MFA yet (documented, never faked). No third-party trackers. Report issues via Support — incidents follow a detected → reviewed workflow.'],
];

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
          <Link href="/support" className="text-sm font-medium text-primary-700 hover:underline">Report an issue →</Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold">Security</h1>
        <p className="text-gray-500 mt-2">What protects your books — stated plainly, without compliance theater.</p>
        <div className="mt-8 space-y-3">
          {ROWS.map(([t, b]) => (
            <div key={t} className="border border-gray-200 rounded-lg p-4 text-sm">
              <h2 className="font-medium">{t}</h2>
              <p className="mt-1 text-gray-600">{b}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
