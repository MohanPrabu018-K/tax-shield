'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Shield, Building2, UserCheck, ArrowRight, CheckCircle2, Lock, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import toast from 'react-hot-toast';

export default function PilotRegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Form fields
  const [firmName, setFirmName] = useState('');
  const [contactName, setContactName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [firmType, setFirmType] = useState('solo_ca');
  const [officeLocation, setOfficeLocation] = useState('');
  const [partnerCount, setPartnerCount] = useState(1);
  const [staffCount, setStaffCount] = useState(3);
  const [clientPortfolioSize, setClientPortfolioSize] = useState(35);
  const [existingSoftware, setExistingSoftware] = useState('Tally Prime & Excel');
  const [expectedUsage, setExpectedUsage] = useState('Client management, GSTR-2B 8-way recon, and document collection');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firmName || !contactName || !email || !phone || !officeLocation || !password) {
      toast.error('Please fill in all mandatory fields');
      return;
    }

    setLoading(true);
    try {
      const res = await api.registerPilotFirm({
        firm_name: firmName,
        contact_name: contactName,
        email,
        phone,
        password,
        firm_type: firmType,
        office_location: officeLocation,
        partner_count: Number(partnerCount),
        staff_count: Number(staffCount),
        client_portfolio_size: Number(clientPortfolioSize),
        major_services: ['accounting', 'gst', 'income_tax', 'audit'],
        existing_software: existingSoftware,
        accounting_workflow: 'Monthly Retainer & Compliance',
        expected_usage: expectedUsage,
        responsible_contact: contactName,
      });

      // Auto sign in with the new credentials
      const loginRes = await api.login(email, password);
      if (loginRes.access_token) {
        api.setToken(loginRes.access_token);
      }

      setSubmitted(true);
      toast.success('Welcome to the TaxShield Professional Pilot!');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <Shield className="h-10 w-10 text-primary-600" />
            <span className="text-2xl font-bold text-slate-900">Tax Shield Professional</span>
          </Link>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            60-Day Real CA Firm Pilot Cohort (v1.2)
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Apply to Join the 10-Firm CA Pilot
          </h1>
          <p className="mt-2 text-sm text-slate-600 max-w-xl mx-auto">
            Experience complete practice management, Client Portal 2.0, 8-way GSTR-2B reconciliation, SQC-1 quality control, and direct client document automation.
          </p>
        </div>

        {!submitted ? (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 sm:p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Firm Profile Section */}
                <div>
                  <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4 flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-primary-600" />
                    1. Practice & Firm Information
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="sm:col-span-2">
                      <Input
                        label="Full Firm / Practice Name"
                        value={firmName}
                        onChange={(e) => setFirmName(e.target.value)}
                        placeholder="e.g. Sharma & Co. Chartered Accountants"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Practice Archetype</label>
                      <select
                        value={firmType}
                        onChange={(e) => setFirmType(e.target.value)}
                        className="w-full text-sm border border-slate-300 rounded-lg py-2 px-3 focus:ring-2 focus:ring-primary-500 bg-white"
                      >
                        <option value="solo_ca">Solo Practicing CA</option>
                        <option value="multi_partner">Multi-Partner CA Firm</option>
                        <option value="gst_specialist">Specialist GST Advisory</option>
                        <option value="audit_practice">Statutory Audit Practice</option>
                        <option value="accountant">Accounting Practice Owner</option>
                      </select>
                    </div>

                    <div>
                      <Input
                        label="Office Location (City, State)"
                        value={officeLocation}
                        onChange={(e) => setOfficeLocation(e.target.value)}
                        placeholder="e.g. Mumbai, Maharashtra"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Team Scale */}
                <div>
                  <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4 flex items-center gap-2">
                    <UserCheck className="w-5 h-5 text-primary-600" />
                    2. Scale & Client Base
                  </h3>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Input
                        label="Partners"
                        type="number"
                        min={1}
                        max={50}
                        value={partnerCount}
                        onChange={(e) => setPartnerCount(Number(e.target.value))}
                        required
                      />
                    </div>
                    <div>
                      <Input
                        label="Staff & Articles"
                        type="number"
                        min={0}
                        max={100}
                        value={staffCount}
                        onChange={(e) => setStaffCount(Number(e.target.value))}
                        required
                      />
                    </div>
                    <div>
                      <Input
                        label="Active Clients"
                        type="number"
                        min={1}
                        max={2000}
                        value={clientPortfolioSize}
                        onChange={(e) => setClientPortfolioSize(Number(e.target.value))}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
                    <div>
                      <Input
                        label="Existing Primary Software"
                        value={existingSoftware}
                        onChange={(e) => setExistingSoftware(e.target.value)}
                        placeholder="e.g. Tally Prime, Computax, Winman"
                      />
                    </div>
                    <div>
                      <Input
                        label="Primary Expectation from Pilot"
                        value={expectedUsage}
                        onChange={(e) => setExpectedUsage(e.target.value)}
                        placeholder="e.g. Eliminate manual document follow-ups"
                      />
                    </div>
                  </div>
                </div>

                {/* Liaison Account Credentials */}
                <div>
                  <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4 flex items-center gap-2">
                    <Lock className="w-5 h-5 text-primary-600" />
                    3. Designated Partner / Pilot Liaison
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <Input
                        label="Contact Person Name"
                        value={contactName}
                        onChange={(e) => setContactName(e.target.value)}
                        placeholder="CA Your Name"
                        required
                      />
                    </div>
                    <div>
                      <Input
                        label="Official Phone / WhatsApp"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+91 9876543210"
                        required
                      />
                    </div>
                    <div>
                      <Input
                        label="Professional Email Address"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="partner@yourfirm.in"
                        required
                      />
                    </div>
                    <div>
                      <Input
                        label="Create Practice Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Minimum 8 characters"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 space-y-1.5">
                  <p className="font-semibold text-slate-800">Pilot Terms & Confidentiality Guarantee:</p>
                  <p>• Zero financial charges during the 60-day pilot period.</p>
                  <p>• Data ownership remains 100% with your firm; complete export available anytime.</p>
                  <p>• Bank-grade tenant isolation; your clients and records are never visible to other firms.</p>
                </div>

                <Button type="submit" className="w-full py-3 font-bold text-base" disabled={loading}>
                  {loading ? 'Setting up Your Workspace...' : 'Register Firm & Launch Practice Workspace'}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </form>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-emerald-200 p-8 text-center space-y-5">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">
              Welcome to TaxShield Professional, {contactName}!
            </h2>
            <p className="text-sm text-slate-600 max-w-md mx-auto">
              Your practice workspace for <strong>{firmName}</strong> has been provisioned. You can now complete your practice configuration and invite your first clients.
            </p>
            <div className="pt-4 flex justify-center gap-3">
              <Button onClick={() => router.push('/practice/setup')} className="bg-emerald-600 hover:bg-emerald-500 font-bold">
                Configure Practice Profile
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button variant="secondary" onClick={() => router.push('/practice')}>
                Go to Practice Dashboard
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

