'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export default function PracticePage() {
  const [overview, setOverview] = useState<any>(null);
  const [clients, setClients] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);
  const [docreqs, setDocreqs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showClient, setShowClient] = useState(false);
  const [showTask, setShowTask] = useState(false);
  const [showReq, setShowReq] = useState(false);
  const [clientName, setClientName] = useState('');
  const [taskTitle, setTaskTitle] = useState('');
  const [taskClient, setTaskClient] = useState('');
  const [reqClient, setReqClient] = useState('');
  const [reqItems, setReqItems] = useState('Bank statement, Sales invoices');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ov, cl, tk] = await Promise.all([
        api.getPracticeOverview(), api.getClients(), api.getTasks(),
      ]);
      setOverview(ov);
      setClients(cl);
      setTasks(tk);
      const [rv, dq] = await Promise.all([
        api.getReviews().catch(() => []),
        api.getDocRequests().catch(() => []),
      ]);
      setReviews(rv);
      setDocreqs(dq);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load practice');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const addClient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createClient({ name: clientName });
      toast.success('Client added — data stays isolated per client');
      setShowClient(false);
      setClientName('');
      load();
    } catch {
      toast.error('Failed to add client');
    }
  };

  const addTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createTask({ title: taskTitle, client: taskClient });
      toast.success('Task created');
      setShowTask(false);
      setTaskTitle('');
      setTaskClient('');
      load();
    } catch {
      toast.error('Failed to create task');
    }
  };

  const addReq = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createDocRequest({
        client: reqClient, items: reqItems.split(',').map((s) => s.trim()).filter(Boolean),
      });
      toast.success('Document request sent');
      setShowReq(false);
      load();
    } catch {
      toast.error('Failed to send request');
    }
  };

  const advanceReview = async (id: string, to: string) => {
    try {
      await api.transitionReview(id, to);
      toast.success(`Review → ${to}`);
      load();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Illegal transition — backend enforces the chain');
    }
  };

  const completeTask = async (id: string) => {
    try {
      await api.updateTask(id, 'done');
      load();
    } catch {
      toast.error('Update failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">CA Practice</h2>
          <p className="text-gray-500 mt-1">Clients, tasks, document requests and reviews — client data never leaks across clients</p>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {[['Clients', overview?.clients], ['Open tasks', overview?.open_tasks], ['Pending reviews', overview?.pending_reviews]].map(([k, v]) => (
            <Card key={k as string}><CardContent>
              <p className="text-xs uppercase text-gray-500">{k}</p>
              <p className="text-xl font-bold">{v ?? '—'}</p>
            </CardContent></Card>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Clients ({clients.length})</CardTitle></CardHeader>
            <CardContent>
              {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} /> : (
                <>
                  <Button size="sm" onClick={() => setShowClient(true)}><Plus className="h-4 w-4 mr-1" />Add client</Button>
                  <ul className="mt-3 space-y-1 text-sm">
                    {clients.map((c: any) => (
                      <li key={c.id} className="border-b border-gray-100 py-1 font-medium">{c.name}</li>
                    ))}
                    {clients.length === 0 && <li className="text-gray-500">No clients yet.</li>}
                  </ul>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Tasks ({tasks.length})</CardTitle></CardHeader>
            <CardContent>
              <Button size="sm" onClick={() => setShowTask(true)}><Plus className="h-4 w-4 mr-1" />Add task</Button>
              <ul className="mt-3 space-y-1 text-sm">
                {tasks.slice(0, 10).map((t: any) => (
                  <li key={t.id} className="flex justify-between border-b border-gray-100 py-1">
                    <span>{t.title} <span className="text-gray-400">· {t.client}</span> <Badge variant={t.status === 'done' ? 'success' : 'medium'}>{t.status}</Badge></span>
                    {t.status !== 'done' && <button className="text-primary-700 hover:underline" onClick={() => completeTask(t.id)}>Done</button>}
                  </li>
                ))}
                {tasks.length === 0 && <li className="text-gray-500">No tasks.</li>}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Document requests ({docreqs.length})</CardTitle></CardHeader>
            <CardContent>
              <Button size="sm" onClick={() => setShowReq(true)}><Plus className="h-4 w-4 mr-1" />Request documents</Button>
              <ul className="mt-3 space-y-1 text-sm">
                {docreqs.slice(0, 10).map((d: any) => (
                  <li key={d.id} className="border-b border-gray-100 py-1">
                    <span className="font-medium">{d.client}</span> · {(d.items || []).join(', ')} · <Badge variant="medium">{d.status}</Badge>
                  </li>
                ))}
                {docreqs.length === 0 && <li className="text-gray-500">No requests.</li>}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Reviews ({reviews.length})</CardTitle></CardHeader>
            <CardContent>
              {(reviews.length === 0 ? <p className="text-sm text-gray-500">No items in review. Chain: auto → needs_review → accountant/ca → approved.</p> : (
                <ul className="space-y-1 text-sm">
                  {reviews.slice(0, 10).map((r: any) => (
                    <li key={r.id} className="flex justify-between border-b border-gray-100 py-1">
                      <span>{r.entity} <Badge variant="medium">{r.state}</Badge></span>
                      <span className="flex gap-1">
                        {['needs_review', 'accountant', 'ca', 'approved'].filter((s) => s !== r.state).slice(0, 2).map((s) => (
                          <button key={s} className="text-primary-700 hover:underline" onClick={() => advanceReview(r.id, s)}>{s}</button>
                        ))}
                      </span>
                    </li>
                  ))}
                </ul>
              ))}
            </CardContent>
          </Card>
        </div>

        <Modal isOpen={showClient} onClose={() => setShowClient(false)} title="Add client">
          <form onSubmit={addClient} className="space-y-4">
            <Input label="Client name" value={clientName} onChange={(e) => setClientName(e.target.value)} required />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setShowClient(false)}>Cancel</Button>
              <Button type="submit">Save</Button>
            </div>
          </form>
        </Modal>

        <Modal isOpen={showTask} onClose={() => setShowTask(false)} title="Add task">
          <form onSubmit={addTask} className="space-y-4">
            <Input label="Title" value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} required />
            <Input label="Client" value={taskClient} onChange={(e) => setTaskClient(e.target.value)} />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setShowTask(false)}>Cancel</Button>
              <Button type="submit">Save</Button>
            </div>
          </form>
        </Modal>

        <Modal isOpen={showReq} onClose={() => setShowReq(false)} title="Request documents">
          <form onSubmit={addReq} className="space-y-4">
            <Input label="Client" value={reqClient} onChange={(e) => setReqClient(e.target.value)} required />
            <Input label="Items (comma separated)" value={reqItems} onChange={(e) => setReqItems(e.target.value)} required />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setShowReq(false)}>Cancel</Button>
              <Button type="submit">Send request</Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

