import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Refund & Cancellation Policy — TaxShield' };

export default function RefundPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="text-xl font-bold">TaxShield</Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12 text-sm text-gray-700 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Refund &amp; Cancellation Policy</h1>
        <p>Cancel anytime from Billing. Access continues until the end of the paid period, then the workspace returns to the Free plan with your data retained per the retention policy.</p>
        <p>Trials never convert to paid plans automatically — a subscription starts only through an explicit checkout.</p>
        <p>Refund requests are handled manually: open a Support ticket with your invoice reference and reason. Each request is reviewed; approved refunds are processed through the original payment method by the billing operator. Test-mode checkouts (clearly labelled) never move money and are never refundable because nothing was charged.</p>
        <p>Chargebacks and disputes: contact support first — most billing issues are resolved faster that way.</p>
      </main>
    </div>
  );
}
