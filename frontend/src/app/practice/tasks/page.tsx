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
  ClipboardCheck,
  Plus,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Filter,
} from 'lucide-react';
import toast from 'react-hot-toast';

const STATUS_OPTIONS = [
  'NOT_STARTED',
  'AWAITING_CLIENT',
  'DOCUMENTS_RECEIVED',
  'IN_PROGRESS',
  'PREPARED',
  'UNDER_REVIEW',
  'REVIEW_NOTES_RAISED',
  'REWORK',
  'APPROVED',
  'COMPLETED',
  'ON_HOLD',
  'CANCELLED',
];

export default function ProfessionalTasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // New task form
  const [title, setTitle] = useState('');
  const [clientName, setClientName] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState('high');
  const [assignedTo, setAssignedTo] = useState('Rahul Verma');
  const [serviceCategory, setServiceCategory] = useState('gst');

  const loadTasks = async () => {
    setLoading(true);
    try {
      const rows = await api.getProfessionalTasks({ status: filterStatus });
      setTasks(rows || []);
    } catch {
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [filterStatus]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createProfessionalTask({
        title,
        client_name: clientName,
        due_date: dueDate,
        priority,
        assigned_to: assignedTo,
        service_category: serviceCategory,
      });
      toast.success('Task created successfully');
      setShowAddModal(false);
      setTitle('');
      setClientName('');
      loadTasks();
    } catch {
      toast.error('Failed to create task');
    }
  };

  const handleTransition = async (tid: string, target: string) => {
    try {
      await api.transitionTask(tid, target);
      toast.success(`Task status updated to ${target}`);
      loadTasks();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Illegal transition under firm policy');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Professional Task Management</h1>
            <p className="text-xs text-slate-500">12-stage auditable workflow with checklist verification and SQC-1 Maker-Checker compliance</p>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Create Task
          </Button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="font-semibold text-slate-500 flex items-center gap-1">
            <Filter className="h-3.5 w-3.5" /> Status:
          </span>
          <button
            onClick={() => setFilterStatus('')}
            className={`px-2.5 py-1 rounded-md font-medium whitespace-nowrap ${filterStatus === '' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}
          >
            All
          </button>
          {['IN_PROGRESS', 'UNDER_REVIEW', 'APPROVED', 'COMPLETED', 'AWAITING_CLIENT'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-2.5 py-1 rounded-md font-medium whitespace-nowrap ${filterStatus === st ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Tasks List */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : tasks.length === 0 ? (
              <div className="p-12 text-center text-slate-500 text-xs">
                No tasks found in this view.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {tasks.map((t) => (
                  <div key={t.id || t._id} className="p-4 hover:bg-slate-50/80 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={t.priority === 'high' ? 'danger' : 'medium'}>{t.priority}</Badge>
                        <span className="text-[10px] uppercase font-bold text-slate-400 font-mono">{t.task_code || 'TSK'}</span>
                        <Badge variant="default">{t.status}</Badge>
                      </div>
                      <h3 className="text-sm font-bold text-slate-900">{t.title}</h3>
                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                        <span>Client: <strong className="text-slate-800">{t.client_name || 'Acme'}</strong></span>
                        <span>Assignee: <strong className="text-slate-800">{t.assigned_to}</strong></span>
                        {t.due_date && <span className="text-rose-600 font-medium">Due: {t.due_date}</span>}
                      </div>

                      {/* Checklist Summary */}
                      {t.checklist && (
                        <div className="pt-1 flex items-center gap-2 text-[11px] text-slate-500">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                          <span>
                            {t.checklist.filter((c: any) => c.done).length} / {t.checklist.length} checklist items completed
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Quick State Transitions */}
                    <div className="flex items-center gap-2 shrink-0">
                      {t.status === 'NOT_STARTED' && (
                        <Button size="sm" onClick={() => handleTransition(t.id || t._id, 'IN_PROGRESS')} className="text-xs bg-blue-600 hover:bg-blue-500 text-white">
                          Start Work
                        </Button>
                      )}
                      {t.status === 'IN_PROGRESS' && (
                        <Button size="sm" onClick={() => handleTransition(t.id || t._id, 'PREPARED')} className="text-xs bg-purple-600 hover:bg-purple-500 text-white">
                          Mark Prepared
                        </Button>
                      )}
                      {t.status === 'PREPARED' && (
                        <Button size="sm" onClick={() => handleTransition(t.id || t._id, 'UNDER_REVIEW')} className="text-xs bg-amber-600 hover:bg-amber-500 text-white">
                          Submit for CA Review
                        </Button>
                      )}
                      {t.status === 'UNDER_REVIEW' && (
                        <Button size="sm" onClick={() => handleTransition(t.id || t._id, 'APPROVED')} className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white">
                          Approve (CA)
                        </Button>
                      )}
                      {t.status === 'APPROVED' && (
                        <Button size="sm" onClick={() => handleTransition(t.id || t._id, 'COMPLETED')} className="text-xs bg-slate-800 hover:bg-slate-700 text-white">
                          Mark Completed
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Create Task Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Create Workflow Task">
          <form onSubmit={handleCreateTask} className="space-y-4 text-xs">
            <Input label="Task Title" value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="e.g. October GSTR-3B Computation" />
            <Input label="Client Name" value={clientName} onChange={(e) => setClientName(e.target.value)} required placeholder="Acme Industrial Technologies" />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Due Date" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} required />
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Service Category</label>
                <select
                  value={serviceCategory}
                  onChange={(e) => setServiceCategory(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-md px-2.5 py-1.5 bg-white"
                >
                  <option value="gst">GST</option>
                  <option value="tds">TDS</option>
                  <option value="tax">Direct Tax / ITR</option>
                  <option value="audit">Tax Audit / Statutory</option>
                  <option value="accounting">Accounting / Books</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Assigned Staff" value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)} required />
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-md px-2.5 py-1.5 bg-white"
                >
                  <option value="high">High (Statutory Due Date)</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Create Task
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

