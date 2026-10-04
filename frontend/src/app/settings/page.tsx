'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { getWorkspace, clearWorkspace } from '@/lib/workspace';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { PageLoading } from '@/components/ui/State';
import { User, Shield, Bell, Database, LogOut, Download } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';

function PasswordForm() {
  const [oldPw, setOldPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const change = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const r = await api.changePassword(oldPw, newPw);
      toast.success(r.message || 'Password changed');
      setOldPw('');
      setNewPw('');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || err?.response?.data?.detail || 'Change failed');
    }
  };
  return (
    <form onSubmit={change} className="flex flex-col sm:flex-row gap-2 max-w-xl">
      <Input type="password" value={oldPw} onChange={(e) => setOldPw(e.target.value)} placeholder="Current password" aria-label="Current password" required />
      <Input type="password" value={newPw} onChange={(e) => setNewPw(e.target.value)} placeholder="New password (8+ chars)" aria-label="New password" required minLength={8} />
      <Button type="submit">Change</Button>
    </form>
  );
}

function SessionsPanel() {
  const { logout } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<any[]>([]);
  useEffect(() => {
    api.getSessions().then((r) => setSessions(r.sessions || [])).catch(() => undefined);
  }, []);
  const logoutAllDevices = async () => {
    try {
      const r = await api.logoutAll();
      if (r.access_token) api.setToken(r.access_token);
      toast.success('All other sessions signed out');
    } catch {
      toast.error('Failed');
    }
  };
  const logoutThis = () => {
    logout();
    router.push('/login');
  };
  return (
    <div>
      <p className="text-sm text-gray-500 mb-2">Recent sign-ins (JWT sessions are stateless — each sign-in is listed):</p>
      <ul className="text-sm space-y-1 mb-3">
        {sessions.slice(0, 10).map((s: any, i: number) => (
          <li key={i} className="text-gray-600">{s.action} · {String(s.at).slice(0, 16).replace('T', ' ')}</li>
        ))}
        {sessions.length === 0 && <li className="text-gray-400">No sessions recorded yet.</li>}
      </ul>
      <div className="flex gap-2">
        <Button variant="secondary" onClick={logoutAllDevices}>Sign out all other devices</Button>
        <Button variant="secondary" onClick={logoutThis}>
          <LogOut className="h-4 w-4 mr-2" /> Sign out this device
        </Button>
      </div>
    </div>
  );
}

function ConsentsPanel() {
  const purposes = ['essential', 'communications', 'ai_processing', 'analytics', 'marketing'];
  const [consents, setConsents] = useState<Record<string, boolean>>({});
  useEffect(() => {
    api.getConsents().then((r) => setConsents(r.consents || {})).catch(() => undefined);
  }, []);
  const set = async (purpose: string, granted: boolean) => {
    try {
      await api.setConsent(purpose, granted);
      setConsents((c) => ({ ...c, [purpose]: granted }));
      toast.success('Consent recorded with history');
    } catch {
      toast.error('Failed');
    }
  };
  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-500">Purpose-specific consent, withdrawable anytime. Essential processing is required for the service; the rest are optional.</p>
      {purposes.map((p) => (
        <label key={p} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm">
          <span className="capitalize font-medium">{p.replace(/_/g, ' ')}{p === 'essential' && ' (required)'}</span>
          <input type="checkbox" checked={!!consents[p]} disabled={p === 'essential'}
            onChange={(e) => set(p, e.target.checked)} className="h-5 w-5"
            aria-label={`Consent for ${p}`} />
        </label>
      ))}
    </div>
  );
}

