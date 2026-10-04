'use client';

import { RecvPayPage } from '../receivables/RecvPayPage';

export default function PayablesPage() {
  return <RecvPayPage kind="purchase" title="Payables" subtitle="What you owe vendors, due dates and payment status" />;
}
