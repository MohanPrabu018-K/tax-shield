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
  BookOpen,
  Plus,
  CheckCircle2,
  FileText,
  ShieldCheck,
  FolderOpen,
  Clock,
  Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function AuditWorkpapersPage() {
  const [workpapers, setWorkpapers] = useState<any[]>([]);
  const [completeness, setCompleteness] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [title, setTitle] = useState('');
  const [section, setSection] = useState('Balance Sheet - Assets');
  const [leadSchedule, setLeadSchedule] = useState('Cash & Bank Balances');
  const [procedures, setProcedures] = useState('');
  const [observations, setObservations] = useState('');
  const [conclusion, setConclusion] = useState('Properly stated without material misstatement.');

  const loadData = async () => {
    setLoading(true);
    try {
      const [wps, comp] = await Promise.all([
        api.getWorkpapers().catch(() => []),
        api.getAuditCompleteness().catch(() => null),
      ]);
      setWorkpapers(wps || []);
      setCompleteness(comp);
    } catch {
      toast.error('Failed to load audit workpapers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateWorkpaper = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createWorkpaper({
        title,
        section,
        lead_schedule: leadSchedule,
        procedures_performed: procedures,
        observations,
        conclusion,
      });
      toast.success('Workpaper created and indexed in audit file');
      setShowAddModal(false);
      setTitle('');
      setProcedures('');
      setObservations('');
      loadData();
    } catch {
      toast.error('Failed to create workpaper');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">Audit & Workpaper Desk</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200">
                ICAI SA 230 AUDIT DOCUMENTATION
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Lead schedules, independent balance confirmations, audit programmes, and partner sign-off
            </p>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            New Workpaper
          </Button>
        </div>

        {/* Audit File Completeness Meter */}
        <Card className="border border-slate-200 shadow-sm bg-gradient-to-r from-slate-900 to-slate-800 text-white">
          <CardContent className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400">
                Standard on Auditing SA 230 Compliance
              </span>
              <h2 className="text-lg font-bold">Audit Engagement Completeness</h2>
              <p className="text-xs text-slate-300">
                Lead schedules, substantive procedures, review notes and management representations
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-3xl font-extrabold text-emerald-400">
                  {completeness?.completeness_pct ?? 100}%
                </span>
                <p className="text-[10px] text-slate-400">
                  {completeness?.is_ready_for_udin ? '✅ Ready for UDIN Generation' : 'In Progress'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Workpapers List */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Engagement Lead Schedules & Working Papers ({workpapers.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : workpapers.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500">
                No workpapers created yet. Click &quot;New Workpaper&quot; to initialize audit schedules.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {workpapers.map((w) => (
                  <div key={w.id || w._id} className="p-4 hover:bg-slate-50/70 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                          {w.workpaper_code}
                        </span>
                        <span className="text-xs font-bold text-slate-900">{w.title}</span>
                        <Badge variant="medium">{w.sign_off_status}</Badge>
                      </div>
                      <p className="text-xs text-slate-600">
                        Section: <strong className="text-slate-800">{w.section}</strong> • Lead: {w.lead_schedule}
                      </p>
                      <p className="text-[11px] text-slate-500 italic">
                        Conclusion: &quot;{w.conclusion}&quot;
                      </p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <Button size="sm" variant="secondary" className="text-xs">
                        View Evidence
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* New Workpaper Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Initialize Audit Working Paper (SA 230)">
          <form onSubmit={handleCreateWorkpaper} className="space-y-4 text-xs">
            <Input label="Workpaper Title" value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="e.g. Bank Confirmation & BRS Scrutiny" />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Audit Section" value={section} onChange={(e) => setSection(e.target.value)} required />
              <Input label="Lead Schedule" value={leadSchedule} onChange={(e) => setLeadSchedule(e.target.value)} required />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Substantive Procedures Performed</label>
              <textarea
                value={procedures}
                onChange={(e) => setProcedures(e.target.value)}
                rows={3}
                className="w-full text-xs border border-slate-300 rounded-md p-2"
                placeholder="Obtained direct confirmations, scrutinized general ledger entries, tested subsequent clearances..."
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Audit Observations & Discrepancies</label>
              <textarea
                value={observations}
                onChange={(e) => setObservations(e.target.value)}
                rows={2}
                className="w-full text-xs border border-slate-300 rounded-md p-2"
                placeholder="List any adjustments or unrecorded items noted..."
              />
            </div>

            <Input label="Auditor Conclusion" value={conclusion} onChange={(e) => setConclusion(e.target.value)} required />

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Save Workpaper
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

