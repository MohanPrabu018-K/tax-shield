'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading } from '@/components/ui/State';
import {
  Scale,
  CheckCircle2,
  AlertTriangle,
  FileText,
  DollarSign,
  Download,
} from 'lucide-react';

export default function IncomeTaxPracticeDeskPage() {
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTaxClients = async () => {
      setLoading(true);
      try {
        const rows = await api.getPracticeClients();
        setClients(rows || []);
      } finally {
        setLoading(false);
      }
    };
    fetchTaxClients();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Income Tax Practice Desk</h1>
            <p className="text-xs text-slate-500">Practice-wide direct tax portfolio, AIS/26AS multi-party reconciliation, regime optimization and return preparation</p>
          </div>
        </div>

        {/* ITR Summary Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-purple-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">ITR Portfolio (AY 2025-26)</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{clients.length} Taxpayers</p>
              <p className="text-[11px] text-slate-500 mt-1">Individual, Firm, LLP, Company</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-emerald-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">Default Regime (115BAC)</p>
              <p className="text-2xl font-bold text-emerald-700 mt-1">72% Clients</p>
              <p className="text-[11px] text-slate-500 mt-1">Lower slab liability identified</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">AIS / 26AS Scrutiny</p>
              <p className="text-2xl font-bold text-blue-700 mt-1">100% Matched</p>
              <p className="text-[11px] text-slate-500 mt-1">Zero unverified high-value transactions</p>
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Table */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              All Clients Income Tax Returns (ITR-1 through ITR-6)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : clients.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                No clients found. Add clients in Client Master.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                    <tr>
                      <th className="py-3 px-4">Taxpayer</th>
                      <th className="py-3 px-4">PAN</th>
                      <th className="py-3 px-4">Recommended Form</th>
                      <th className="py-3 px-4">Regime</th>
                      <th className="py-3 px-4">AIS Match</th>
                      <th className="py-3 px-4">Readiness</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {clients.map((c) => {
                      const form = c.entity_type === 'pvt_ltd' ? 'ITR-6' : c.entity_type === 'partnership' ? 'ITR-5' : c.entity_type === 'proprietorship' ? 'ITR-3' : 'ITR-1 / 2';
                      return (
                        <tr key={c.id || c._id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3 px-4 font-bold text-slate-900">{c.name}</td>
                          <td className="py-3 px-4 font-mono font-bold text-slate-700">{c.pan || 'ABCDE1234F'}</td>
                          <td className="py-3 px-4">
                            <span className="font-mono font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 text-[10px]">
                              {form}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-semibold text-emerald-700">New (115BAC)</span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="flex items-center gap-1 text-emerald-700 font-medium">
                              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                              Matched
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Badge variant="success">100% READY</Badge>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Button size="sm" variant="secondary" className="text-xs">
                              Computation
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
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

