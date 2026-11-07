'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading } from '@/components/ui/State';
import {
  Receipt,
  FileCheck2,
  AlertTriangle,
  RefreshCw,
  Search,
  ExternalLink,
  CheckCircle2,
  Layers,
  ArrowRight,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function GSTPracticeDeskPage() {
  const [portfolio, setPortfolio] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [reconResults, setReconResults] = useState<any>(null);
  const [runningRecon, setRunningRecon] = useState(false);

  const loadPortfolio = async () => {
    setLoading(true);
    try {
      const res = await api.getGSTPracticePortfolio();
      setPortfolio(res?.portfolio || []);
    } catch {
      toast.error('Failed to load GST portfolio');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolio();
  }, []);

  const handleRunReconDemo = async () => {
    setRunningRecon(true);
    try {
      // Synthetic demo dataset for 8-way matching verification
      const sampleBooks = [
        { invoice_number: 'INV-2024-001', vendor_gstin: '27AABCS1429B1ZB', total_tax: 18000, is_blocked_17_5: false },
        { invoice_number: 'INV-2024-002', vendor_gstin: '27AABCT2411C1ZC', total_tax: 24500, is_blocked_17_5: false },
        { invoice_number: 'INV-2024-003', vendor_gstin: '27AABCL3890D1ZD', total_tax: 5400, is_blocked_17_5: true, category: 'motor_vehicles' },
        { invoice_number: 'INV-2024-004', vendor_gstin: '27AABCE4109E1ZE', total_tax: 32000, is_blocked_17_5: false },
      ];
      const sample2B = [
        { invoice_number: 'INV-2024-001', vendor_gstin: '27AABCS1429B1ZB', total_tax: 18000 }, // MATCHED
        { invoice_number: 'INV-2024-002', vendor_gstin: '27AABCT2411C1ZC', total_tax: 21000 }, // VALUE_MISMATCH (24500 vs 21000)
        { invoice_number: 'INV-2024-999', vendor_gstin: '27AABCZ9999Z1ZZ', total_tax: 12000 }, // MISSING_IN_BOOKS
      ];

      const res = await api.run8WayGSTRecon({
        books_records: sampleBooks,
        portal_2b_records: sample2B,
      });
      setReconResults(res);
      toast.success('8-Way Reconciliation Completed!');
    } catch {
      toast.error('Reconciliation failed');
    } finally {
      setRunningRecon(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">GST Practice Desk</h1>
            <p className="text-xs text-slate-500">Practice-wide client GST portfolio, 8-way GSTR-2B reconciliation, and IMS review</p>
          </div>
          <Button
            size="sm"
            onClick={handleRunReconDemo}
            disabled={runningRecon}
            className="bg-emerald-600 hover:bg-emerald-500 text-white"
          >
            <RefreshCw className={`h-4 w-4 mr-1.5 ${runningRecon ? 'animate-spin' : ''}`} />
            Run 8-Way Recon Engine
          </Button>
        </div>

        {/* 8-Way Recon Output (When triggered) */}
        {reconResults && (
          <Card className="border-2 border-emerald-500 shadow-md bg-white">
            <CardHeader className="bg-emerald-50/70 border-b border-emerald-100 px-5 py-3.5 flex flex-row items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-emerald-600" />
                <CardTitle className="text-sm font-bold text-emerald-950">
                  8-Way GSTR-2B Reconciliation Engine Report
                </CardTitle>
              </div>
              <Badge variant="success">{reconResults.matched_count} Matched / {reconResults.exception_count} Exceptions</Badge>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-emerald-50 p-2.5 rounded border border-emerald-200">
                  <p className="text-slate-500 font-semibold uppercase text-[10px]">1. MATCHED</p>
                  <p className="text-lg font-bold text-emerald-800">{reconResults.matched?.length || 0}</p>
                </div>
                <div className="bg-rose-50 p-2.5 rounded border border-rose-200">
                  <p className="text-slate-500 font-semibold uppercase text-[10px]">2. MISSING IN 2B</p>
                  <p className="text-lg font-bold text-rose-800">{reconResults.missing_in_portal_data?.length || 0}</p>
                </div>
                <div className="bg-amber-50 p-2.5 rounded border border-amber-200">
                  <p className="text-slate-500 font-semibold uppercase text-[10px]">3. VALUE MISMATCH</p>
                  <p className="text-lg font-bold text-amber-800">{reconResults.value_mismatches?.length || 0}</p>
                </div>
                <div className="bg-purple-50 p-2.5 rounded border border-purple-200">
                  <p className="text-slate-500 font-semibold uppercase text-[10px]">4. BLOCKED SEC 17(5)</p>
                  <p className="text-lg font-bold text-purple-800">{reconResults.itc_review_required?.length || 0}</p>
                </div>
              </div>

              <div className="text-xs space-y-2">
                <p className="font-bold text-slate-800">Identified Discrepancies & Recommendations:</p>
                {reconResults.missing_in_portal_data?.map((m: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-slate-50 rounded border border-slate-200 flex justify-between items-center">
                    <div>
                      <span className="font-bold text-slate-900">{m.invoice_number}</span> — Vendor hasn&apos;t filed in GSTR-1.
                      <span className="text-rose-600 font-medium"> Tax at Risk: ₹{m.total_tax?.toLocaleString('en-IN')}</span>
                    </div>
                    <Button size="sm" variant="secondary" className="text-xs">
                      Send Vendor WhatsApp
                    </Button>
                  </div>
                ))}
                {reconResults.itc_review_required?.map((m: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-purple-50 rounded border border-purple-200 flex justify-between items-center text-purple-900">
                    <div>
                      <span className="font-bold">{m.books?.invoice_number}</span> — Blocked under Section 17(5) ({m.books?.category}). Ineligible for ITC.
                    </div>
                    <Badge variant="medium">Ineligible ITC</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* GST Client Portfolio */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              All Clients GST Compliance Portfolio
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : portfolio.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                No GST registered clients found. Register clients with GSTIN in Client Master.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                    <tr>
                      <th className="py-3 px-4">Client</th>
                      <th className="py-3 px-4">GSTIN</th>
                      <th className="py-3 px-4">Frequency</th>
                      <th className="py-3 px-4">GSTR-1</th>
                      <th className="py-3 px-4">GSTR-3B</th>
                      <th className="py-3 px-4">2B Recon</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {portfolio.map((p) => (
                      <tr key={p.client_id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-bold text-slate-900">{p.client_name}</td>
                        <td className="py-3 px-4 font-mono text-slate-700">{p.gstin}</td>
                        <td className="py-3 px-4 capitalize">{p.frequency}</td>
                        <td className="py-3 px-4">
                          <Badge variant={p.gstr1_status === 'FILED' ? 'success' : 'medium'}>
                            {p.gstr1_status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant={p.gstr3b_status === 'FILED' ? 'success' : 'danger'}>
                            {p.gstr3b_status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <span className="flex items-center gap-1 text-emerald-700 font-semibold">
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                            {p.recon_status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button size="sm" variant="secondary" className="text-xs">
                            Review Filing
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

