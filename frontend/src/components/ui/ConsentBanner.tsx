'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

const KEY = 'taxshield_cookie_ack';

/** No-dark-pattern notice: essential session only, no tracking. One acknowledgement, remembered. */
export function ConsentBanner() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(KEY)) setShow(true);
    } catch {
      setShow(true);
    }
  }, []);

  if (!show) return null;

  const ack = () => {
    try {
      localStorage.setItem(KEY, new Date().toISOString());
    } catch { /* ignore */ }
    setShow(false);
  };

  return (
    <div className="fixed bottom-0 inset-x-0 z-50 p-4" role="dialog" aria-label="Cookie notice">
      <div className="max-w-3xl mx-auto bg-white border border-gray-200 rounded-xl shadow-lg p-4 text-sm flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <p className="text-gray-600 flex-1">
          TaxShield uses only an essential sign-in session plus on-device preferences — no analytics or ad cookies.
          See <Link href="/cookie-policy" className="text-primary-700 hover:underline">Cookie Policy</Link>.
        </p>
        <button onClick={ack} className="px-4 py-2 font-medium text-white bg-primary-600 rounded-lg whitespace-nowrap">
          Understood
        </button>
      </div>
    </div>
  );
}
