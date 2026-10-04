'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Modal } from '@/components/ui/Modal';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Badge } from '@/components/ui/Badge';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SupportPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [priority, setPriority] = useState('normal');
  const [open, setOpen] = useState<any>(null);
  const [reply, setReply] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.getSupportTickets();
      setTickets(r || []);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const r = await api.createSupportTicket({ subject, body, priority });
      toast.success(`Ticket ${r.reference} created`);
      setShowModal(false);
      setSubject('');
      setBody('');
      load();
    } catch {
      toast.error('Failed to create ticket');
    }
  };

  const view = async (id: string) => {
    try {
      setOpen(await api.getSupportTicket(id));
    } catch {
      toast.error('Failed to open ticket');
    }
  };

  const sendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.replySupportTicket(open.id, reply);
      toast.success('Reply sent');
      setReply('');
      view(open.id);
      load();
    } catch {
      toast.error('Reply failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-4xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Help & Support</h2>
            <p className="text-gray-500 mt-1">Internal ticket desk — no Zendesk/Intercom needed</p>
          </div>
          <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-2" />New ticket</Button>
        </div>

        <Card>
          <CardHeader><CardTitle>Your tickets ({tickets.length})</CardTitle></CardHeader>
          <CardContent className="p-0">
            {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
            : tickets.length === 0 ? (
              <EmptyState title="No tickets" body="Report a problem, ask a question or request a feature." action={<Button onClick={() => setShowModal(true)}>Open a ticket</Button>} />
            ) : (
              <ul className="divide-y divide-gray-100">
                {tickets.map((t: any) => (
                  <li key={t.id}>
                    <button className="w-full text-left px-4 py-3 hover:bg-gray-50 flex justify-between items-center" onClick={() => view(t.id)}>
                      <span className="text-sm font-medium">{t.subject} <span className="text-gray-400 font-normal">· {t.messages} messages</span></span>
                      <span className="flex gap-2"><Badge variant="medium">{t.priority}</Badge><Badge variant={t.status === 'closed' ? 'success' : 'info'}>{t.status}</Badge></span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="New support ticket">
          <form onSubmit={create} className="space-y-4">
            <Input label="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} required />
            <Input label="Describe the issue" value={body} onChange={(e) => setBody(e.target.value)} required />
            <Select label="Priority" value={priority} onChange={(e) => setPriority(e.target.value)} options={[
              { value: 'low', label: 'Low' }, { value: 'normal', label: 'Normal' },
              { value: 'high', label: 'High' }, { value: 'urgent', label: 'Urgent' },
            ]} />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" type="button" onClick={() => setShowModal(false)}>Cancel</Button>
              <Button type="submit">Submit</Button>
            </div>
          </form>
        </Modal>

        <Modal isOpen={!!open} onClose={() => setOpen(null)} title={open?.subject || ''} size="lg">
          {open && (
            <div className="space-y-3">
              {(open.messages || []).map((m: any, i: number) => (
                <div key={i} className={`text-sm p-3 rounded-lg ${m.from === 'support' ? 'bg-blue-50' : 'bg-gray-50'}`}>
                  <p className="text-xs text-gray-500 mb-1">{m.from} · {String(m.created_at).slice(0, 16)}</p>
                  <p>{m.body}</p>
                </div>
              ))}
              {open.status !== 'closed' && (
                <form onSubmit={sendReply} className="flex gap-2">
                  <Input value={reply} onChange={(e) => setReply(e.target.value)} placeholder="Write a reply…" aria-label="Reply" />
                  <Button type="submit">Send</Button>
                </form>
              )}
            </div>
          )}
        </Modal>
      </div>
    </DashboardLayout>
  );
}

