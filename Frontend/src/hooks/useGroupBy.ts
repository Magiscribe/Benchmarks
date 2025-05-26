import { useState, useEffect } from 'react';
import { FilterColumn } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

export const useGroupBy = (testType: string) => {
  const [availableGroupBy, setAvailableGroupBy] = useState<FilterColumn[]>([]);
  const [selectedGroupBy, setSelectedGroupBy] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch available group by columns (using the same filters endpoint)
  const fetchAvailableGroupBy = async () => {
    if (!testType) {
      setAvailableGroupBy([]);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/available-filters/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: FilterColumn[] = await response.json();
      setAvailableGroupBy(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load group by options: ${errorMessage}`);
      console.error('Error fetching group by options:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAvailableGroupBy();
    // Reset selected group by when test type changes
    setSelectedGroupBy([]);
  }, [testType]);

  const handleGroupBySelect = (columnName: string) => {
    setSelectedGroupBy(prev => {
      if (prev.includes(columnName)) {
        return prev.filter(col => col !== columnName);
      } else {
        return [...prev, columnName];
      }
    });
  };

  const selectAllGroupBy = () => {
    setSelectedGroupBy(availableGroupBy.map(col => col.name));
  };

  const selectNoGroupBy = () => {
    setSelectedGroupBy([]);
  };

  return {
    availableGroupBy,
    selectedGroupBy,
    loading,
    error,
    handleGroupBySelect,
    selectAllGroupBy,
    selectNoGroupBy,
    setSelectedGroupBy
  };
}; 