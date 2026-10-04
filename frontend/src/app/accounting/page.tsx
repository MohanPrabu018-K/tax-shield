'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { formatCurrency } from '@/lib/utils';
import { Plus } from 'lucide-react';
import toast from 'react-hot-toast';

type Tab = 'accounts' | 'journals' | 'trial' | 'pl' | 'bs' | 'cash';

export default function AccountingPage() {
  const [tab, setTab] = useState<Tab>('accounts');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showJournal, setShowJournal] = useState(false);
  const [narration, setNarration] = useState('');
  const [lines, setLines] = useState([{ account_code: '1010', debit: '', credit: '' }, { account_code: '4000', debit: '', credit: '' }]);
  const [ledgerCode, setLedgerCode] = useState('1010');
  const [ledger, setLedger] = useState<any>(null);

  const load = async (t: Tab = tab) => {
    setLoading(true);
    setError(null);
    try {
      await api.ensureAccounts();
      let result: any = null;
      if (t === 'accounts') result = await api.getAccounts();
      if (t === 'journals') result = await api.getJournals(0, 100);
      if (t === 'trial') result = await api.getTrialBalance();
      if (t === 'pl') result = await api.getProfitLoss();
      if (t === 'bs') result = await api.getBalanceSheet();
      if (t === 'cash') result = await api.getCashFlow();
      setData(result);
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const switchTab = (t: Tab) => { setTab(t); setData(null); load(t); };

  const postJournal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.postJournal({
        narration,
        lines: lines.map((l) => ({ account_code: l.account_code, debit: parseFloat(l.debit || '0'), credit: parseFloat(l.credit || '0') })),
        idempotency_key: `ui-${Date.now()}`,
      });
      toast.success('Journal posted — debits equal credits');
      setShowJournal(false);
      setNarration('');
      load('journals');
      setTab('journals');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Unbalanced or invalid journal');
    }
  };

  const viewLedger = async () => {
    try {
      setLedger(await api.getLedger(ledgerCode));
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Ledger failed');
    }
  };

  const reverse = async (id: string) => {
    if (!window.confirm('Reverse this entry with an offsetting journal?')) return;
    try {
      await api.reverseJournal(id, 'Manual reversal');
      toast.success('Reversed');
      load('journals');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Reverse failed');
    }
  };

  const tabs: { id: Tab; label: string }[] = [
    { id: 'accounts', label: 'Chart of Accounts' },
    { id: 'journals', label: 'Journal Entries' },
    { id: 'trial', label: 'Trial Balance' },
    { id: 'pl', label: 'Profit & Loss' },
    { id: 'bs', label: 'Balance Sheet' },
    { id: 'cash', label: 'Cash Flow' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Books</h2>
            <p className="text-gray-500 mt-1">You record business events — TaxShield posts the accounting</p>
          </div>
          <Button onClick={() => setShowJournal(true)}><Plus className="h-4 w-4 mr-2" />Manual Journal</Button>
        </div>

        <div className="flex gap-2 flex-wrap" role="tablist" aria-label="Accounting views">
          {tabs.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => switchTab(t.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium border ${tab === t.id ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {loading ? <PageLoading /> : error ? <ErrorState message={error} onRetry={() => load()} /> : (
          <>
            {tab === 'accounts' && (
              <Card><CardHeader><CardTitle>Chart of Accounts ({data?.length || 0})</CardTitle></CardHeader>
                <CardContent className="p-0">
                  <Table><TableHeader><TableRow><TableHead>Code</TableHead><TableHead>Name</TableHead><TableHead>Type</TableHead></TableRow></TableHeader>
                    <TableBody>{(data || []).map((a: any) => (
                      <TableRow key={a.code}><TableCell className="font-mono">{a.code}</TableCell><TableCell>{a.name}</TableCell><TableCell className="capitalize">{a.type}</TableCell></TableRow>
                    ))}</TableBody></Table>
                </CardContent></Card>
            )}
            {tab === 'journals' && (
              <Card><CardHeader><CardTitle>Journal Entries</CardTitle></CardHeader>
                <CardContent>
                  {(data || []).length === 0 ? <EmptyState title="No entries yet" body="Entries appear automatically from transactions, invoices and POS bills — or post one manually." /> : (
                    <div className="space-y-3">
                      {data.map((j: any) => (
                        <div key={j.id} className="border border-gray-100 rounded-lg p-3 text-sm">
                          <div className="flex justify-between items-start gap-2">
                            <div>
                              <p className="font-medium">{j.narration || 'Journal'} <span className="text-gray-400 font-normal">· {String(j.date).slice(0, 10)}</span></p>
                              {j.lines.map((l: any, i: number) => (
                                <p key={i} className="text-gray-600 font-mono text-xs">{l.account_code} · Dr {formatCurrency(l.debit)} · Cr {formatCurrency(l.credit)}</p>
                              ))}
                            </div>
                            <Button variant="secondary" size="sm" onClick={() => reverse(j.id)}>Reverse</Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent></Card>
            )}
            {tab === 'trial' && (
              <Card><CardHeader><CardTitle>Trial Balance · {data?.balanced ? 'Balanced ✓' : 'Out of balance ✗'}</CardTitle></CardHeader>
                <CardContent className="p-0">
                  <Table><TableHeader><TableRow><TableHead>Account</TableHead><TableHead className="text-right">Debit</TableHead><TableHead className="text-right">Credit</TableHead></TableRow></TableHeader>
                    <TableBody>
                      {(data?.rows || []).map((r: any) => (
                        <TableRow key={r.code}><TableCell>{r.code} · {r.name}</TableCell><TableCell className="text-right">{formatCurrency(r.debit)}</TableCell><TableCell className="text-right">{formatCurrency(r.credit)}</TableCell></TableRow>
                      ))}
                      <TableRow><TableCell className="font-bold">Total</TableCell><TableCell className="text-right font-bold">{formatCurrency(data?.total_debit)}</TableCell><TableCell className="text-right font-bold">{formatCurrency(data?.total_credit)}</TableCell></TableRow>
                    </TableBody></Table>
                </CardContent></Card>
            )}
            {tab === 'pl' && (
              <Card><CardHeader><CardTitle>Profit & Loss</CardTitle></CardHeader>
                <CardContent>
                  {[['Revenue', data?.revenue], ['COGS', data?.cogs], ['Gross profit', data?.gross_profit], ['Total expenses', data?.total_expenses], ['Net profit', data?.net_profit]].map(([k, v]) => (
                    <p key={k as string} className="flex justify-between py-2 border-b border-gray-100 text-sm"><span>{k}</span><strong>{formatCurrency(v as number)}</strong></p>
                  ))}
                </CardContent></Card>
            )}
            {tab === 'bs' && (
              <Card><CardHeader><CardTitle>Balance Sheet · {data?.balanced ? 'Balanced ✓' : 'Out of balance ✗'}</CardTitle></CardHeader>
                <CardContent>
                  {[['Assets', data?.assets], ['Liabilities', data?.liabilities], ['Equity', data?.equity], ['Net profit (in equity)', data?.net_profit], ['Equity total', data?.equity_total]].map(([k, v]) => (
                    <p key={k as string} className="flex justify-between py-2 border-b border-gray-100 text-sm"><span>{k}</span><strong>{formatCurrency(v as number)}</strong></p>
                  ))}
                </CardContent></Card>
            )}
            {tab === 'cash' && (
              <Card><CardHeader><CardTitle>Cash Flow</CardTitle></CardHeader>
                <CardContent>
                  {[['Operating', data?.operating], ['Investing', data?.investing], ['Financing', data?.financing], ['Net change', data?.net_change]].map(([k, v]) => (
                    <p key={k as string} className="flex justify-between py-2 border-b border-gray-100 text-sm"><span>{k}</span><strong>{formatCurrency(v as number)}</strong></p>
                  ))}
                </CardContent></Card>
            )}
          </>
        )}

        <Card>
          <CardHeader><CardTitle>General Ledger — account lookup</CardTitle></CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input value={ledgerCode} onChange={(e) => setLedgerCode(e.target.value)} placeholder="Account code, e.g. 1010" aria-label="Account code" className="max-w-xs" />
              <Button variant="secondary" onClick={viewLedger}>View</Button>
            </div>
            {ledger && (
              <div className="mt-3 text-sm">
                <p className="font-medium">{ledger.account?.code} · {ledger.account?.name} · Balance {formatCurrency(ledger.balance)}</p>
                {(ledger.entries || []).slice(0, 20).map((e: any, i: number) => (
                  <p key={i} className="text-gray-600 font-mono text-xs">{String(e.date).slice(0, 10)} · Dr {formatCurrency(e.debit)} · Cr {formatCurrency(e.credit)} · bal {formatCurrency(e.balance)}</p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Modal isOpen={showJournal} onClose={() => setShowJournal(false)} title="Manual Journal (must balance)" size="lg">
          <form onSubmit={postJournal} className="space-y-4">
            <Input label="Narration" value={narration} onChange={(e) => setNarration(e.target.value)} required />
            {lines.map((l, i) => (
              <div key={i} className="grid grid-cols-3 gap-2">
                <Input label={i === 0 ? 'Account' : ''} value={l.account_code} onChange={(e) => setLines(lines.map((x, j) => (j === i ? { ...x, account_code: e.target.value } : x)))} aria-label={`Line ${i + 1} account`} />
                <Input label={i === 0 ? 'Debit' : ''} type="number" step="0.01" value={l.debit} onChange={(e) => setLines(lines.map((x, j) => (j === i ? { ...x, debit: e.target.value } : x)))} aria-label={`Line ${i + 1} debit`} />
                <Input label={i === 0 ? 'Credit' : ''} type="number" step="0.01" value={l.credit} onChange={(e) => setLines(lines.map((x, j) => (j === i ? { ...x, credit: e.target.value } : x)))} aria-label={`Line ${i + 1} credit`} />
              </div>
            ))}
            <div className="flex justify-between">
              <Button variant="secondary" type="button" onClick={() => setLines([...lines, { account_code: '', debit: '', credit: '' }])}>Add line</Button>
              <Button type="submit">Post (balanced only)</Button>
            </div>
          </form>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
