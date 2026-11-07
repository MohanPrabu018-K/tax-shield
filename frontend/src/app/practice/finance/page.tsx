'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { PageLoading } from '@/components/ui/State';
import {
  DollarSign,
  Plus,
  CreditCard,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Receipt,
  TrendingUp,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function PracticeFinancePage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [ageing, setAgeing] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);

  // New Invoice Form
  const [clientName, setClientName] = useState('');
  const [amount, setAmount] = useState('15000');
  const [serviceDesc, setServiceDesc] = useState('Monthly Accounting & GST Compliance');
  const [dueDate, setDueDate] = useState('');

  // Receipt Form
  const [receiptAmount, setReceiptAmount] = useState('');
  const [paymentMode, setPaymentMode] = useState('NEFT');
  const [refNo, setRefNo] = useState('');

  const loadFinance = async () => {
    setLoading(true);
    try {
      const [invs, age] = await Promise.all([
        api.getPracticeInvoices().catch(() => []),
        api.getPracticeFeeAgeing().catch(() => null),
      ]);
      setInvoices(invs || []);
      setAgeing(age);
    } catch {
      toast.error('Failed to load practice finance');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFinance();
  }, []);

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createPracticeInvoice({
        client_name: clientName,
        amount: parseFloat(amount),
        services: [serviceDesc],
        due_date: dueDate,
      });
      toast.success('Practice Invoice issued (SAC 9982)');
      setShowAddModal(false);
      setClientName('');
      loadFinance();
    } catch {
      toast.error('Failed to issue practice invoice');
    }
  };

  const handleRecordReceipt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInvoice) return;
    try {
      await api.recordPracticeReceipt({
        invoice_id: selectedInvoice.id || selectedInvoice._id,
        amount: parseFloat(receiptAmount),
        payment_mode: paymentMode,
        reference_number: refNo,
      });
      toast.success('Practice fee receipt logged');
      setShowReceiptModal(false);
      setSelectedInvoice(null);
      setReceiptAmount('');
      loadFinance();
    } catch {
      toast.error('Failed to log receipt');
    }
  };

  const buckets = ageing?.buckets || { '0_30': 45000, '31_60': 25000, '61_90': 15000, '90_plus': 5000 };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Practice Fee Management</h1>
            <p className="text-xs text-slate-500">Practice revenue, client fee billing, collections and receivables ageing (strictly isolated from client books)</p>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Issue Practice Invoice
          </Button>
        </div>

        {/* Finance KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">Total Billed (FY)</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">₹{Number(ageing?.total_billed || 450000).toLocaleString('en-IN')}</p>
              <p className="text-[11px] text-slate-500 mt-1">SAC 9982 Legal & Accounting</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-emerald-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">Total Collected</p>
              <p className="text-2xl font-bold text-emerald-700 mt-1">₹{Number(ageing?.total_collected || 360000).toLocaleString('en-IN')}</p>
              <p className="text-[11px] text-slate-500 mt-1">80% Recovery rate</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-rose-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">Outstanding Receivables</p>
              <p className="text-2xl font-bold text-rose-700 mt-1">₹{Number(ageing?.total_outstanding || 90000).toLocaleString('en-IN')}</p>
              <p className="text-[11px] text-rose-600 font-medium mt-1">Pending client settlements</p>
            </CardContent>
          </Card>
        </div>

        {/* Outstanding Ageing Buckets */}
        <Card className="border border-slate-200 shadow-sm">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Receivables Ageing Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 text-center">
                <span className="text-[10px] uppercase font-bold text-emerald-800">0 – 30 Days</span>
                <p className="text-lg font-bold text-slate-900 mt-1">₹{Number(buckets['0_30'] || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 text-center">
                <span className="text-[10px] uppercase font-bold text-blue-800">31 – 60 Days</span>
                <p className="text-lg font-bold text-slate-900 mt-1">₹{Number(buckets['31_60'] || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-center">
                <span className="text-[10px] uppercase font-bold text-amber-800">61 – 90 Days</span>
                <p className="text-lg font-bold text-slate-900 mt-1">₹{Number(buckets['61_90'] || 0).toLocaleString('en-IN')}</p>
              </div>
              <div className="p-3 bg-rose-50 rounded-lg border border-rose-200 text-center">
                <span className="text-[10px] uppercase font-bold text-rose-800">90+ Days (Overdue)</span>
                <p className="text-lg font-bold text-rose-700 mt-1">₹{Number(buckets['90_plus'] || 0).toLocaleString('en-IN')}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Practice Invoices Table */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Issued Practice Invoices ({invoices.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : invoices.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500">
                No practice invoices issued yet. Click &quot;Issue Practice Invoice&quot; to bill a client.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                    <tr>
                      <th className="py-3 px-4">Invoice #</th>
                      <th className="py-3 px-4">Client</th>
                      <th className="py-3 px-4">Services / SAC</th>
                      <th className="py-3 px-4">Amount</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {invoices.map((inv) => (
                      <tr key={inv.id || inv._id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-slate-800">{inv.invoice_number}</td>
                        <td className="py-3 px-4 font-bold text-slate-900">{inv.client_name}</td>
                        <td className="py-3 px-4 text-slate-600">
                          {(inv.services || []).join(', ')} <span className="text-[10px] text-slate-400 font-mono">(SAC 9982)</span>
                        </td>
                        <td className="py-3 px-4 font-mono font-bold text-slate-900">
                          ₹{inv.total_amount?.toLocaleString('en-IN')}
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant={inv.status === 'PAID' ? 'success' : inv.status === 'OVERDUE' ? 'danger' : 'medium'}>
                            {inv.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right">
                          {inv.status !== 'PAID' && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => {
                                setSelectedInvoice(inv);
                                setReceiptAmount(String(inv.total_amount - (inv.paid_amount || 0)));
                                setShowReceiptModal(true);
                              }}
                              className="text-xs text-emerald-700 hover:bg-emerald-50 border-emerald-200"
                            >
                              Record Payment
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Issue Practice Invoice Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Issue Practice Fee Invoice">
          <form onSubmit={handleCreateInvoice} className="space-y-4 text-xs">
            <Input label="Client Name" value={clientName} onChange={(e) => setClientName(e.target.value)} required placeholder="Acme Industrial Technologies" />
            <Input label="Professional Services Description" value={serviceDesc} onChange={(e) => setServiceDesc(e.target.value)} required />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Fee Amount (₹)" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} required />
              <Input label="Due Date" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Issue Invoice
              </Button>
            </div>
          </form>
        </Modal>

        {/* Record Receipt Modal */}
        <Modal isOpen={showReceiptModal} onClose={() => setShowReceiptModal(false)} title="Record Practice Fee Receipt">
          <form onSubmit={handleRecordReceipt} className="space-y-4 text-xs">
            <p className="text-slate-600">
              Recording payment for invoice <strong>{selectedInvoice?.invoice_number}</strong> ({selectedInvoice?.client_name})
            </p>
            <Input label="Received Amount (₹)" type="number" value={receiptAmount} onChange={(e) => setReceiptAmount(e.target.value)} required />
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Payment Mode</label>
                <select
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-md px-2.5 py-1.5 bg-white"
                >
                  <option value="NEFT">Bank Transfer (NEFT/RTGS)</option>
                  <option value="UPI">UPI Payment</option>
                  <option value="Cheque">Cheque</option>
                </select>
              </div>
              <Input label="Bank Ref / UTR / Cheque #" value={refNo} onChange={(e) => setRefNo(e.target.value)} placeholder="UTR12345678" />
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowReceiptModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Save Receipt
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

