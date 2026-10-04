'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Menu, Bell, Search, User, LogOut, LayoutDashboard, CreditCard, FolderOpen, ShieldCheck, CalendarCheck, LineChart, BarChart3, Settings, MessageCircle } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { cn } from '@/lib/utils';

const TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/onboarding': 'Setup',
  '/search': 'Search',
  '/notifications': 'Notifications',
  '/transactions': 'Transactions',
  '/banking': 'Banking & Reconciliation',
  '/customers': 'Customers',
  '/vendors': 'Vendors',
  '/receivables': 'Receivables',
  '/payables': 'Payables',
  '/invoices': 'Invoices',
  '/pos': 'Point of Sale',
  '/accounting': 'Books',
  '/tax': 'Income Tax',
  '/ais': 'AIS / Form 26AS',
  '/gst': 'GST Workspace',
  '/tds': 'TDS Workspace',
  '/compliance': 'Compliance Center',
  '/close': 'Month-End Close',
  '/obligations': 'Obligations',
  '/deadlines': 'Deadlines',
  '/documents': 'Document Center',
  '/reports': 'Reports',
  '/intelligence': 'Business Intelligence',
  '/inventory': 'Inventory',
  '/scenarios': 'Scenarios',
  '/assistant': 'Assistant',
  '/practice': 'CA Practice',
  '/billing': 'Billing',
  '/support': 'Support',
  '/admin': 'Admin Console',
  '/settings': 'Settings',
};

const MOBILE_NAV = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Transactions', href: '/transactions', icon: CreditCard },
  { name: 'Invoices', href: '/invoices', icon: FolderOpen },
  { name: 'Compliance', href: '/compliance', icon: ShieldCheck },
  { name: 'Deadlines', href: '/deadlines', icon: CalendarCheck },
  { name: 'Reports', href: '/reports', icon: BarChart3 },
  { name: 'Assistant', href: '/assistant', icon: MessageCircle },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const currentTitle = TITLES[pathname] || 'Tax Shield';

  return (
    <header className="sticky top-0 z-40 w-full bg-white/95 backdrop-blur-sm border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            aria-label="Toggle menu"
            aria-expanded={mobileMenuOpen}
          >
            <Menu className="h-6 w-6" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900 lg:text-xl hidden sm:block">
            {currentTitle}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/search"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            aria-label="Global search"
          >
            <Search className="h-5 w-5" />
          </Link>
          <Link
            href="/notifications"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
          </Link>

          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 p-1.5 hover:bg-gray-100 rounded-lg"
              aria-expanded={userMenuOpen}
              aria-haspopup="true"
              aria-label="Account menu"
            >
              <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                <User className="h-5 w-5 text-primary-600" />
              </div>
              <span className="hidden sm:block text-sm font-medium text-gray-700">
                {user?.name || 'User'}
              </span>
            </button>

            {userMenuOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} aria-hidden="true" />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                  </div>
                  <Link
                    href="/settings"
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <User className="h-4 w-4" />
                    Profile
                  </Link>
                  <button
                    onClick={() => { logout(); setUserMenuOpen(false); router.push('/login'); }}
                    className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-gray-100 py-4 px-4">
          <nav className="space-y-2" aria-label="Mobile navigation">
            {MOBILE_NAV.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
