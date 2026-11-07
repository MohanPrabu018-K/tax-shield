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
  Users,
  Plus,
  Search,
  Building,
  ShieldCheck,
  AlertTriangle,
  FolderOpen,
  Briefcase,
  ExternalLink,
  ChevronRight,
  FileText,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function ClientMasterPage() {
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [selectedClient360, setSelectedClient360] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Add Client Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [name, setName] = useState('');
  const [entityType, setEntityType] = useState('pvt_ltd');
  const [pan, setPan] = useState('');
  const [gstin, setGstin] = useState('');
  const [tan, setTan] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [assignedAccountant, setAssignedAccountant] = useState('Rahul Verma');
  const [responsiblePartner, setResponsiblePartner] = useState('CA Kailash Nath');

  const loadClients = async () => {
    setLoading(true);
    try {
      const rows = await api.getPracticeClients({ search, tag: selectedTag });
      setClients(rows || []);
    } catch {
      toast.error('Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClients();
  }, [search, selectedTag]);

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createPracticeClient({
        name,
        entity_type: entityType,
        pan,
        gstin,
        tan,
        email,
        phone,
        assigned_accountant: assignedAccountant,
        responsible_partner: responsiblePartner,
      });
      toast.success('Client registered in Master Repository');
      setShowAddModal(false);
      setName('');
      setPan('');
      setGstin('');
      setTan('');
      loadClients();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to create client');
    }
  };

  const handleOpen360 = async (client: any) => {
    try {
      const full = await api.getClient360(client.id || client._id);
      setSelectedClient360(full);
      setActiveTab('overview');
    } catch {
      toast.error('Failed to load 360 profile');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Client Master 360°</h1>
            <p className="text-xs text-slate-500">Comprehensive legal entity registry, statutory registrations and 360-degree workspaces</p>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Add New Client
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search clients by name, PAN or GSTIN..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full text-xs pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>
          <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
            {['', 'High Priority', 'GST Monthly', 'Audit Applicable', 'Active'].map((t) => (
              <button
                key={t}
                onClick={() => setSelectedTag(t)}
                className={`text-xs px-2.5 py-1 rounded-md font-medium whitespace-nowrap transition-colors ${
                  selectedTag === t
                    ? 'bg-slate-800 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {t || 'All Tags'}
              </button>
            ))}
          </div>
        </div>

        {/* Client Master Table */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : clients.length === 0 ? (
              <div className="p-12 text-center text-slate-500 text-xs">
                No clients found matching criteria. Click &quot;Add New Client&quot; to register your first entity.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-semibold">
                    <tr>
                      <th className="py-3 px-4">Client Name & Code</th>
                      <th className="py-3 px-4">Constitution</th>
                      <th className="py-3 px-4">PAN / TAN</th>
                      <th className="py-3 px-4">GSTIN</th>
                      <th className="py-3 px-4">Engagement Team</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {clients.map((c) => (
                      <tr key={c.id || c._id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-4">
                          <p className="font-bold text-slate-900">{c.name}</p>
                          <span className="text-[10px] text-slate-400 font-mono">{c.client_code}</span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="capitalize px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700">
                            {c.entity_type?.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px]">
                          <div>PAN: <span className="font-semibold text-slate-800">{c.pan || '—'}</span></div>
                          {c.tan && <div className="text-slate-500 text-[10px]">TAN: {c.tan}</div>}
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px]">
                          {c.gstin ? (
                            <span className="font-semibold text-slate-800">{c.gstin}</span>
                          ) : (
                            <span className="text-slate-400 italic">Unregistered</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-[11px]">
                          <p className="text-slate-800 font-medium">CA: {c.responsible_partner || 'CA Kailash'}</p>
                          <p className="text-slate-500">Staff: {c.assigned_accountant || 'Rahul'}</p>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Button size="sm" variant="secondary" onClick={() => handleOpen360(c)} className="text-xs">
                            360° Profile
                            <ChevronRight className="h-3.5 w-3.5 ml-1" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Client 360° Profile Modal / Drawer */}
        {selectedClient360 && (
          <Modal
            isOpen={Boolean(selectedClient360)}
            onClose={() => setSelectedClient360(null)}
            title={`360° Workspace: ${selectedClient360.client?.name}`}
          >
            <div className="space-y-4">
              {/* Tabs */}
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2 text-xs overflow-x-auto">
                {['overview', 'engagements', 'tasks', 'risk'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-3 py-1.5 rounded-md font-semibold uppercase tracking-wider text-[10px] transition-colors ${
                      activeTab === tab
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {activeTab === 'overview' && (
                <div className="space-y-4 text-xs">
                  <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200">
                    <div>
                      <p className="text-slate-500">Legal Entity Type:</p>
                      <p className="font-bold text-slate-900 capitalize">{selectedClient360.client?.entity_type}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Financial Year:</p>
                      <p className="font-bold text-slate-900">{selectedClient360.client?.financial_year}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">PAN:</p>
                      <p className="font-mono font-bold text-slate-900">{selectedClient360.client?.pan || '—'}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">GSTIN:</p>
                      <p className="font-mono font-bold text-slate-900">{selectedClient360.client?.gstin || '—'}</p>
                    </div>
                  </div>

                  <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-900">
                    <p className="font-bold flex items-center gap-1.5">
                      <AlertTriangle className="h-4 w-4 text-amber-600" />
                      Client Health & Risk Score: {selectedClient360.risk?.risk_score}/100 ({selectedClient360.risk?.risk_level})
                    </p>
                    <p className="mt-1 text-[11px]">{selectedClient360.risk?.recommended_action}</p>
                  </div>
                </div>
              )}

              {activeTab === 'engagements' && (
                <div className="space-y-2 text-xs">
                  {selectedClient360.engagements?.length === 0 ? (
                    <p className="text-slate-500">No active contracted engagements.</p>
                  ) : (
                    selectedClient360.engagements?.map((e: any) => (
                      <div key={e.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center">
                        <div>
                          <p className="font-bold text-slate-900">{e.service_name}</p>
                          <p className="text-[11px] text-slate-500">Scope: {e.scope} • Fee: ₹{e.agreed_fee}</p>
                        </div>
                        <Badge variant="medium">{e.status}</Badge>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'tasks' && (
                <div className="space-y-2 text-xs">
                  {selectedClient360.tasks?.length === 0 ? (
                    <p className="text-slate-500">No open compliance tasks.</p>
                  ) : (
                    selectedClient360.tasks?.map((t: any) => (
                      <div key={t.id} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center">
                        <div>
                          <p className="font-bold text-slate-900">{t.title}</p>
                          <p className="text-[10px] text-slate-500">Due: {t.due_date} • Assignee: {t.assigned_to}</p>
                        </div>
                        <Badge variant="default">{t.status}</Badge>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'risk' && (
                <div className="space-y-3 text-xs">
                  <p className="font-bold text-slate-900">Operational Risk Diagnostics:</p>
                  <ul className="space-y-1.5">
                    {selectedClient360.risk?.reasons?.map((r: string, idx: number) => (
                      <li key={idx} className="flex items-center gap-2 text-rose-700 bg-rose-50 p-2 rounded border border-rose-200">
                        <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                        <span>{r}</span>
                      </li>
                    ))}
                    {(!selectedClient360.risk?.reasons || selectedClient360.risk?.reasons.length === 0) && (
                      <li className="text-emerald-700 bg-emerald-50 p-2 rounded border border-emerald-200">
                        Zero compliance or documentation exceptions flagged.
                      </li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          </Modal>
        )}

        {/* Add Client Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Register New Client Master">
          <form onSubmit={handleCreateClient} className="space-y-4 text-xs">
            <Input label="Client / Business Legal Name" value={name} onChange={(e) => setName(e.target.value)} required />
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Entity Constitution</label>
                <select
                  value={entityType}
                  onChange={(e) => setEntityType(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-md px-2.5 py-1.5 bg-white"
                >
                  <option value="pvt_ltd">Private Limited Company</option>
                  <option value="partnership">Partnership Firm</option>
                  <option value="llp">Limited Liability Partnership</option>
                  <option value="proprietorship">Sole Proprietorship</option>
                  <option value="individual">Individual / Salaried</option>
                  <option value="trust">Trust / Section 8</option>
                </select>
              </div>
              <Input label="PAN" value={pan} onChange={(e) => setPan(e.target.value)} placeholder="e.g. ABCDE1234F" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="GSTIN (if applicable)" value={gstin} onChange={(e) => setGstin(e.target.value)} placeholder="27ABCDE1234F1Z5" />
              <Input label="TAN (if deductor)" value={tan} onChange={(e) => setTan(e.target.value)} placeholder="MUMB12345A" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Primary Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input label="Contact Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Responsible Partner" value={responsiblePartner} onChange={(e) => setResponsiblePartner(e.target.value)} />
              <Input label="Assigned Staff Accountant" value={assignedAccountant} onChange={(e) => setAssignedAccountant(e.target.value)} />
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Save Client
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

