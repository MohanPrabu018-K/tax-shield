'use client';

import { RecvPayPage } from '../receivables/RecvPayPage';

export default function PayablesPage() {
  return <RecvPayPage kind="purchase" title="Bills You Owe" subtitle="Payables: what you owe vendors, due dates, payment status" />;
}
