'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading } from '@/components/ui/State';
import {
  Users,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function TeamWorkloadPage() {
  const [workload, setWorkload] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadWorkload = async () => {
    setLoading(true);
    try {
      const res = await api.getTeamWorkload();
      setWorkload(res?.workload || []);
    } catch {
      toast.error('Failed to load team workload');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkload();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Staff & Team Workload Analytics</h1>
          <p className="text-xs text-slate-500">Real-time team task distribution, review bottlenecks, and workload-aware assignment capacity</p>
        </div>

        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Team Capacity & Task Distribution ({workload.length} Professionals)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : workload.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500">
                No staff members configured. Configure staff in Practice Setup.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                    <tr>
                      <th className="py-3 px-4">Staff Member</th>
                      <th className="py-3 px-4">Role & Dept</th>
                      <th className="py-3 px-4 text-center">Open Tasks</th>
                      <th className="py-3 px-4 text-center">Overdue</th>
                      <th className="py-3 px-4 text-center">In Review</th>
                      <th className="py-3 px-4">Capacity Utilization</th>
                      <th className="py-3 px-4 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {workload.map((w, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-bold text-slate-900">{w.name}</td>
                        <td className="py-3 px-4 text-slate-600 capitalize">
                          {w.role} • <span className="text-slate-400 font-medium">{w.department}</span>
                        </td>
                        <td className="py-3 px-4 text-center font-bold text-slate-800">{w.open_tasks}</td>
                        <td className="py-3 px-4 text-center">
                          {w.overdue_tasks > 0 ? (
                            <span className="font-bold text-rose-600">{w.overdue_tasks}</span>
                          ) : (
                            <span className="text-slate-400">0</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center font-semibold text-purple-700">{w.pending_reviews}</td>
                        <td className="py-3 px-4">
                          <div className="w-36 space-y-1">
                            <div className="flex justify-between text-[10px] text-slate-500">
                              <span>Load</span>
                              <span className="font-bold">{w.capacity_utilization_pct}%</span>
                            </div>
                            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                              <div
                                className={`h-1.5 rounded-full ${
                                  w.capacity_utilization_pct > 80
                                    ? 'bg-rose-500'
                                    : w.capacity_utilization_pct > 50
                                    ? 'bg-amber-500'
                                    : 'bg-emerald-500'
                                }`}
                                style={{ width: `${w.capacity_utilization_pct}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Badge variant={w.status === 'overloaded' ? 'danger' : 'success'}>
                            {w.status?.toUpperCase()}
                          </Badge>
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

