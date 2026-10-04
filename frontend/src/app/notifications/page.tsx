'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import toast from 'react-hot-toast';

export default function NotificationsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.getNotifications(filter === 'unread');
      setItems(r.notifications || []);
      setUnread(r.unread || 0);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const mark = async (id: string, read: boolean) => {
    try {
      await api.markNotification(id, read);
      load();
    } catch {
      toast.error('Update failed');
    }
  };

  const markAll = async () => {
    try {
      const r = await api.markAllNotificationsRead();
      toast.success(`${r.count} marked read`);
      load();
    } catch {
      toast.error('Update failed');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-3xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Notifications {unread > 0 && <Badge variant="danger">{unread} unread</Badge>}</h2>
            <p className="text-gray-500 mt-1">In-app only — no paid email or SMS providers, by design</p>
          </div>
          <Button variant="secondary" size="sm" onClick={markAll}>Mark all read</Button>
        </div>

        <div className="flex gap-2" role="tablist" aria-label="Filter">
          {(['all', 'unread'] as const).map((f) => (
            <button key={f} role="tab" aria-selected={filter === f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-full text-sm border ${filter === f ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'}`}>
              {f === 'all' ? 'All' : 'Unread'}
            </button>
          ))}
        </div>

        <Card>
          <CardContent className="p-0">
            {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={load} />
            : items.length === 0 ? (
              <EmptyState title="All caught up" body="Security, billing, compliance and document alerts appear here." />
            ) : (
              <ul className="divide-y divide-gray-100">
                {items.map((a: any) => (
                  <li key={a.id} className={`px-4 py-3 flex items-start gap-3 ${a.read ? 'opacity-60' : ''}`}>
                    <Badge variant={a.severity === 'high' ? 'danger' : a.severity === 'medium' ? 'medium' : 'info'}>{a.category}</Badge>
                    <div className="flex-1 text-sm">
                      <p className="font-medium">{a.title}</p>
                      {a.body && <p className="text-gray-500">{a.body}</p>}
                      <p className="text-xs text-gray-400">{String(a.created_at).slice(0, 16)}</p>
                      {a.link && <Link href={a.link} className="text-primary-700 hover:underline text-xs">Open →</Link>}
                    </div>
                    {!a.read && (
                      <button className="text-xs text-primary-700 hover:underline" onClick={() => mark(a.id, true)}>Mark read</button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
