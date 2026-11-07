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
  FileText,
  Plus,
  Briefcase,
  CheckCircle2,
  Calendar,
  Layers,
  Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function EngagementsServiceCatalogPage() {
  const [engagements, setEngagements] = useState<any[]>([]);
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'engagements' | 'catalog'>('engagements');
  const [showAddModal, setShowAddModal] = useState(false);

  // New Engagement Form
  const [clientName, setClientName] = useState('');
  const [serviceName, setServiceName] = useState('Monthly GST Compliance & Reconciliation');
  const [serviceCategory, setServiceCategory] = useState('gst');
  const [scope, setScope] = useState('GSTR-1, GSTR-3B, GSTR-2B reconciliation, ITC optimization');
  const [agreedFee, setAgreedFee] = useState('15000');
  const [feeType, setFeeType] = useState('recurring_monthly');
  const [assignedStaff, setAssignedStaff] = useState('Rahul Verma');

  const loadData = async () => {
    setLoading(true);
    try {
      const [engs, servs] = await Promise.all([
        api.getEngagements().catch(() => []),
        api.getServiceCatalog().catch(() => []),
      ]);
      setEngagements(engs || []);
      setServices(servs || []);
    } catch {
      toast.error('Failed to load engagements');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateEngagement = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createEngagement({
        client_name: clientName,
        client_id: 'clt_manual',
        service_name: serviceName,
        service_category: serviceCategory,
        scope,
        agreed_fee: parseFloat(agreedFee),
        fee_type: feeType,
        assigned_staff: assignedStaff,
      });
      toast.success('Engagement created and tasks linked');
      setShowAddModal(false);
      setClientName('');
      loadData();
    } catch {
      toast.error('Failed to create engagement');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Engagement & Service Catalog</h1>
            <p className="text-xs text-slate-500">Contracted professional service scopes, deliverable schedules, and ICAI SA 210 terms</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="bg-slate-100 p-0.5 rounded-lg border border-slate-200 flex text-xs font-semibold">
              <button
                onClick={() => setActiveTab('engagements')}
                className={`px-3 py-1.5 rounded-md transition-colors ${activeTab === 'engagements' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-600'}`}
              >
                Engagements ({engagements.length})
              </button>
              <button
                onClick={() => setActiveTab('catalog')}
                className={`px-3 py-1.5 rounded-md transition-colors ${activeTab === 'catalog' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-600'}`}
              >
                Service Catalog ({services.length})
              </button>
            </div>
            {activeTab === 'engagements' && (
              <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
                <Plus className="h-4 w-4 mr-1.5" />
                New Engagement
              </Button>
            )}
          </div>
        </div>

        {/* Content based on active tab */}
        {activeTab === 'engagements' ? (
          <Card className="border border-slate-200 shadow-sm overflow-hidden">
            <CardContent className="p-0">
              {loading ? (
                <div className="p-8"><PageLoading /></div>
              ) : engagements.length === 0 ? (
                <div className="p-12 text-center text-xs text-slate-500">
                  No engagements registered yet. Click &quot;New Engagement&quot; to contract a client service.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                      <tr>
                        <th className="py-3 px-4">Engagement Code</th>
                        <th className="py-3 px-4">Client</th>
                        <th className="py-3 px-4">Service & Scope</th>
                        <th className="py-3 px-4">Agreed Fee</th>
                        <th className="py-3 px-4">Assigned Team</th>
                        <th className="py-3 px-4">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {engagements.map((e) => (
                        <tr key={e.id || e._id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-slate-800">{e.engagement_code}</td>
                          <td className="py-3 px-4 font-bold text-slate-900">{e.client_name || 'Acme'}</td>
                          <td className="py-3 px-4">
                            <p className="font-semibold text-slate-900">{e.service_name}</p>
                            <p className="text-[11px] text-slate-500 line-clamp-1">{e.scope}</p>
                          </td>
                          <td className="py-3 px-4 font-mono font-bold text-emerald-700">
                            ₹{e.agreed_fee?.toLocaleString('en-IN')}{' '}
                            <span className="text-[10px] text-slate-400 font-normal">({e.fee_type})</span>
                          </td>
                          <td className="py-3 px-4 text-[11px]">
                            <p className="text-slate-800 font-medium">Lead: {e.responsible_partner || 'CA Partner'}</p>
                            <p className="text-slate-500">Staff: {e.assigned_staff || 'Staff'}</p>
                          </td>
                          <td className="py-3 px-4">
                            <Badge variant="medium">{e.status}</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {services.map((s) => (
              <Card key={s.code} className="border border-slate-200 shadow-sm hover:border-emerald-400 transition-all">
                <CardContent className="p-4 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                      {s.code}
                    </span>
                    <Badge variant="default">{s.category?.toUpperCase()}</Badge>
                  </div>
                  <h3 className="font-bold text-slate-900 text-sm">{s.name}</h3>
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-slate-500 text-[11px]">
                    <span>Standard Practice Fee:</span>
                    <span className="font-bold text-emerald-700 font-mono">₹{s.default_fee?.toLocaleString('en-IN')}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* New Engagement Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Contract Professional Engagement">
          <form onSubmit={handleCreateEngagement} className="space-y-4 text-xs">
            <Input label="Client Name" value={clientName} onChange={(e) => setClientName(e.target.value)} required placeholder="Acme Industrial Technologies" />
            <Input label="Contracted Service Title" value={serviceName} onChange={(e) => setServiceName(e.target.value)} required />
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Contractual Scope of Work</label>
              <textarea
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                rows={2}
                className="w-full text-xs border border-slate-300 rounded-md p-2"
                placeholder="Define specific statutory deliverables and exclusions..."
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Agreed Professional Fee (₹)" type="number" value={agreedFee} onChange={(e) => setAgreedFee(e.target.value)} required />
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Fee Model</label>
                <select
                  value={feeType}
                  onChange={(e) => setFeeType(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-md px-2.5 py-1.5 bg-white"
                >
                  <option value="recurring_monthly">Monthly Retainer</option>
                  <option value="recurring_quarterly">Quarterly</option>
                  <option value="fixed_annual">Annual Fixed Fee</option>
                  <option value="milestone">Milestone Based</option>
                </select>
              </div>
            </div>

            <Input label="Assigned Lead Staff" value={assignedStaff} onChange={(e) => setAssignedStaff(e.target.value)} required />

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Contract Engagement
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

