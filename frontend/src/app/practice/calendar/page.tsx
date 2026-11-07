'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  Calendar as CalendarIcon,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';

const STATUTORY_EVENTS = [
  { day: '07', title: 'TDS / TCS Deposit', description: 'Monthly deposit of tax deducted at source under Chapter XVII-B', category: 'tds', urgency: 'HIGH' },
  { day: '11', title: 'GSTR-1 Outward Supplies', description: 'Monthly details of outward supplies for regular taxpayers', category: 'gst', urgency: 'CRITICAL' },
  { day: '13', title: 'Invoice Furnishing Facility (IFF)', description: 'Quarterly taxpayers (QRMP) optional B2B invoice upload', category: 'gst', urgency: 'MEDIUM' },
  { day: '15', title: 'Advance Tax Installment / PF ECR', description: 'Statutory advance tax payment & EPF/ESIC monthly deposit', category: 'tax', urgency: 'HIGH' },
  { day: '20', title: 'GSTR-3B Return & Net Tax Settlement', description: 'Monthly summary return, ITC reconciliation, and cash ledger offset', category: 'gst', urgency: 'CRITICAL' },
  { day: '31', title: 'Quarterly TDS Return (26Q / 24Q)', description: 'Filing of quarterly withholding return with OLTAS challans', category: 'tds', urgency: 'CRITICAL' },
];

export default function ComplianceCalendarPage() {
  const [selectedMonth, setSelectedMonth] = useState('November 2024');

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">Practice Compliance Calendar</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                INDIAN STATUTORY DEADLINES
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Source-verified statutory due dates across Direct Tax, GST, TDS and ROC linked to client obligations
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" className="text-xs">
              <ChevronLeft className="h-3.5 w-3.5 mr-1" />
              Prev Month
            </Button>
            <span className="text-xs font-bold px-3 py-1.5 bg-slate-100 rounded-md border border-slate-200">
              {selectedMonth}
            </span>
            <Button size="sm" variant="secondary" className="text-xs">
              Next Month
              <ChevronRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </div>
        </div>

        {/* Calendar Timeline Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {STATUTORY_EVENTS.map((ev, idx) => (
            <Card key={idx} className="border border-slate-200 shadow-sm hover:border-emerald-400 transition-all">
              <CardContent className="p-4 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <div className="h-10 w-10 rounded-xl bg-slate-900 text-emerald-400 flex flex-col items-center justify-center font-bold">
                    <span className="text-sm leading-none">{ev.day}</span>
                    <span className="text-[8px] uppercase tracking-wider text-slate-400">Nov</span>
                  </div>
                  <Badge variant={ev.urgency === 'CRITICAL' ? 'danger' : 'medium'}>
                    {ev.urgency}
                  </Badge>
                </div>

                <div>
                  <h3 className="font-bold text-slate-900 text-sm">{ev.title}</h3>
                  <p className="text-slate-500 text-[11px] mt-1">{ev.description}</p>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                  <span className="capitalize font-semibold text-slate-700">Category: {ev.category}</span>
                  <span className="text-emerald-700 font-bold">All Applicable Clients</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Annual Milestone Dates Banner */}
        <Card className="border border-slate-200 shadow-sm bg-slate-50">
          <CardHeader className="px-5 py-3 border-b border-slate-200/80">
            <CardTitle className="text-xs font-bold uppercase tracking-wide text-slate-800">
              Annual Statutory Filing Milestones
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <p className="font-bold text-slate-900">31st July</p>
                <p className="text-slate-500 text-[11px] mt-0.5">Non-Audit ITR (Individuals / Salaried / Presumptive 44AD)</p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <p className="font-bold text-slate-900">30th September</p>
                <p className="text-slate-500 text-[11px] mt-0.5">Tax Audit Report Sec 44AB (Form 3CA/3CB & 3CD with UDIN)</p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <p className="font-bold text-slate-900">31st October</p>
                <p className="text-slate-500 text-[11px] mt-0.5">Audited Corporate & Tax Audit ITR (ITR-5 & ITR-6)</p>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <p className="font-bold text-slate-900">31st December</p>
                <p className="text-slate-500 text-[11px] mt-0.5">Annual GST Return (GSTR-9 & Reconciliation GSTR-9C)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

