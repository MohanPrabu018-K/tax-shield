'use client';

export type UserType = 'individual' | 'freelancer' | 'business' | 'accountant' | 'ca';

export interface WorkspaceProfile {
  userType: UserType;
  businessName: string;
  businessType: string;
  gstApplicable: boolean;
  tdsApplicable: boolean;
  incomeSources: string[];
  taxPeriod: string;
  completedAt: string;
}

const KEY = 'taxshield_workspace';

export function getWorkspace(): WorkspaceProfile | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as WorkspaceProfile) : null;
  } catch {
    return null;
  }
}

export function saveWorkspace(profile: WorkspaceProfile) {
  localStorage.setItem(KEY, JSON.stringify(profile));
}

export function clearWorkspace() {
  localStorage.removeItem(KEY);
}

/** Modules shown for a user type. Individuals see a simple product; practices see PRACTICE. */
export function visibleModules(userType: UserType | undefined): Set<string> {
  const all = new Set(['practice', 'pos', 'inventory', 'gst', 'tds']);
  if (!userType) return all;
  if (userType === 'individual') {
    all.delete('practice');
    all.delete('pos');
    all.delete('inventory');
  }
  if (userType === 'freelancer') {
    all.delete('practice');
    all.delete('pos');
    all.delete('inventory');
  }
  if (userType === 'business') return all;
  // accountant / ca: everything
  return all;
}
