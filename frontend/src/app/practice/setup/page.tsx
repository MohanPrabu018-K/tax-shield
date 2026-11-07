'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Check, ChevronRight, ChevronLeft, Building2, UserCheck, ShieldCheck, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

export default function PracticeSetupWizardPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);

  // Form State
  const [firmName, setFirmName] = useState('Kailash & Associates, Chartered Accountants');
  const [firmType, setFirmType] = useState('partnership');
  const [icaiFrn, setIcaiFrn] = useState('012345S');
  const [primaryContact, setPrimaryContact] = useState('CA Kailash Nath');
  const [email, setEmail] = useState('kailash@kailashca.in');
  const [phone, setPhone] = useState('+91 9876543210');
  const [city, setCity] = useState('Mumbai');
  const [state, setState] = useState('Maharashtra');

  // Services
  const [selectedServices, setSelectedServices] = useState<string[]>([
    'ACC-01', 'ACC-02', 'ACC-03', 'GST-01', 'GST-02', 'ITR-01', 'ITR-03', 'TDS-01', 'AUD-01', 'AUD-02'
  ]);

  // Partners & Staff
  const [partners, setPartners] = useState([
    { name: 'CA Kailash Nath', membership: '123456', cop: 'active' },
    { name: 'CA Sunita Sharma', membership: '654321', cop: 'active' },
  ]);

  const toggleService = (code: string) => {
    setSelectedServices((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      await api.savePracticeProfile({
        firm_name: firmName,
        firm_type: firmType,
        icai_frn: icaiFrn,
        primary_contact_name: primaryContact,
        email,
        phone,
        city,
        state,
        services: selectedServices,
        partners,
        departments: ['Direct Tax', 'GST', 'Audit & Assurance', 'Accounting'],
        workflow_preferences: {
          require_partner_approval: true,
          prevent_self_approval: true,
          auto_task_generation: true,
          whatsapp_reminders_enabled: true,
        },
      });
      toast.success('Practice Setup Completed! Welcome to TaxShield Professional.');
      router.push('/practice');
    } catch {
      toast.error('Failed to complete practice setup');
    } finally {
      setSaving(false);
    }
  };

  const stepsList = [
    'Practice Info',
    'Professional Profile',
    'Firm Structure',
    'Services Catalog',
    'Workflow Rules',
    'Client Migration',
  ];

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-1">
          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 uppercase tracking-wide">
            Onboarding Wizard
          </span>
          <h1 className="text-2xl font-bold text-slate-900">CA Practice Setup Wizard</h1>
          <p className="text-xs text-slate-500">Configure your firm branding, partners, services and quality control workflows</p>
        </div>

        {/* Stepper Progress */}
        <div className="grid grid-cols-6 gap-2 text-center text-xs">
          {stepsList.map((label, idx) => {
            const stepNum = idx + 1;
            const isDone = stepNum < step;
            const isCurrent = stepNum === step;
            return (
              <div
                key={label}
                onClick={() => setStep(stepNum)}
                className={`cursor-pointer p-2 rounded-lg border transition-all ${
                  isCurrent
                    ? 'border-emerald-500 bg-emerald-50/50 text-emerald-900 font-bold'
                    : isDone
                    ? 'border-slate-300 bg-slate-100 text-slate-700'
                    : 'border-slate-200 text-slate-400'
                }`}
              >
                <div className="flex items-center justify-center mb-1">
                  {isDone ? (
                    <Check className="h-4 w-4 text-emerald-600" />
                  ) : (
                    <span className={`h-5 w-5 rounded-full flex items-center justify-center text-[10px] ${isCurrent ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-600'}`}>
                      {stepNum}
                    </span>
                  )}
                </div>
                <span className="hidden sm:inline">{label}</span>
              </div>
            );
          })}
        </div>

        {/* Wizard Step Body */}
        <Card className="border border-slate-200 shadow-sm">
          <CardContent className="p-6">
            {step === 1 && (
              <div className="space-y-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-emerald-600" />
                  Step 1: Practice Information
                </CardTitle>
                <div className="grid md:grid-cols-2 gap-4">
                  <Input label="Firm / Practice Name" value={firmName} onChange={(e) => setFirmName(e.target.value)} required />
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Constitution Type</label>
                    <select
                      value={firmType}
                      onChange={(e) => setFirmType(e.target.value)}
                      className="w-full text-sm border border-slate-300 rounded-md px-3 py-2 bg-white"
                    >
                      <option value="sole_proprietorship">Sole Practicing CA</option>
                      <option value="partnership">Partnership CA Firm</option>
                      <option value="llp">LLP Practice</option>
                      <option value="tax_consultant">Independent Tax Practitioner</option>
                    </select>
                  </div>
                  <Input label="ICAI Firm Registration No. (FRN)" value={icaiFrn} onChange={(e) => setIcaiFrn(e.target.value)} placeholder="e.g. 012345S" />
                  <Input label="Managing Partner / Contact" value={primaryContact} onChange={(e) => setPrimaryContact(e.target.value)} required />
                  <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} />
                  <Input label="State" value={state} onChange={(e) => setState(e.target.value)} />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <UserCheck className="h-5 w-5 text-emerald-600" />
                  Step 2: Professional Profile & Registration
                </CardTitle>
                <div className="grid md:grid-cols-2 gap-4">
                  <Input label="Official Practice Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                  <Input label="Practice Phone / Mobile" value={phone} onChange={(e) => setPhone(e.target.value)} required />
                </div>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2 text-xs text-slate-600">
                  <p className="font-semibold text-slate-800">ICAI Compliance Note:</p>
                  <p>TaxShield records official membership and FRN details for authentic workpaper headers and UDIN linkage. TaxShield does NOT automate portal credentials or pretend to generate digital signatures.</p>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-emerald-600" />
                  Step 3: Firm Structure & Partners
                </CardTitle>
                <p className="text-xs text-slate-500">Add the signing partners and branch offices in your CA firm.</p>
                <div className="space-y-3">
                  {partners.map((p, idx) => (
                    <div key={idx} className="flex items-center gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <div className="h-8 w-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs">
                        P{idx + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-xs font-bold text-slate-900">{p.name}</p>
                        <p className="text-[11px] text-slate-500">ICAI Membership: {p.membership} • COP: Active</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-emerald-600" />
                  Step 4: Services Provided
                </CardTitle>
                <p className="text-xs text-slate-500">Select the practice services your firm provides to clients:</p>
                <div className="grid sm:grid-cols-2 gap-3 text-xs">
                  {[
                    { code: 'ACC-01', name: 'Monthly Bookkeeping & Accounting' },
                    { code: 'ACC-02', name: 'Bank Reconciliation & Scrutiny' },
                    { code: 'ACC-03', name: 'Schedule III Financial Statements' },
                    { code: 'GST-01', name: 'GSTR-1 & GSTR-3B Monthly Returns' },
                    { code: 'GST-02', name: '8-Way GSTR-2B vs Books Recon' },
                    { code: 'ITR-01', name: 'Individual & Salaried Tax Returns' },
                    { code: 'ITR-03', name: 'Corporate Tax Returns (ITR-6)' },
                    { code: 'TDS-01', name: 'Quarterly TDS (Form 24Q / 26Q)' },
                    { code: 'AUD-01', name: 'Tax Audit Sec 44AB (Form 3CD)' },
                    { code: 'AUD-02', name: 'Statutory Company Audit' },
                  ].map((s) => (
                    <label
                      key={s.code}
                      onClick={() => toggleService(s.code)}
                      className={`flex items-center gap-2.5 p-3 rounded-lg border cursor-pointer transition-all ${
                        selectedServices.includes(s.code)
                          ? 'border-emerald-500 bg-emerald-50/40 text-emerald-950 font-semibold'
                          : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedServices.includes(s.code)}
                        onChange={() => {}}
                        className="rounded text-emerald-600 focus:ring-emerald-500"
                      />
                      <span>{s.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {step === 5 && (
              <div className="space-y-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-emerald-600" />
                  Step 5: Quality Control & Review Rules (ICAI SQC-1)
                </CardTitle>
                <div className="space-y-3 text-xs">
                  <label className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <input type="checkbox" defaultChecked disabled className="rounded text-emerald-600 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-900 block">Enforce Independent Maker-Checker Review</span>
                      <span className="text-slate-500">Preparer cannot approve their own work when firm policy requires manager/partner sign-off.</span>
                    </div>
                  </label>
                  <label className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <input type="checkbox" defaultChecked disabled className="rounded text-emerald-600 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-900 block">Automatic Recurring Statutory Task Generation</span>
                      <span className="text-slate-500">Automatically instantiate monthly GSTR-1, 3B and quarterly TDS tasks on the 1st of each period.</span>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {step === 6 && (
              <div className="space-y-4">
                <CardTitle className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Check className="h-5 w-5 text-emerald-600" />
                  Step 6: Ready to Launch Practice
                </CardTitle>
                <p className="text-xs text-slate-600">
                  Your firm profile is configured with {selectedServices.length} practice services, {partners.length} signing partners, and SQC-1 quality control workflows enabled.
                </p>
                <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200 text-xs text-emerald-900 space-y-1">
                  <p className="font-bold">Next Steps in TaxShield Professional:</p>
                  <p>• Add or import client records via Client Master 360°</p>
                  <p>• Review approaching statutory deadlines on Compliance Calendar</p>
                  <p>• Distribute tasks and monitor team capacity</p>
                </div>
              </div>
            )}

            {/* Stepper Navigation Buttons */}
            <div className="flex items-center justify-between pt-6 border-t border-slate-200 mt-6">
              {step > 1 ? (
                <Button variant="secondary" size="sm" onClick={() => setStep(step - 1)}>
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
              ) : <div />}

              {step < 6 ? (
                <Button size="sm" onClick={() => setStep(step + 1)} className="bg-emerald-600 hover:bg-emerald-500 text-white">
                  Next Step
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              ) : (
                <Button size="sm" onClick={handleFinish} disabled={saving} className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
                  {saving ? 'Completing Setup...' : 'Launch Practice Workspace'}
                  <Sparkles className="h-4 w-4 ml-1" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

