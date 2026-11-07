'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { saveWorkspace, getWorkspace, UserType } from '@/lib/workspace';
import { INCOME_CATEGORIES } from '@/types';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

const STEPS = ['You', 'Business', 'Tax setup', 'Done'];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [userType, setUserType] = useState<UserType>('individual');
  const [businessName, setBusinessName] = useState('');
  const [businessType, setBusinessType] = useState('services');
  const [gstApplicable, setGstApplicable] = useState(false);
  const [tdsApplicable, setTdsApplicable] = useState(false);
  const [incomeSources, setIncomeSources] = useState<string[]>(['salary']);
  const [taxPeriod, setTaxPeriod] = useState('2024-25');

  // Server-persisted onboarding: hydrate from backend, fall back to localStorage
  useEffect(() => {
    (async () => {
      try {
        const r: any = await api.getOnboarding?.();
        const o = r?.onboarding;
        if (o) {
          if (o.userType) setUserType(o.userType);
          if (o.businessName) setBusinessName(o.businessName);
          if (o.businessType) setBusinessType(o.businessType);
          if (typeof o.gstApplicable === 'boolean') setGstApplicable(o.gstApplicable);
          if (typeof o.tdsApplicable === 'boolean') setTdsApplicable(o.tdsApplicable);
          if (Array.isArray(o.incomeSources) && o.incomeSources.length) setIncomeSources(o.incomeSources);
          if (o.taxPeriod) setTaxPeriod(o.taxPeriod);
          if (typeof o.step === 'number') setStep(Math.min(o.step, STEPS.length - 1));
          return;
        }
      } catch {}
      const local = getWorkspace();
      if (local) {
        setUserType(local.userType); setBusinessName(local.businessName);
        setBusinessType(local.businessType); setGstApplicable(local.gstApplicable);
        setTdsApplicable(local.tdsApplicable); setIncomeSources(local.incomeSources);
        setTaxPeriod(local.taxPeriod);
      }
    })();
  }, []);

  const persist = async (partial: any = {}) => {
    const profile: any = {
      userType, businessName, businessType, gstApplicable, tdsApplicable,
      incomeSources, taxPeriod, ...partial,
    };
    try { await api.putOnboarding?.(profile); } catch {}
    saveWorkspace({ ...profile, completedAt: profile.completedAt || new Date().toISOString() });
  };

  const toggleSource = (v: string) => {
    setIncomeSources((s) => {
      const next = s.includes(v) ? s.filter((x) => x !== v) : [...s, v];
      persist({ incomeSources: next });
      return next;
    });
  };

  const next = () => {
    const ns = Math.min(step + 1, STEPS.length - 1);
    setStep(ns);
    persist({ step: ns });
  };
  const back = () => setStep((s) => Math.max(s - 1, 0));

  const finish = () => {
    if (incomeSources.length === 0) {
      toast.error('Pick at least one income source');
      return;
    }
    const done = new Date().toISOString();
    persist({ completedAt: done });
    toast.success('Workspace ready');
    router.push('/dashboard');
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900">Set up your workspace</h2>
        <ol className="flex gap-2 mt-3 mb-6" aria-label="Progress">
          {STEPS.map((label, i) => (
            <li key={label} className={`flex-1 h-2 rounded-full ${i <= step ? 'bg-primary-600' : 'bg-gray-200'}`} aria-label={label} />
          ))}
        </ol>

        {step === 0 && (
          <Card>
            <CardHeader><CardTitle>Who are you?</CardTitle></CardHeader>
            <CardContent>
              <Select
                label="User type"
                value={userType}
                onChange={(e) => setUserType(e.target.value as UserType)}
                options={[
                  { value: 'individual', label: 'Individual' },
                  { value: 'freelancer', label: 'Freelancer' },
                  { value: 'business', label: 'Small business' },
                  { value: 'accountant', label: 'Accountant' },
                  { value: 'ca', label: 'CA / Practice' },
                ]}
              />
              <div className="flex justify-end mt-4">
                <Button onClick={next}>Continue</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 1 && (
          <Card>
            <CardHeader><CardTitle>Business setup</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input label="Business / display name" value={businessName} onChange={(e) => setBusinessName(e.target.value)} placeholder="e.g. Sharma Services" />
                <Select
                  label="Business type"
                  value={businessType}
                  onChange={(e) => setBusinessType(e.target.value)}
                  options={[
                    { value: 'services', label: 'Services' },
                    { value: 'shop', label: 'Shop / retail' },
                    { value: 'consulting', label: 'Consulting / professional' },
                    { value: 'manufacturing', label: 'Manufacturing' },
                    { value: 'other', label: 'Other' },
                  ]}
                />
                <fieldset>
                  <legend className="text-sm font-medium text-gray-700 mb-1">Income sources</legend>
                  <div className="flex flex-wrap gap-2">
                    {INCOME_CATEGORIES.map((c) => (
                      <button
                        key={c.value}
                        type="button"
                        onClick={() => toggleSource(c.value)}
                        aria-pressed={incomeSources.includes(c.value)}
                        className={`px-3 py-1.5 rounded-full text-sm border ${incomeSources.includes(c.value) ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'}`}
                      >
                        {c.label}
                      </button>
                    ))}
                  </div>
                </fieldset>
              </div>
              <div className="flex justify-between mt-4">
                <Button variant="secondary" onClick={back}>Back</Button>
                <Button onClick={next}>Continue</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 2 && (
          <Card>
            <CardHeader><CardTitle>Tax setup</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Select
                  label="Tax period (financial year)"
                  value={taxPeriod}
                  onChange={(e) => setTaxPeriod(e.target.value)}
                  options={[
                    { value: '2024-25', label: 'FY 2024-25' },
                    { value: '2023-24', label: 'FY 2023-24' },
                  ]}
                />
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input type="checkbox" checked={gstApplicable} onChange={(e) => setGstApplicable(e.target.checked)} className="h-4 w-4" />
                  GST applicable (registered / needs GST tracking)
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input type="checkbox" checked={tdsApplicable} onChange={(e) => setTdsApplicable(e.target.checked)} className="h-4 w-4" />
                  TDS applicable (deducts or suffers TDS)
                </label>
              </div>
              <div className="flex justify-between mt-4">
                <Button variant="secondary" onClick={back}>Back</Button>
                <Button onClick={next}>Continue</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 3 && (
          <Card>
            <CardHeader><CardTitle>Ready</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                {userType} · {incomeSources.length} income source(s) · FY {taxPeriod}
                {gstApplicable ? ' · GST' : ''}{tdsApplicable ? ' · TDS' : ''}.
                Your dashboard adapts to this profile. You can change it anytime by redoing this setup.
              </p>
              <div className="flex justify-between mt-4">
                <Button variant="secondary" onClick={back}>Back</Button>
                <Button onClick={finish}>Go to dashboard</Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
