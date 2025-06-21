import { useState, useEffect } from 'react';
import { Benchmark } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}`;

export const useDashboardData = () => {
  const [benchmarks, setbenchmarks] = useState<Benchmark[]>([]);
  const [selectedBenchmark, setselectedBenchmark] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchbenchmarks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/benchmarks`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }      const data: Benchmark[] = await response.json();
      setbenchmarks(data);
      
      // Auto-select first benchmark
      if (data.length > 0) {
        setselectedBenchmark(data[0].id);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load Benchmarks: ${errorMessage}`);
      console.error('Error fetching benchmarks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchbenchmarks();
  }, []);

  return {
    benchmarks,
    selectedBenchmark,
    setselectedBenchmark,
    loading,
    error,
    refetch: fetchbenchmarks
  };
};
