import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { ConsentBanner } from '@/components/ui/ConsentBanner';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'TaxShield — Financial & Compliance OS for Indian Small Businesses',
    template: '%s — TaxShield',
  },
  description: 'Record once. TaxShield handles accounting, invoicing, GST, TDS, reconciliation, documents, compliance and reporting — deterministic and private.',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
        <ConsentBanner />
      </body>
    </html>
  );
}