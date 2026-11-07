'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading } from '@/components/ui/State';
import {
  ShieldCheck,
  CheckCircle2,
  Clock,
  Upload,
  FileText,
  DollarSign,
  MessageCircle,
  Download,
  Building,
  UserCheck,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function ClientPortalPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchPortal = async () => {
      setLoading(true);
      try {
        const res = await api.getPortalDashboard();
        setData(res);
      } catch {
        toast.error('Failed to load portal data');
      } finally {
        setLoading(false);
      }
    };
    fetchPortal();
  }, []);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    toast.success('Message delivered to your assigned Chartered Accountant');
    setMessage('');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <PageLoading />
      </div>
    );
  }

  const clientName = data?.client_name || 'Acme Industrial Technologies Pvt Ltd';
  const assignedCa = data?.assigned_ca || 'CA Kailash Nath (Senior Partner)';
  const assignedAccountant = data?.assigned_accountant || 'Rahul Verma';

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-12">
      {/* Client Portal Header */}
      <header className="bg-slate-900 text-white px-6 py-4 shadow-sm border-b border-slate-800">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="text-base font-bold text-white tracking-tight">TaxShield</span>
              <span className="block text-[10px] font-semibold text-emerald-400 tracking-wider uppercase">Client Portal</span>
            </div>
          </div>
          <div className="text-xs text-slate-300">
            Client Account: <strong className="text-white">{clientName}</strong>
          </div>
        </div>
      </header>

      {/* Main Client Workspace Container */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 space-y-6">
        {/* Engagement Team Card */}
        <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-900 p-5 rounded-xl border border-slate-800 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">
              Assigned Professional Engagement Team
            </span>
            <h1 className="text-lg font-bold">{clientName}</h1>
            <p className="text-xs text-slate-300">
              Responsible CA: <strong className="text-white">{assignedCa}</strong> • Lead Staff: {assignedAccountant}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <a href="https://wa.me/" target="_blank" rel="noreferrer">
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs">
                <MessageCircle className="h-3.5 w-3.5 mr-1.5" />
                WhatsApp Engagement Team
              </Button>
            </a>
          </div>
        </div>

        {/* Action Center: Pending Documents Requested by Firm */}
        <Card className="border border-amber-200 shadow-sm bg-amber-50/40">
          <CardHeader className="bg-amber-100/50 border-b border-amber-200 px-5 py-3 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <Upload className="h-4 w-4 text-amber-700" />
              <CardTitle className="text-xs font-bold uppercase text-amber-950 tracking-wide">
                Documents Requested by Your Accountant (Action Required)
              </CardTitle>
            </div>
            <Badge variant="medium">Pending Upload</Badge>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            {[
              { title: 'Bank Statement (Oct 2024)', desc: 'SBI Current A/c No. 3849102948 — Required for month-end reconciliation' },
              { title: 'Credit Card Statement (Oct 2024)', desc: 'Corporate Card Expenses — Required for expense verification' },
            ].map((req, idx) => (
              <div key={idx} className="bg-white p-3 rounded-lg border border-amber-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <p className="font-bold text-slate-900">{req.title}</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">{req.desc}</p>
                </div>
                <Button size="sm" className="bg-amber-600 hover:bg-amber-500 text-white text-xs shrink-0 font-medium">
                  <Upload className="h-3.5 w-3.5 mr-1.5" />
                  Upload PDF / Excel
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Live Statutory Compliance Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border border-slate-200 shadow-sm">
            <CardHeader className="p-4 pb-2 border-b border-slate-100">
              <CardTitle className="text-xs font-bold uppercase text-slate-600">GST Filing Status</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span>GSTR-1 (Sales):</span>
                <Badge variant="success">FILED (ACK 9841)</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>GSTR-3B (Tax Offset):</span>
                <Badge variant="medium">IN CA REVIEW</Badge>
              </div>
              <p className="text-[11px] text-slate-400 pt-1">Period: October 2024</p>
            </CardContent>
          </Card>

          <Card className="border border-slate-200 shadow-sm">
            <CardHeader className="p-4 pb-2 border-b border-slate-100">
              <CardTitle className="text-xs font-bold uppercase text-slate-600">TDS Withholding Status</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span>Quarter Q2 (Jul-Sep):</span>
                <Badge variant="success">DEPOSITED</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Return Form 26Q:</span>
                <Badge variant="success">READY</Badge>
              </div>
              <p className="text-[11px] text-slate-400 pt-1">Due date: 31st Oct</p>
            </CardContent>
          </Card>

          <Card className="border border-slate-200 shadow-sm">
            <CardHeader className="p-4 pb-2 border-b border-slate-100">
              <CardTitle className="text-xs font-bold uppercase text-slate-600">Income Tax Return</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span>Assessment Year:</span>
                <span className="font-bold text-slate-800">AY 2025-26</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Data Collection:</span>
                <Badge variant="medium">85% COMPLETE</Badge>
              </div>
              <p className="text-[11px] text-slate-400 pt-1">AIS / Form 26AS Scrutiny Matched</p>
            </CardContent>
          </Card>
        </div>

        {/* Authorized Deliverables & Signed Reports */}
        <Card className="border border-slate-200 shadow-sm">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Authorized Deliverables & Signed Documents
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100 text-xs">
              {[
                { title: 'Signed Balance Sheet & P&L Account (FY 2023-24)', type: 'Audited Financials', date: '30 Sep 2024' },
                { title: 'Official ITR Acknowledgement Receipt (AY 2024-25)', type: 'ITR-6 Filed', date: '31 Oct 2024' },
                { title: 'Tax Audit Report Form 3CD (UDIN: 24123456ABCDEF1234)', type: 'Sec 44AB Report', date: '30 Sep 2024' },
              ].map((doc, idx) => (
                <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="space-y-0.5">
                    <p className="font-bold text-slate-900">{doc.title}</p>
                    <p className="text-[11px] text-slate-500">{doc.type} • Delivered on {doc.date}</p>
                  </div>
                  <Button size="sm" variant="secondary" className="text-xs">
                    <Download className="h-3.5 w-3.5 mr-1" />
                    Download PDF
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Message to Engagement Team */}
        <Card className="border border-slate-200 shadow-sm">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Message Your Accountant
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <form onSubmit={handleSendMessage} className="space-y-3">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={2}
                placeholder="Ask your CA a question regarding GST, tax notices, or document queries..."
                className="w-full text-xs border border-slate-300 rounded-md p-2.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
              <div className="flex justify-end">
                <Button type="submit" size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs">
                  Send Message
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

