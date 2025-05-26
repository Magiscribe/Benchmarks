import { useState } from 'react';
import { MultiMetricResults } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

export const useResults = () => {
  const [results, setResults] = useState<MultiMetricResults | null>(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const fetchResults = async (
    testType: string,
    metrics: string[],
    request: {
      models: string[];
      filters: Record<string, string[]>;
      parameters: Record<string, Record<string, any>>;
    },
    groupBy?: string[]
  ) => {
    if (!testType || metrics.length === 0) return;

    setResultsLoading(true);
    try {
      // For each metric, fetch results
      const resultsPromises = metrics.map(async (metric) => {
        const endpoint = groupBy && groupBy.length > 0
          ? `${API_BASE}/results/${testType}/${metric}/group-by/${groupBy.join(',')}`
          : `${API_BASE}/results/${testType}/${metric}`;

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            selected_models: request.models,
            selected_filters: request.filters,
            parameter_values: request.parameters[metric] || {}
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
      });

      const results = await Promise.all(resultsPromises);
      
      // Combine results into a single object
      const combinedResults: MultiMetricResults = {};
      results.forEach((result, index) => {
        const metric = metrics[index];
        combinedResults[metric] = result;
      });

      setResults(combinedResults);
    } catch (error) {
      console.error('Error fetching results:', error);
      setResults(null);
    } finally {
      setResultsLoading(false);
    }
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const clearResults = () => {
    setResults(null);
  };

  return {
    results,
    resultsLoading,
    sortField,
    sortDirection,
    fetchResults,
    handleSort,
    clearResults
  };
};
