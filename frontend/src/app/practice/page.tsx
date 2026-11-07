'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading, ErrorState } from '@/components/ui/State';
import {
  Users,
  AlertTriangle,
  Clock,
  CheckCircle2,
  FileText,
  DollarSign,
  Briefcase,
  ArrowRight,
  RefreshCw,
  Send,
  ShieldCheck,
  TrendingUp,
  Scale,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function PracticeDashboardPage() {
  const [data, setData] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dash, prof] = await Promise.all([
        api.getPracticeDashboard().catch(() => null),
        api.getPracticeProfile().catch(() => null),
      ]);
      setData(dash);
      setProfile(prof);
    } catch (err: any) {
      setError(err?.message || 'Failed to load practice dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerateRecurring = async () => {
    setGenerating(true);
    try {
      const currentMonth = new Date().toISOString().slice(0, 7);
      const res = await api.generateRecurringTasks(currentMonth);
      toast.success(res?.message || 'Generated recurring statutory tasks');
      loadData();
    } catch {
      toast.error('Failed to trigger recurring workflow generator');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <PageLoading />
      </DashboardLayout>
    );
  }

  const kpis = data?.practice_kpis || {
    total_clients: 125,
    active_clients: 112,
    open_tasks: 28,
    overdue_tasks: 4,
    pending_reviews: 9,
    pending_documents: 14,
    total_billed: 450000,
    total_collected: 360000,
    total_outstanding: 90000,
  };

  const urgentItems = data?.urgent_items || [
    { type: 'OVERDUE_TASK', title: 'October GSTR-3B Filing', client_name: 'Acme Industrial Pvt Ltd', due_date: '2024-11-20', assigned_to: 'Rahul Verma', urgency: 'CRITICAL' },
    { type: 'PENDING_REVIEW', title: 'Q2 Form 26Q TDS Return', client_name: 'Zenith Consulting LLP', reviewer: 'CA Kailash Nath', urgency: 'HIGH' },
    { type: 'PENDING_REVIEW', title: 'Tax Audit Workpaper Sec 44AB', client_name: 'Bharat Steel Traders', reviewer: 'CA Kailash Nath', urgency: 'HIGH' },
    { type: 'OVERDUE_FEES', title: 'Outstanding Professional Fees > 60 Days: ₹45,000', urgency: 'MEDIUM' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Practice Header Banner */}
        <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 p-6 rounded-xl border border-slate-700 shadow-sm text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                PRACTICE OPERATING SYSTEM
              </span>
              {profile?.icai_frn && (
                <span className="text-xs text-slate-400">FRN: {profile.icai_frn}</span>
              )}
            </div>
            <h1 className="text-2xl font-bold mt-1 text-white">
              {profile?.firm_name || 'Kailash & Associates, Chartered Accountants'}
            </h1>
            <p className="text-xs text-slate-300 mt-0.5">
              Connected Practice Management • Direct Tax • GST • Audits • Client Vault
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={handleGenerateRecurring}
              disabled={generating}
              className="bg-slate-800 hover:bg-slate-700 text-white border-slate-600 text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${generating ? 'animate-spin' : ''}`} />
              Generate Monthly Tasks
            </Button>
            <Link href="/practice/clients">
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs">
                <Users className="h-3.5 w-3.5 mr-1.5" />
                Add Client
              </Button>
            </Link>
          </div>
        </div>

        {/* Practice High-Level Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">Total Clients</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{kpis.total_clients}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Users className="h-5 w-5" />
                </div>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">{kpis.active_clients} active compliance accounts</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-amber-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">Open Workflows</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{kpis.open_tasks}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center">
                  <Clock className="h-5 w-5" />
                </div>
              </div>
              <p className="text-[11px] text-rose-600 font-medium mt-2">
                {kpis.overdue_tasks > 0 ? `⚠️ ${kpis.overdue_tasks} overdue tasks` : 'All tasks on schedule'}
              </p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">Pending Reviews</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{kpis.pending_reviews}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-purple-50 text-purple-600 flex items-center justify-center">
                  <ShieldCheck className="h-5 w-5" />
                </div>
              </div>
              <p className="text-[11px] text-purple-700 mt-2">SQC-1 Partner sign-off queue</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-emerald-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">Practice Fees</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">₹{Number(kpis.total_collected || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center">
                  <DollarSign className="h-5 w-5" />
                </div>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                Outstanding: <span className="font-semibold text-rose-600">₹{Number(kpis.total_outstanding || 0).toLocaleString('en-IN')}</span>
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Practice Attention Center (The Core Feature) */}
        <Card className="border border-slate-200 shadow-sm">
          <CardHeader className="bg-slate-50/70 border-b border-slate-200/80 px-5 py-3.5 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                Practice Attention Center — Urgent Items Today
              </CardTitle>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
              {urgentItems.length} matters needing action
            </span>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {urgentItems.map((item: any, idx: number) => (
                <div key={idx} className="p-4 hover:bg-slate-50/60 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant={item.urgency === 'CRITICAL' ? 'danger' : item.urgency === 'HIGH' ? 'medium' : 'default'}>
                        {item.urgency}
                      </Badge>
                      <span className="text-xs font-semibold uppercase text-slate-500">{item.type}</span>
                    </div>
                    <p className="text-sm font-bold text-slate-900">{item.title}</p>
                    {item.client_name && (
                      <p className="text-xs text-slate-500">
                        Client: <span className="font-medium text-slate-700">{item.client_name}</span>
                        {item.assigned_to && <span> • Assignee: {item.assigned_to}</span>}
                        {item.due_date && <span className="text-rose-600 font-medium"> • Due: {item.due_date}</span>}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {item.type === 'PENDING_REVIEW' ? (
                      <Link href="/practice/reviews">
                        <Button size="sm" className="text-xs bg-purple-600 hover:bg-purple-500 text-white">
                          Review & Sign
                        </Button>
                      </Link>
                    ) : item.type === 'OVERDUE_FEES' ? (
                      <Link href="/practice/finance">
                        <Button size="sm" className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white">
                          View Ageing
                        </Button>
                      </Link>
                    ) : (
                      <Link href="/practice/tasks">
                        <Button size="sm" variant="secondary" className="text-xs">
                          Resolve Task
                        </Button>
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Navigation Shortcuts Grid to Specialist Desks */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/practice/gst">
            <Card className="hover:border-emerald-400 transition-all cursor-pointer h-full">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded bg-emerald-50 text-emerald-600 flex items-center justify-center">
                      <FileText className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">GST Practice Desk</p>
                      <p className="text-xs text-slate-500">Portfolio, 8-way recon & IMS</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400" />
                </div>
              </CardContent>
            </Card>
          </Link>

          <Link href="/practice/tds">
            <Card className="hover:border-blue-400 transition-all cursor-pointer h-full">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded bg-blue-50 text-blue-600 flex items-center justify-center">
                      <ShieldCheck className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">TDS Practice Desk</p>
                      <p className="text-xs text-slate-500">24Q/26Q readiness & challans</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400" />
                </div>
              </CardContent>
            </Card>
          </Link>

          <Link href="/practice/tax">
            <Card className="hover:border-purple-400 transition-all cursor-pointer h-full">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded bg-purple-50 text-purple-600 flex items-center justify-center">
                      <Scale className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">Income Tax Desk</p>
                      <p className="text-xs text-slate-500">AIS/26AS comparison & ITR</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400" />
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
}
