'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

/** Run an async loader once (or on demand) with loading/error states. No refetch storms. */
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const seq = useRef(0);

  const reload = useCallback(async () => {
    const id = ++seq.current;
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      if (seq.current === id) setData(result);
    } catch (e: any) {
      if (seq.current === id) setError(e?.response?.data?.error || e?.message || 'Failed to load');
    } finally {
      if (seq.current === id) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    reload();
    const seqRef = seq; // capture the ref object, not its possibly-stale .current
    return () => { seqRef.current++; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reload]);

  return { data, loading, error, reload, setData };
}

export function useDebouncedValue<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

/** Server-side pagination driver: page state + fetch(skip, limit). */
export function usePager(pageSize = 20) {
  const [page, setPage] = useState(0);
  const skip = page * pageSize;
  const reset = useCallback(() => setPage(0), []);
  return { page, setPage, skip, limit: pageSize, reset };
}
