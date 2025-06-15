import { useState, useEffect } from 'react';
import { TestType } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}/data`;

export const useDashboardData = () => {
  const [testTypes, setTestTypes] = useState<TestType[]>([]);
  const [selectedTestType, setSelectedTestType] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTestTypes = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/available-tests`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: TestType[] = await response.json();
      setTestTypes(data);
      
      // Auto-select first available test type
      const firstAvailable = data.find(t => t.available);
      if (firstAvailable) {
        setSelectedTestType(firstAvailable.name);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load test types: ${errorMessage}`);
      console.error('Error fetching test types:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTestTypes();
  }, []);

  return {
    testTypes,
    selectedTestType,
    setSelectedTestType,
    loading,
    error,
    refetch: fetchTestTypes
  };
};
