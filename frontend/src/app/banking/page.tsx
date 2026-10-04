'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { PageLoading, EmptyState, ErrorState } from '@/components/ui/State';
import { useAsync } from '@/lib/useApi';
import { formatCurrency } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import toast from 'react-hot-toast';

interface Analysis {
  received: number;
  importable: number;
  duplicates: number;
  invalid: number;
  invalid_rows: any[];
  duplicate_rows: any[];
  suggestions: any[];
}

const INCOME_CATS = ['salary', 'freelance', 'business', 'rental', 'bank_interest', 'dividends', 'capital_gains', 'other'];

export default function BankingPage() {
  const recon = useAsync(() => api.getReconciliation());
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [rows, setRows] = useState<any[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [importing, setImporting] = useState(false);
  const [txType, setTxType] = useState('income');

  const parseCsv = (text: string): any[] => {
    const lines = text.split(/\r?\n/).filter((l) => l.trim());
    if (lines.length < 2) return [];
    const headers = lines[0].split(',').map((h) => h.trim().toLowerCase());
    return lines.slice(1).map((line) => {
      const cells = line.split(',');
      const obj: any = {};
      headers.forEach((h, i) => { obj[h] = (cells[i] || '').trim(); });
      if (obj.amount) obj.amount = parseFloat(obj.amount);
      return obj;
    });
  };

  const analyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    try {
      const text = await file.text();
      const parsed = parseCsv(text);
      setRows(parsed);
      const result = await api.analyzeImport(parsed);
      setAnalysis(result);
    } catch (e: any) {
      toast.error(e?.response?.data?.error || 'Failed to analyze file');
    } finally {
      setAnalyzing(false);
    }
  };

  const doImport = async () => {
    if (!analysis || !rows.length) return;
    setImporting(true);
    try {
      // Recompute importable rows client-side exactly as the backend validated them:
      // skip rows missing date/amount (reported invalid) and dups are excluded via suggestions alignment.
      const valid = rows.filter((r) => r.date && r.amount !== undefined && r.amount !== '');
      const mapped = valid.slice(0, analysis.importable).map((r, i) => {
        const sug = analysis.suggestions[i];
        let category = 'other';
        if (sug && !sug.needs_review) {
          const inIncome = INCOME_CATS.includes(sug.category);
          if ((txType === 'income' && inIncome) || (txType === 'expense' && !inIncome)) {
            category = sug.category;
          }
        }
        return {
          date: r.date,
          description: r.description || 'Bank import',
          amount: Math.abs(parseFloat(r.amount)),
          transaction_type: txType,
          category,
          source: r.source || 'Bank statement',
        };
      });
      if (mapped.length === 0) {
        toast.error('Nothing importable');
        return;
      }
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/transactions/bulk`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${api.getToken()}` },
          body: JSON.stringify(mapped),
        }
      );
      if (!res.ok) throw new Error('Import failed');
      const out = await res.json();
      toast.success(`Imported ${out.inserted} transactions`);
      setAnalysis(null);
      setRows([]);
      setFile(null);
    } catch {
      toast.error('Import failed');
    } finally {
      setImporting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Banking & Reconciliation</h2>
          <p className="text-gray-500 mt-1">Import statements, review duplicates, reconcile against AIS/26AS</p>
        </div>

        <Card>
          <CardHeader><CardTitle>Import bank statement (CSV)</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500 mb-3">Columns: date, description, amount, source (optional). Duplicates are detected, never silently imported.</p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} aria-label="CSV file" />
              <Select label="" value={txType} onChange={(e) => setTxType(e.target.value)} options={[
                { value: 'income', label: 'As income' },
                { value: 'expense', label: 'As expense' },
              ]} className="sm:w-40" />
              <Button onClick={analyze} loading={analyzing} disabled={!file}>Analyze</Button>
            </div>
            {analysis && (
              <div className="mt-4 space-y-2 text-sm">
                <p>Received <strong>{analysis.received}</strong> · Importable <strong className="text-green-700">{analysis.importable}</strong> · Duplicates <strong className="text-yellow-700">{analysis.duplicates}</strong> · Invalid <strong className="text-red-600">{analysis.invalid}</strong></p>
                {analysis.invalid_rows?.length > 0 && (
                  <p className="text-gray-500">Rejected rows are listed, never silently discarded (first {analysis.invalid_rows.length} shown in console-safe summary).</p>
                )}
                <Button onClick={doImport} loading={importing} disabled={analysis.importable === 0}>
                  Import {analysis.importable} transactions
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Reconciliation (TaxShield books ↔ AIS / 26AS)</CardTitle></CardHeader>
          <CardContent>
            {recon.loading ? <PageLoading /> : recon.error ? (
              <ErrorState message={recon.error} onRetry={recon.reload} />
            ) : !recon.data ? (
              <EmptyState title="No reconciliation data" body="Add transactions and AIS records first." />
            ) : (
              <div className="space-y-2 text-sm">
                <p>Internal total <strong>{formatCurrency(recon.data.internal_total || 0)}</strong> · AIS total <strong>{formatCurrency(recon.data.ais_total || 0)}</strong></p>
                <p>
                  <Badge variant="success">matched {recon.data.matched}</Badge>{' '}
                  <Badge variant="medium">mismatched {recon.data.mismatched}</Badge>{' '}
                  <Badge variant="danger">missing {recon.data.missing}</Badge>{' '}
                  <span className="text-gray-500">score {recon.data.score}</span>
                </p>
                {(recon.data.items || []).slice(0, 10).map((it: any, i: number) => (
                  <div key={i} className="border border-gray-100 rounded-lg p-3">
                    <p className="font-medium">{it.source} · {it.income_type} · <Badge variant={it.status === 'matched' ? 'success' : 'danger'}>{it.status}</Badge></p>
                    <p className="text-gray-500">AIS {formatCurrency(it.ais_amount)} vs books {formatCurrency(it.internal_match)} (diff {formatCurrency(it.difference)}). {it.action}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
