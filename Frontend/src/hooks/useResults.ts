import { useState } from 'react';
import { MultiMetricResults, ResultsRequest } from '../types/dashboard';

const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

export const useResults = () => {
  const [results, setResults] = useState<MultiMetricResults | null>(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [sortField, setSortField] = useState<string>('model');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const fetchResults = async (
    testType: string,
    selectedMetrics: string[],
    request: ResultsRequest
  ) => {
    if (!testType || selectedMetrics.length === 0) return;

    try {
      setResultsLoading(true);
      const multiMetricResults: MultiMetricResults = {};

      // Fetch results for each selected metric
      for (const metric of selectedMetrics) {
        try {
          // Get parameters specific to this metric
          const metricParameters = request.parameters?.[metric] || {};
          
          const response = await fetch(`${API_BASE}/results/${testType}/${metric}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              selected_models: request.models,
              selected_filters: request.filters || {},
              parameter_values: metricParameters
            }),
          });

          if (response.ok) {
            const result = await response.json();
            multiMetricResults[metric] = result;
          } else {
            console.error(`Error fetching results for metric ${metric}:`, response.statusText);
          }
        } catch (err) {
          console.error(`Error fetching results for metric ${metric}:`, err);
        }
      }

      setResults(multiMetricResults);
    } catch (err) {
      console.error('Error fetching results:', err);
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
