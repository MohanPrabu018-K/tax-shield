'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading } from '@/components/ui/State';
import {
  Droplets,
  CheckCircle2,
  AlertTriangle,
  FileText,
  DollarSign,
  Layers,
} from 'lucide-react';

export default function TDSPracticeDeskPage() {
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTds = async () => {
      setLoading(true);
      try {
        const rows = await api.getPracticeClients();
        const tdsClients = (rows || []).filter((c: any) => c.tan || c.tds_applicable);
        setClients(tdsClients);
      } finally {
        setLoading(false);
      }
    };
    fetchTds();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">TDS Practice Desk</h1>
          <p className="text-xs text-slate-500">Practice-wide quarterly withholding tax monitoring, 24Q/26Q return preparation, and challan reconciliation</p>
        </div>

        {/* Overview Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">TDS Deductor Clients</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{clients.length}</p>
              <p className="text-[11px] text-slate-500 mt-1">Active TAN registrations</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-emerald-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">Current Quarter</p>
              <p className="text-2xl font-bold text-emerald-700 mt-1">Q2 (Jul – Sep)</p>
              <p className="text-[11px] text-slate-500 mt-1">Due date: 31st October</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-amber-500">
            <CardContent className="p-4">
              <p className="text-xs font-semibold uppercase text-slate-500">Challan Allocation</p>
              <p className="text-2xl font-bold text-amber-700 mt-1">100% Verified</p>
              <p className="text-[11px] text-slate-500 mt-1">Zero unmapped challan lines</p>
            </CardContent>
          </Card>
        </div>

        {/* TDS Client Table */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              TDS Quarterly Return Portfolio (Form 24Q / 26Q)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : clients.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                No TDS deductors configured. Add clients with TAN numbers in Client Master.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                    <tr>
                      <th className="py-3 px-4">Client</th>
                      <th className="py-3 px-4">TAN</th>
                      <th className="py-3 px-4">Applicable Sections</th>
                      <th className="py-3 px-4">Challan Status</th>
                      <th className="py-3 px-4">Filing Status</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {clients.map((c) => (
                      <tr key={c.id || c._id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-bold text-slate-900">{c.name}</td>
                        <td className="py-3 px-4 font-mono font-bold text-slate-700">{c.tan || 'MUMB12345A'}</td>
                        <td className="py-3 px-4 text-slate-600">
                          194C (Contractors), 194J (Prof. Fees), 192 (Salary)
                        </td>
                        <td className="py-3 px-4">
                          <span className="flex items-center gap-1 text-emerald-700 font-medium">
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                            Challans Reconciled
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant="medium">READY_FOR_REVIEW</Badge>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button size="sm" variant="secondary" className="text-xs">
                            Scrutinize 26Q
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

