'use client';

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
} from 'lucide-react';
import { getWorkspace, visibleModules } from '@/lib/workspace';

interface NavItem {
  name: string;
  href: string;
  icon: any;
  module?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const GROUPS: NavGroup[] = [
  { label: 'Home', items: [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Onboarding', href: '/onboarding', icon: Sparkles },
    { name: 'Search', href: '/search', icon: Search },
    { name: 'Notifications', href: '/notifications', icon: Bell },
  ]},
  { label: 'Money', items: [
    { name: 'Transactions', href: '/transactions', icon: CreditCard },
    { name: 'Banking', href: '/banking', icon: Landmark },
    { name: 'Customers', href: '/customers', icon: Users },
    { name: 'Vendors', href: '/vendors', icon: UserRound },
    { name: 'Receivables', href: '/receivables', icon: FileText },
    { name: 'Payables', href: '/payables', icon: Receipt },
  ]},
  { label: 'Sell', items: [
    { name: 'Invoices', href: '/invoices', icon: FileText },
    { name: 'POS', href: '/pos', icon: ShoppingCart, module: 'pos' },
  ]},
  { label: 'Accounting', items: [
    { name: 'Books', href: '/accounting', icon: BookOpen },
  ]},
  { label: 'Tax', items: [
    { name: 'Income Tax', href: '/tax', icon: Scale },
    { name: 'AIS / 26AS', href: '/ais', icon: Sheet },
    { name: 'GST', href: '/gst', icon: Receipt, module: 'gst' },
    { name: 'TDS', href: '/tds', icon: Droplets, module: 'tds' },
  ]},
  { label: 'Compliance', items: [
    { name: 'Compliance', href: '/compliance', icon: ShieldCheck },
    { name: 'Month-End', href: '/close', icon: ClipboardCheck },
    { name: 'Obligations', href: '/obligations', icon: ShieldCheck },
    { name: 'Deadlines', href: '/deadlines', icon: ClipboardCheck },
  ]},
  { label: 'Manage', items: [
    { name: 'Documents', href: '/documents', icon: FolderOpen },
    { name: 'Reports', href: '/reports', icon: LineChart },
    { name: 'Intelligence', href: '/intelligence', icon: Sparkles },
    { name: 'Inventory', href: '/inventory', icon: Boxes, module: 'inventory' },
    { name: 'Scenarios', href: '/scenarios', icon: LineChart },
    { name: 'Assistant', href: '/assistant', icon: MessageCircle },
    { name: 'Billing', href: '/billing', icon: CreditCard },
    { name: 'Support', href: '/support', icon: LifeBuoy },
    { name: 'Practice', href: '/practice', icon: Briefcase, module: 'practice' },
    { name: 'Admin', href: '/admin', icon: ShieldCheck },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]},
];

export function Sidebar() {
  const pathname = usePathname();
  const profile = typeof window !== 'undefined' ? getWorkspace() : null;
  const visible = visibleModules(profile?.userType);

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 hidden lg:block" aria-label="Primary">
      <div className="flex flex-col h-full">
        <div className="flex items-center h-16 px-6 border-b border-gray-100">
          <Link href="/dashboard" className="flex items-center gap-2">
            <ShieldCheck className="h-8 w-8 text-primary-600" aria-hidden="true" />
            <span className="text-xl font-bold text-gray-900">Tax Shield</span>
          </Link>
        </div>
        <nav className="flex-1 px-4 py-4 space-y-4 overflow-y-auto" aria-label="Main navigation">
          {GROUPS.map((group) => {
            const items = group.items.filter((i) => !i.module || visible.has(i.module));
            if (items.length === 0) return null;
            return (
              <div key={group.label}>
                <p className="px-3 pb-1 text-xs font-semibold uppercase tracking-wider text-gray-400">
                  {group.label}
                </p>
                <div className="space-y-1">
                  {items.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                          isActive
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        )}
                        aria-current={isActive ? 'page' : undefined}
                      >
                        <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                        {item.name}
                      </Link>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-100">
          <p className="text-xs text-gray-500 text-center">Tax Shield · Financial OS</p>
        </div>
      </div>
    </aside>
  );
}
