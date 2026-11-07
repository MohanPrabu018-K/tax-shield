'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading } from '@/components/ui/State';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  UserCheck,
  FileText,
  Clock,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MakerCheckerReviewQueuePage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadReviews = async () => {
    setLoading(true);
    try {
      const rows = await api.getProfessionalTasks({ status: 'UNDER_REVIEW' });
      setTasks(rows || []);
    } catch {
      toast.error('Failed to load review queue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, []);

  const handleApprove = async (tid: string) => {
    try {
      await api.transitionTask(tid, 'APPROVED', 'Partner sign-off granted under firm quality control.');
      toast.success('Work approved and signed off by Partner');
      loadReviews();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Approval failed: Preparer cannot approve own work.');
    }
  };

  const handleRequestRework = async (tid: string) => {
    const notes = prompt('Enter review notes / correction required:');
    if (!notes) return;
    try {
      await api.transitionTask(tid, 'REVIEW_NOTES_RAISED', notes);
      toast.success('Review notes recorded. Work returned for staff correction.');
      loadReviews();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to update review');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900">Maker-Checker Review Queue</h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-800 border border-purple-200">
              ICAI SQC-1 QUALITY CONTROL
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Standard Quality Control: Prepared work submitted by staff must receive independent partner scrutiny prior to filing
          </p>
        </div>

        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Pending Partner Approval Queue ({tasks.length})
            </CardTitle>
            <span className="text-xs text-slate-500">Independent review enforced</span>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : tasks.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500 space-y-2">
                <CheckCircle2 className="h-8 w-8 text-emerald-500 mx-auto" />
                <p className="font-bold text-slate-800 text-sm">Review Queue is Clear!</p>
                <p>All prepared client filings and audit schedules have been reviewed.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {tasks.map((t) => (
                  <div key={t.id || t._id} className="p-4 hover:bg-slate-50/70 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="medium">{t.service_category?.toUpperCase()}</Badge>
                        <span className="text-xs font-bold text-slate-900">{t.title}</span>
                      </div>
                      <p className="text-xs text-slate-600">
                        Client: <strong className="text-slate-900">{t.client_name || 'Acme Industrial'}</strong> • Prepared by:{' '}
                        <span className="font-semibold text-blue-700">{t.assigned_to || 'Staff Accountant'}</span>
                      </p>
                      {t.checklist && (
                        <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                          <span>Preparer completed all {t.checklist.length} verification checklist items</span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleRequestRework(t.id || t._id)}
                        className="text-xs text-amber-700 hover:bg-amber-50 border-amber-200"
                      >
                        <RotateCcw className="h-3.5 w-3.5 mr-1" />
                        Raise Notes / Rework
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleApprove(t.id || t._id)}
                        className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                      >
                        <ShieldCheck className="h-3.5 w-3.5 mr-1" />
                        Grant Partner Sign-off
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