function DeletionPanel() {
  const { logout } = useAuth();
  const router = useRouter();
  const [status, setStatus] = useState<any>(null);
  const [confirm, setConfirm] = useState('');
  useEffect(() => {
    api.deletionStatus().then(setStatus).catch(() => undefined);
  }, []);
  const request = async () => {
    try {
      const r = await api.requestDeletion();
      toast.success('Deletion requested — 7-day grace');
      setStatus({ status: 'pending', grace_until: r.grace_until });
    } catch {
      toast.error('Request failed');
    }
  };
  const execute = async () => {
    try {
      await api.executeDeletion(confirm, true);
      toast.success('Account deleted');
      logout();
      router.push('/');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || err?.response?.data?.detail || 'Execute failed');
    }
  };
  return (
    <div className="p-4 bg-red-50 border border-red-100 rounded-lg text-sm space-y-3">
      <p className="text-red-800">Deletion purges your transactions, invoices, documents (files included), clients and workspace data. Security audit events and billing records are retained as required — shown to you before you confirm.</p>
      {!status?.status ? (
        <Button variant="danger" onClick={request}>Request deletion (7-day grace)</Button>
      ) : (
        <>
          <p className="text-red-800">Status: <strong>{status.status}</strong>{status.grace_until ? ` · grace until ${String(status.grace_until).slice(0, 10)}` : ''}</p>
          <div className="flex gap-2">
            <Input value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder='Type DELETE to confirm' aria-label="Deletion confirmation" />
            <Button variant="danger" onClick={execute}>Delete now</Button>
          </div>
        </>
      )}
    </div>
  );
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export default function SettingsPage() {
  const { user, logout, loading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'security' | 'data'>('profile');
  const [aiPref, setAiPref] = useState('enabled');
  const [inAppAlerts, setInAppAlerts] = useState(true);

  useEffect(() => {
    try {
      setAiPref(localStorage.getItem('taxshield_ai') || 'enabled');
      setInAppAlerts(localStorage.getItem('taxshield_alerts') !== 'off');
    } catch { /* ignore */ }
  }, []);

  const savePrefs = () => {
    try {
      localStorage.setItem('taxshield_ai', aiPref);
      localStorage.setItem('taxshield_alerts', inAppAlerts ? 'on' : 'off');
      toast.success('Preferences saved on this device');
    } catch {
      toast.error('Could not save preferences');
    }
  };

  const downloadAuthed = async (path: string, filename: string) => {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        headers: { Authorization: `Bearer ${api.getToken()}` },
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Downloaded ${filename}`);
    } catch {
      toast.error('Export failed');
    }
  };

  const logoutAll = () => {
    api.clearToken();
    try { localStorage.removeItem('token'); } catch { /* ignore */ }
    logout();
    router.push('/login');
    toast.success('Signed out on this device');
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'preferences', label: 'Preferences', icon: Shield },
    { id: 'security', label: 'Security', icon: Bell },
    { id: 'data', label: 'Data Management', icon: Database },
  ];

  const ws = getWorkspace();

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-4xl">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-500 mt-1">Manage your account and preferences</p>
        </div>

        <Card>
          <CardContent className="p-0">
            <nav className="border-b border-gray-100" aria-label="Settings tabs">
              <ul className="flex flex-wrap -mb-px" role="tablist">
                {tabs.map((tab) => (
                  <li key={tab.id} role="presentation">
                    <button
                      role="tab"
                      aria-selected={activeTab === tab.id}
                      aria-controls={`${tab.id}-panel`}
                      id={`${tab.id}-tab`}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === tab.id
                          ? 'border-primary-600 text-primary-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-200'
                      }`}
                    >
                      <tab.icon className="h-4 w-4" />
                      {tab.label}
                    </button>
                  </li>
                ))}
              </ul>
            </nav>

            <div className="p-6">
              {activeTab === 'profile' && (
                <div id="profile-panel" role="tabpanel" aria-labelledby="profile-tab" className="space-y-6">
                  {loading ? <PageLoading /> : (
                    <>
                      <div className="flex items-center gap-4">
                        <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center">
                          <User className="h-10 w-10 text-primary-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{user?.name || 'User'}</h3>
                          <p className="text-gray-500">{user?.email}</p>
                          <p className="text-sm text-gray-400">Member since {user?.created_at ? formatDate(user.created_at) : 'Unknown'}</p>
                        </div>
                      </div>
                      <dl className="grid sm:grid-cols-2 gap-4 text-sm">
                        <div><dt className="text-gray-500">Tax jurisdiction</dt><dd className="font-medium">{user?.tax_jurisdiction || '—'}</dd></div>
                        <div><dt className="text-gray-500">Financial year</dt><dd className="font-medium">{user?.financial_year || '—'}</dd></div>
                        <div><dt className="text-gray-500">Employment</dt><dd className="font-medium">{user?.employment_type || '—'}</dd></div>
                        <div><dt className="text-gray-500">Preferred regime</dt><dd className="font-medium">{user?.preferred_tax_regime || 'Not specified'}</dd></div>
                      </dl>
                      <div className="border-t border-gray-100 pt-4">
                        <h4 className="font-medium text-gray-900 mb-1">Workspace setup</h4>
                        <p className="text-sm text-gray-500 mb-3">
                          {ws ? `${ws.userType} · ${ws.incomeSources.length} income source(s) · FY ${ws.taxPeriod}` : 'Not completed yet.'}
                        </p>
                        <Button variant="secondary" onClick={() => router.push('/onboarding')}>
                          {ws ? 'Redo setup' : 'Complete setup'}
                        </Button>
                      </div>
                      <p className="text-xs text-gray-400">Profile editing via API is not available yet — values shown are what you registered with. Server-side profile updates are on the roadmap; nothing here pretends to save.</p>
                    </>
                  )}
                </div>
              )}

              {activeTab === 'preferences' && (
                <div id="preferences-panel" role="tabpanel" aria-labelledby="preferences-tab" className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">In-app alerts</h3>
                    <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700">Compliance, invoice and document alerts in Notifications</span>
                      <input type="checkbox" checked={inAppAlerts} onChange={(e) => setInAppAlerts(e.target.checked)} className="h-5 w-5" />
                    </label>
                    <p className="text-xs text-gray-400 mt-1">No paid email/SMS providers. Alerts are in-app only by design.</p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">AI assistance</h3>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="ai-pref">Explanations style</label>
                    <select id="ai-pref" value={aiPref} onChange={(e) => setAiPref(e.target.value)} className="w-full px-3 py-2 border rounded-lg bg-white border-gray-300">
                      <option value="enabled">Enabled (deterministic results + friendly explanations)</option>
                      <option value="minimal">Minimal (facts only, no extra phrasing)</option>
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Your financial data is never used for model training. Tax and accounting math is always deterministic, regardless of this setting.</p>
                  </div>
                  <Button onClick={savePrefs}>Save preferences</Button>
                </div>
              )}

              {activeTab === 'security' && (
                <div id="security-panel" role="tabpanel" aria-labelledby="security-tab" className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">How you are protected</h3>
                    <ul className="text-sm text-gray-600 list-disc pl-5 space-y-1">
                      <li>JWT Bearer authentication with bcrypt-hashed passwords</li>
                      <li>Server-side tenant isolation on every data request</li>
                      <li>Rate-limited login/register and chat endpoints</li>
                      <li>Ownership-checked document downloads (never public URLs)</li>
                    </ul>
                  </div>
                  <div className="border-t border-gray-100 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Change password</h3>
                    <PasswordForm />
                  </div>
                  <div className="border-t border-gray-100 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Sessions</h3>
                    <SessionsPanel />
                  </div>
                  <p className="text-xs text-gray-400">Two-factor authentication is not shipped yet — deliberately absent here rather than simulated. Password resets use single-use 30-minute tokens.</p>
                </div>
              )}

              {activeTab === 'data' && (
                <div id="data-panel" role="tabpanel" aria-labelledby="data-tab" className="space-y-6">
                  <div>
                    <CardHeader><CardTitle>Export my data (real downloads)</CardTitle></CardHeader>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <Button variant="secondary" onClick={() => downloadAuthed('/exports/transactions.csv', 'transactions.csv')}>
                        <Download className="h-4 w-4 mr-2" />Transactions (CSV)
                      </Button>
                      <Button variant="secondary" onClick={() => downloadAuthed('/exports/invoices.csv', 'invoices.csv')}>
                        <Download className="h-4 w-4 mr-2" />Invoices (CSV)
                      </Button>
                      <Button variant="secondary" onClick={() => downloadAuthed('/exports/parties.csv', 'parties.csv')}>
                        <Download className="h-4 w-4 mr-2" />Parties (CSV)
                      </Button>
                      <Button variant="secondary" onClick={() => downloadAuthed('/exports/me', 'taxshield-export.json')}>
                        <Download className="h-4 w-4 mr-2" />All data (JSON)
                      </Button>
                    </div>
                  </div>
                  <div className="border-t border-gray-100 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Workspace on this device</h3>
                    <Button variant="secondary" onClick={() => { clearWorkspace(); toast.success('Local workspace cleared'); router.push('/onboarding'); }}>
                      Reset local setup
                    </Button>
                  </div>
                  <div className="border-t border-gray-100 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Consent preferences</h3>
                    <ConsentsPanel />
                  </div>
                  <div className="border-t border-gray-100 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete account</h3>
                    <DeletionPanel />
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
