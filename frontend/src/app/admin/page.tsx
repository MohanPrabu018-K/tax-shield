'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';

export default function AdminPage() {
  const [view, setView] = useState('overview');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [forbidden, setForbidden] = useState(false);
  const [incidentTitle, setIncidentTitle] = useState('');
  const [ruleVersion, setRuleVersion] = useState('');

  const load = async (v = view) => {
    setLoading(true);
    setForbidden(false);
    try {
      
      if (v === 'overview') setData(await api.getAdminOverview()); else if (v === 'users') setData(await api.getAdminUsers()); else if (v === 'subscriptions') setData(await api.getAdminSubscriptions()); else if (v === 'support') setData(await api.getAdminSupport()); else if (v === 'audit') setData(await api.getAdminAudit()); else if (v === 'health') setData(await api.getAdminHealth()); else if (v === 'incidents') setData(await api.getAdminIncidents());
    } catch (e: any) {
      if (e?.response?.status === 403) setForbidden(true);
      else toast.error('Admin load failed');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const go = (v: string) => { setView(v); setData(null); load(v); };

  const toggleUser = async (id: string, active: boolean) => {
    try {
      await api.patchAdminUser(id, { is_active: !active });
      toast.success('User updated (audited)');
      load('users');
    } catch {
      toast.error('Update failed');
    }
  };

  const createIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createIncident(incidentTitle);
      toast.success('Incident opened');
      setIncidentTitle('');
      load('incidents');
    } catch {
      toast.error('Failed');
    }
  };

  const advanceIncident = async (id: string, status: string) => {
    try {
      await api.patchIncident(id, { status, note: `Moved to ${status}` });
      load('incidents');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Update failed');
    }
  };

  const activateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!window.confirm(`Activate rule version ${ruleVersion}? Only TESTED/APPROVED versions can activate.`)) return;
    try {
      const r = await api.activateRule(parseInt(ruleVersion));
      toast.success(`Rule v${r.data.version} active (${r.data.checksum})`);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Activation refused by the gate');
    }
  };

  if (forbidden) {
    return (
      <DashboardLayout>
        <EmptyState title="Admin only" body="This console requires an admin account (ADMIN_EMAILS bootstrap or is_admin flag). All attempts are audited." />
      </DashboardLayout>
    );
  }

  const tabs = ['overview', 'users', 'subscriptions', 'support', 'audit', 'health', 'incidents'];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Admin Console</h2>
          <p className="text-gray-500 mt-1">Authorized, audited, reversible where possible</p>
        </div>

        <div className="flex gap-2 flex-wrap" role="tablist" aria-label="Admin views">
          {tabs.map((t) => (
            <button key={t} role="tab" aria-selected={view === t} onClick={() => go(t)}
              className={`px-3 py-1.5 rounded-full text-sm border capitalize ${view === t ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'}`}>
              {t}
            </button>
          ))}
        </div>

        {loading ? <PageLoading /> : !data ? <EmptyState title="No data" body="Select a view." /> : (
          <>
            {view === 'overview' && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(data.counts || {}).map(([k, v]) => (
                  <Card key={k}><CardContent>
                    <p className="text-xs uppercase text-gray-500">{k}</p>
                    <p className="text-xl font-bold">{String(v)}</p>
                  </CardContent></Card>
                ))}
              </div>
            )}
            {view === 'users' && (
              <Card><CardContent className="p-0">
                <Table><TableHeader><TableRow><TableHead>Email</TableHead><TableHead>Name</TableHead><TableHead>Active</TableHead><TableHead><span className="sr-only">Actions</span></TableHead></TableRow></TableHeader>
                  <TableBody>
                    {(data.users || []).map((u: any) => (
                      <TableRow key={u.id}>
                        <TableCell>{u.email}</TableCell>
                        <TableCell>{u.name} {u.is_admin && <Badge variant="info">admin</Badge>}</TableCell>
                        <TableCell>{u.is_active ? 'yes' : 'no'}</TableCell>
                        <TableCell><Button variant="secondary" size="sm" onClick={() => toggleUser(u.id, u.is_active)}>{u.is_active ? 'Deactivate' : 'Activate'}</Button></TableCell>
                      </TableRow>
                    ))}
                  </TableBody></Table>
              </CardContent></Card>
            )}
            {view === 'subscriptions' && (
              <Card><CardContent className="p-0">
                <Table><TableHeader><TableRow><TableHead>User</TableHead><TableHead>Plan</TableHead><TableHead>Status</TableHead><TableHead>Provider</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {(data.subscriptions || []).map((s: any, i: number) => (
                      <TableRow key={i}><TableCell className="font-mono text-xs">{s.user_id}</TableCell><TableCell>{s.plan}</TableCell><TableCell>{s.status}</TableCell><TableCell>{s.provider}</TableCell></TableRow>
                    ))}
                  </TableBody></Table>
              </CardContent></Card>
            )}
            {view === 'support' && (
              <Card><CardContent>
                {(data.tickets || []).map((t: any) => (
                  <div key={t.id} className="border-b border-gray-100 py-2 text-sm">
                    <p className="font-medium">{t.subject} <Badge variant="medium">{t.status}</Badge></p>
                    <p className="text-gray-500">{t.user_id} · {(t.messages || []).length} messages</p>
                  </div>
                ))}
                {(data.tickets || []).length === 0 && <p className="text-sm text-gray-500">No tickets.</p>}
              </CardContent></Card>
            )}
            {view === 'audit' && (
              <Card><CardContent>
                {(data.events || []).slice(0, 50).map((e: any, i: number) => (
                  <p key={i} className="text-xs font-mono border-b border-gray-100 py-1">{e.created_at} · {e.action} · {e.user_id} · {e.request_id}</p>
                ))}
              </CardContent></Card>
            )}
            {view === 'health' && (
              <div className="grid md:grid-cols-2 gap-4">
                <Card><CardHeader><CardTitle>System</CardTitle></CardHeader><CardContent>
                  <p className="text-sm">API: <strong>{data.api}</strong></p>
                  <p className="text-sm">Database: <strong>{data.database?.ok ? `ok (${data.database?.ping_ms}ms)` : 'DOWN'}</strong></p>
                </CardContent></Card>
                <Card><CardHeader><CardTitle>Rule activation (gated)</CardTitle></CardHeader><CardContent>
                  <form onSubmit={activateRule} className="flex gap-2">
                    <Input value={ruleVersion} onChange={(e) => setRuleVersion(e.target.value)} placeholder="Version, e.g. 2" aria-label="Rule version" />
                    <Button type="submit">Activate</Button>
                  </form>
                  <p className="text-xs text-gray-400 mt-2">Only TESTED/APPROVED versions activate; every activation is audit-logged with checksum.</p>
                </CardContent></Card>
              </div>
            )}
            {view === 'incidents' && (
              <div className="space-y-4">
                <Card><CardContent>
                  <form onSubmit={createIncident} className="flex gap-2">
                    <Input value={incidentTitle} onChange={(e) => setIncidentTitle(e.target.value)} placeholder="Incident title" aria-label="Incident title" />
                    <Button type="submit">Open</Button>
                  </form>
                </CardContent></Card>
                {(data.incidents || []).map((inc: any) => (
                  <Card key={inc.id}><CardHeader><CardTitle>{inc.title} <Badge variant={inc.status === 'resolved' || inc.status === 'reviewed' ? 'success' : 'danger'}>{inc.status}</Badge></CardTitle></CardHeader>
                    <CardContent>
                      <div className="flex gap-2 flex-wrap">
                        {['investigating', 'contained', 'resolved', 'reviewed'].filter((s) => s !== inc.status).map((s) => (
                          <Button key={s} variant="secondary" size="sm" onClick={() => advanceIncident(inc.id, s)}>{s}</Button>
                        ))}
                      </div>
                    </CardContent></Card>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

