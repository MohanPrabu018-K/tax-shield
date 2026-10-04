import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Phase 1: safe edge middleware — headers only, no auth decisions here.
// Auth stays in DashboardLayout + server-side JWT checks. Private app
// routes get X-Robots-Tag: noindex so dashboards are never indexed.
const PRIVATE_PREFIXES = [
  '/dashboard',
  '/transactions',
  '/documents',
  '/obligations',
  '/deadlines',
  '/scenarios',
  '/reports',
  '/assistant',
  '/settings',
];

export function middleware(request: NextRequest) {
  const requestId =
    request.headers.get('x-request-id') ?? Math.random().toString(36).slice(2, 12);
  const response = NextResponse.next();
  response.headers.set('x-request-id', requestId);
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set(
    'Permissions-Policy',
    'microphone=(self), camera=()'
  );
  const path = request.nextUrl.pathname;
  if (PRIVATE_PREFIXES.some((p) => path === p || path.startsWith(p + '/'))) {
    response.headers.set('X-Robots-Tag', 'noindex, nofollow');
  }
  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
