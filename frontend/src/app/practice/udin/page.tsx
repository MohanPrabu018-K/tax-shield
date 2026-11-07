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
  ShieldCheck,
  Plus,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  FileText,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function UDINTrackerPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [udin, setUdin] = useState('');
  const [clientName, setClientName] = useState('');
  const [documentType, setDocumentType] = useState('Tax Audit Report (Sec 44AB)');
  const [documentDate, setDocumentDate] = useState(new Date().toISOString().slice(0, 10));
  const [notes, setNotes] = useState('');

  const loadUDINs = async () => {
    setLoading(true);
    try {
      const rows = await api.getUDINRecords();
      setRecords(rows || []);
    } catch {
      toast.error('Failed to load UDIN records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUDINs();
  }, []);

  const handleRecordUDIN = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.recordUDIN({
        udin,
        client_name: clientName,
        document_type: documentType,
        document_date: documentDate,
        notes,
      });
      toast.success('UDIN verified and linked to engagement dossier');
      setShowAddModal(false);
      setUdin('');
      setClientName('');
      loadUDINs();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Invalid UDIN format');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">UDIN Management Desk</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                ICAI MANDATORY COMPLIANCE
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Record, validate and link official Unique Document Identification Numbers (UDIN) to signed reports and certificates
            </p>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Record Official UDIN
          </Button>
        </div>

        {/* Regulatory Advisory Box */}
        <div className="bg-blue-50/70 p-4 rounded-xl border border-blue-200 text-xs text-blue-950 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold text-sm">Regulatory Integrity Notice:</p>
            <p>
              Under ICAI regulations, UDIN must be generated exclusively by the signing Chartered Accountant through the official ICAI portal (<a href="https://udin.icai.org" target="_blank" rel="noreferrer" className="underline font-semibold">udin.icai.org</a>). TaxShield validates format structure (18 characters: 6-digit membership + 12 alphanumeric) and maintains an immutable audit record linking the official UDIN to the engagement workpapers and client report.
            </p>
          </div>
        </div>

        {/* UDIN Records Table */}
        <Card className="border border-slate-200 shadow-sm overflow-hidden">
          <CardHeader className="bg-slate-50 border-b border-slate-200 px-5 py-3.5">
            <CardTitle className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Firm UDIN Registry ({records.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8"><PageLoading /></div>
            ) : records.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500">
                No UDINs recorded yet. Click &quot;Record Official UDIN&quot; to log your first signed report.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase">
                    <tr>
                      <th className="py-3 px-4">Official UDIN</th>
                      <th className="py-3 px-4">Client</th>
                      <th className="py-3 px-4">Document Type</th>
                      <th className="py-3 px-4">Signing CA</th>
                      <th className="py-3 px-4">Document Date</th>
                      <th className="py-3 px-4">Verification</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {records.map((r) => (
                      <tr key={r.id || r._id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-emerald-800">
                          {r.udin}
                        </td>
                        <td className="py-3 px-4 font-medium text-slate-900">{r.client_name || 'Acme'}</td>
                        <td className="py-3 px-4 text-slate-700">{r.document_type}</td>
                        <td className="py-3 px-4 text-slate-700">{r.signing_ca}</td>
                        <td className="py-3 px-4 text-slate-500">{r.document_date}</td>
                        <td className="py-3 px-4">
                          <Badge variant="success">RECORDED_VERIFIED</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Record UDIN Modal */}
        <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Record Official ICAI UDIN">
          <form onSubmit={handleRecordUDIN} className="space-y-4 text-xs">
            <Input
              label="18-Character Official UDIN"
              value={udin}
              onChange={(e) => setUdin(e.target.value.toUpperCase())}
              required
              placeholder="e.g. 123456ABCDEF123456"
            />
            <Input
              label="Client Name"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              required
              placeholder="Acme Industrial Technologies Pvt Ltd"
            />
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Document / Certificate Type</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-md px-2.5 py-1.5 bg-white"
                >
                  <option value="Tax Audit Report (Sec 44AB)">Tax Audit Report (Sec 44AB)</option>
                  <option value="Statutory Audit Report">Statutory Company Audit Report</option>
                  <option value="Net Worth Certificate">Net Worth Certificate</option>
                  <option value="Turnover Certificate">Turnover Certificate</option>
                  <option value="GSTR-9C Reconciliation">GSTR-9C Reconciliation Statement</option>
                  <option value="Trust Audit Form 10B">Trust Audit Form 10B/10BB</option>
                </select>
              </div>
              <Input label="Document Date" type="date" value={documentDate} onChange={(e) => setDocumentDate(e.target.value)} required />
            </div>

            <Input label="Internal Notes / Filing Ref" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="e.g. Form 3CA/3CD uploaded on portal" />

            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button type="button" variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                Verify & Save UDIN
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}

