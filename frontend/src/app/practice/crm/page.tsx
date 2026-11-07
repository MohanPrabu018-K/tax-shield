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
  UserRound,
  Plus,
  ArrowRight,
  CheckCircle2,
  Phone,
  Mail,
  Calendar,
  Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';

const STAGES = [
  { id: 'NEW_LEAD', label: 'New Lead' },
  { id: 'CONTACTED', label: 'Contacted' },
  { id: 'DISCUSSION', label: 'Discussion' },
  { id: 'PROPOSAL_SENT', label: 'Proposal Sent' },
  { id: 'NEGOTIATION', label: 'Negotiation' },
  { id: 'ACCEPTED', label: 'Accepted' },
];

export default function LeadsCRMPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [entityName, setEntityName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [fee, setFee] = useState('25000');
  const [services, setServices] = useState('Monthly Accounting, GST, ITR');
  const [followUp, setFollowUp] = useState('');
  const [notes, setNotes] = useState('');

  const loadLeads = async () => {
    setLoading(true);
    try {
      const rows = await api.getLeads();
      setLeads(rows || []);
    } catch {
      toast.error('Failed to load leads pipeline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createLead({
        contact_name: name,
        entity_name: entityName,
        phone,
        email,
        expected_fee: parseFloat(fee),
        services_required: services.split(',').map((s) => s.trim()),
        follow_up_date: followUp,
        notes,
      });
      toast.success('Prospective lead registered');
      setShowAddModal(false);
      setName('');
      setPhone('');
      loadLeads();
    } catch {
      toast.error('Failed to create lead');
    }
  };

  const handleAdvanceStage = async (lid: string, targetStage: string) => {
    try {
      await api.updateLeadStage(lid, targetStage);
      toast.success(`Pipeline updated to ${targetStage}`);
      loadLeads();
    } catch {
      toast.error('Failed to update stage');
    }
  };

  const handleConvert = async (lid: string) => {
    try {
      const res = await api.convertLead(lid);
      toast.success(res?.message || 'Lead converted to active Client Master');
      loadLeads();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to convert lead');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Client CRM & Lead Management</h1>
            <p className="text-xs text-slate-500">Pipeline tracking from initial enquiry to proposal, negotiation and 1-click client onboarding</p>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Add Prospective Lead
          </Button>
        </div>

        {/* Pipeline Kanban Columns */}
        {loading ? (
          <PageLoading />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {STAGES.map((st) => {
              const stageLeads = leads.filter((l) => (l.stage || 'NEW_LEAD') === st.id);
              return (
                <div key={st.id} className="bg-slate-100/70 p-3 rounded-xl border border-slate-200 flex flex-col min-h-[350px]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wide">{st.label}</span>
                    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-slate-200 text-slate-700">
                      {stageLeads.length}
                    </span>
                  </div>

                  <div className="space-y-2 flex-1">
                    {stageLeads.map((lead) => (
                      <Card key={lead.id || lead._id} className="border border-slate-200 shadow-xs hover:border-emerald-400 transition-all bg-white">
                        <CardContent className="p-3 space-y-2 text-xs">
                          <div>
                            <p className="font-bold text-slate-900 leading-tight">{lead.entity_name || lead.contact_name}</p>
                            <p className="text-[10px] text-slate-500 mt-0.5">{lead.contact_name}</p>
                          </div>

                          <div className="text-[11px] text-slate-600">
                            Est. Fee: <span className="font-bold text-emerald-700 font-mono">₹{lead.expected_fee?.toLocaleString('en-IN')}</span>
                          </div>

                          {lead.follow_up_date && (
                            <div className="flex items-center gap-1 text-[10px] text-slate-500">
                              <Calendar className="h-3 w-3 text-slate-400" />
                              <span>Follow-up: {lead.follow_up_date}</span>
                            </div>
                          )}

                          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                            {st.id !== 'ACCEPTED' ? (
                              <button
                                onClick={() => {
                                  const nextIdx = STAGES.findIndex((s) => s.id === st.id) + 1;
                                  if (nextIdx < STAGES.length) {
                                    handleAdvanceStage(lead.id || lead._id, STAGES[nextIdx].id);
                                  }
                                }}
                                className="text-[10px] font-semibold text-emerald-700 hover:underline flex items-center gap-0.5"
                              >
                                Advance <ArrowRight className="h-3 w-3" />
                              </button>
                            ) : (
                              <Button
                                size="sm"
                                onClick={() => handleConvert(lead.id || lead._id)}
                                className="w-full text-[10px] py-1 h-auto bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                              >
                                <Sparkles className="h-3 w-3 mr-1" />
                                Convert to Client
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Add Lead Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Record Prospective Lead">
          <form onSubmit={handleCreateLead} className="space-y-4 text-xs">
            <Input label="Business / Entity Name" value={entityName} onChange={(e) => setEntityName(e.target.value)} required placeholder="e.g. Apex Traders LLP" />
            <Input label="Primary Contact Person" value={name} onChange={(e) => setName(e.target.value)} required placeholder="Mr. Rajesh Gupta" />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Mobile / WhatsApp Phone" value={phone} onChange={(e) => setPhone(e.target.value)} required />
              <Input label="Email Address" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Expected Annual Fee (₹)" type="number" value={fee} onChange={(e) => setFee(e.target.value)} required />
              <Input label="Next Follow-up Date" type="date" value={followUp} onChange={(e) => setFollowUp(e.target.value)} />
            </div>

            <Input label="Services Required" value={services} onChange={(e) => setServices(e.target.value)} />

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Requirement Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className="w-full text-xs border border-slate-300 rounded-md p-2"
                placeholder="Client looking to migrate from existing accountant for better GST filing turnaround..."
              />
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Save Lead
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

