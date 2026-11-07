'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  CreditCard,
  Landmark,
  Users,
  UserRound,
  FileText,
  ShoppingCart,
  BookOpen,
  Scale,
  Sheet,
  Droplets,
  Receipt,
  LineChart,
  FolderOpen,
  ShieldCheck,
  ClipboardCheck,
  Boxes,
  Briefcase,
  MessageCircle,
  Settings,
  Sparkles,
  Bell,
  Search,
  LifeBuoy,
  UserCheck,
} from 'lucide-react';
import { getWorkspace, saveWorkspace, visibleModules, UserType } from '@/lib/workspace';

interface NavItem {
  name: string;
  href: string;
  icon: any;
  badge?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const PRACTICE_GROUPS: NavGroup[] = [
  {
    label: 'Practice Management',
    items: [
      { name: 'Practice Overview', href: '/practice', icon: LayoutDashboard },
      { name: 'Practice Setup', href: '/practice/setup', icon: Sparkles },
      { name: 'Client Master 360°', href: '/practice/clients', icon: Users },
      { name: 'Leads & CRM', href: '/practice/crm', icon: UserRound },
      { name: 'Engagements', href: '/practice/engagements', icon: FileText },
    ],
  },
  {
    label: 'Work Management',
    items: [
      { name: 'All Tasks (12 Stages)', href: '/practice/tasks', icon: ClipboardCheck },
      { name: 'Team Workload', href: '/practice/team', icon: Users },
      { name: 'Review Queue', href: '/practice/reviews', icon: ShieldCheck, badge: 'SQC-1' },
      { name: 'Audit Workpapers', href: '/practice/workpapers', icon: BookOpen, badge: 'SA 230' },
    ],
  },
  {
    label: 'Compliance Desks',
    items: [
      { name: 'GST Practice Desk', href: '/practice/gst', icon: Receipt, badge: '8-Way' },
      { name: 'TDS Practice Desk', href: '/practice/tds', icon: Droplets },
      { name: 'Income Tax Desk', href: '/practice/tax', icon: Scale },
      { name: 'UDIN Tracker', href: '/practice/udin', icon: ShieldCheck, badge: 'ICAI' },
      { name: 'Compliance Calendar', href: '/practice/calendar', icon: ClipboardCheck },
    ],
  },
  {
    label: 'Practice Finance',
    items: [
      { name: 'Fee & Billing', href: '/practice/finance', icon: CreditCard },
    ],
  },
  {
    label: 'Client Portal',
    items: [
      { name: 'Client Portal View', href: '/portal', icon: Landmark },
    ],
  },
  {
    label: 'Client Accounting',
    items: [
      { name: 'Books & Ledger', href: '/accounting', icon: BookOpen },
      { name: 'Invoices & Sell', href: '/invoices', icon: FileText },
      { name: 'Banking', href: '/banking', icon: Landmark },
      { name: 'Transactions', href: '/transactions', icon: CreditCard },
      { name: 'AIS / Form 26AS', href: '/ais', icon: Sheet },
      { name: 'Month-End Close', href: '/close', icon: ClipboardCheck },
    ],
  },
  {
    label: 'Intelligence & Settings',
    items: [
      { name: 'CA Assistant', href: '/assistant', icon: MessageCircle, badge: 'AI' },
      { name: 'Reports & Analytics', href: '/reports', icon: LineChart },
      { name: 'Documents Vault', href: '/documents', icon: FolderOpen },
      { name: 'Notifications', href: '/notifications', icon: Bell },
      { name: 'Firm Settings', href: '/settings', icon: Settings },
    ],
  },
];

const PERSONA_OPTIONS: { id: UserType; label: string }[] = [
  { id: 'ca_partner', label: 'Persona: CA Partner / Firm Owner' },
  { id: 'ca', label: 'Persona: Solo Practicing CA' },
  { id: 'accountant', label: 'Persona: Small Accounting Firm' },
  { id: 'gst_specialist', label: 'Persona: GST Specialist' },
  { id: 'tax_specialist', label: 'Persona: Direct Tax Specialist' },
  { id: 'audit_staff', label: 'Persona: Audit Staff (SA 230)' },
  { id: 'client', label: 'Persona: Client Portal (SME Owner)' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [activePersona, setActivePersona] = useState<UserType>('ca_partner');

  useEffect(() => {
    const ws = getWorkspace();
    if (ws?.userType) {
      setActivePersona(ws.userType);
    }
  }, []);

  const handlePersonaChange = (type: UserType) => {
    setActivePersona(type);
    const existing = getWorkspace() || {
      businessName: 'Kailash & Associates, CAs',
      businessType: 'partnership',
      gstApplicable: true,
      tdsApplicable: true,
      incomeSources: ['Profession', 'Audit'],
      taxPeriod: '2024-25',
      completedAt: new Date().toISOString(),
      userType: type,
    };
    saveWorkspace({ ...existing, userType: type });
  };

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-slate-200 border-r border-slate-800 hidden lg:block" aria-label="Primary">
      <div className="flex flex-col h-full">
        {/* Brand Header */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-slate-800 bg-slate-950/40">
          <Link href="/practice" className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="text-base font-bold text-white tracking-tight">TaxShield</span>
              <span className="block text-[10px] font-semibold text-emerald-400 tracking-wider uppercase">Professional</span>
            </div>
          </Link>
        </div>

        {/* Persona Switcher Selector */}
        <div className="px-4 py-3 bg-slate-950/60 border-b border-slate-800/80">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-1.5 flex items-center gap-1">
            <UserCheck className="h-3 w-3 text-emerald-400" />
            Active Role Persona
          </label>
          <select
            value={activePersona}
            onChange={(e) => handlePersonaChange(e.target.value as UserType)}
            className="w-full text-xs bg-slate-800 text-slate-200 border border-slate-700 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          >
            {PERSONA_OPTIONS.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 px-3 py-3 space-y-4 overflow-y-auto" aria-label="Main navigation">
          {PRACTICE_GROUPS.map((group) => (
            <div key={group.label} className="space-y-1">
              <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                {group.label}
              </p>
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href !== '/practice' && item.href !== '/dashboard' && pathname?.startsWith(item.href));
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center justify-between px-3 py-2 text-xs font-medium rounded-md transition-colors',
                      isActive
                        ? 'bg-emerald-500/15 text-emerald-400 font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    )}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={cn('h-4 w-4 shrink-0', isActive ? 'text-emerald-400' : 'text-slate-400')} />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer Status */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-[11px] text-slate-400 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-medium text-slate-300">Practice OS Online</span>
          </div>
          <span className="text-[10px] text-slate-500">v2.0-IN</span>
        </div>
      </div>
    </aside>
  );
}
