import { useState, useEffect } from 'react';
import { Metric, FilterColumn, MultiMetricResults } from '../types/dashboard';
import { ChartConfiguration } from '../types/charts';

const API_BASE = `${import.meta.env.VITE_API_URL}`;

export const useChartFirstData = (benchmark: string) => {
  const [availableMetrics, setAvailableMetrics] = useState<Metric[]>([]);
  const [availableFilters, setAvailableFilters] = useState<FilterColumn[]>([]);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [filterValues, setFilterValues] = useState<Record<string, string[]>>({});
  const [results, setResults] = useState<MultiMetricResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all available options when benchmark changes
  useEffect(() => {    if (!benchmark) {
      setAvailableMetrics([]);
      setAvailableFilters([]);
      setAvailableModels([]);
      setFilterValues({});
      setError(null);
      return;
    }

    const fetchOptions = async () => {
      try {
        setError(null);
          // Fetch all options in parallel
        const [metricsResponse, filtersResponse, modelsResponse] = await Promise.all([
          fetch(`${API_BASE}/benchmarks/${benchmark}/metrics`),
          fetch(`${API_BASE}/benchmarks/${benchmark}/filters`),
          fetch(`${API_BASE}/benchmarks/${benchmark}/models`)
        ]);

        if (!metricsResponse.ok || !filtersResponse.ok || !modelsResponse.ok) {
          throw new Error('Failed to fetch configuration options');
        }        const [metrics, filtersData, models] = await Promise.all([
          metricsResponse.json(),
          filtersResponse.json(),
          modelsResponse.json()
        ]);

        setAvailableMetrics(metrics);
        setAvailableModels(models);
        
        // Convert filters data to the expected format
        // Backend returns: { "font": ["Arial", "Times"], "size": ["12", "14"] }
        // Frontend expects: FilterColumn[] for availableFilters and Record<string, string[]> for filterValues
        const filterColumns: FilterColumn[] = Object.keys(filtersData).map(key => ({
          name: key,
          type: 'categorical' as const, // We'll assume all are categorical for now
          description: `Filter by ${key}`
        }));
        
        setAvailableFilters(filterColumns);
        setFilterValues(filtersData);} catch (err) {
        console.error('Error fetching options:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setAvailableMetrics([]);
        setAvailableFilters([]);
        setAvailableModels([]);
        setFilterValues({});
      }
    };    fetchOptions();
  }, [benchmark]);
  const createChart = async (
    config: ChartConfiguration,
    selectedModels: string[],
    selectedFilters: Record<string, string[]>
  ) => {
    if (!benchmark) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Determine which metrics we need based on chart configuration
      const requiredMetrics = getRequiredMetrics(config);
      
      if (requiredMetrics.length === 0) {
        throw new Error('No metrics specified for chart');
      }      // Determine if we need grouping
      const groupBy = config.categorical ? config.categorical : undefined;

      // Prepare the request payload matching backend contract
      const requestPayload = {
        models: selectedModels.length > 0 ? selectedModels : availableModels,
        filters: selectedFilters
      };
        
      const metricPromises = requiredMetrics.map(async (metric) => {
        let endpoint = `${API_BASE}/benchmarks/${benchmark}/metrics/${metric}`;
        
        // Add group_by as query parameter if needed
        if (groupBy) {
          endpoint += `?group_by=${groupBy}`;
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestPayload),
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch data for metric: ${metric}`);
        }

        return response.json();
      });

      const metricResults = await Promise.all(metricPromises);

      // Combine results into MultiMetricResults format
      const combinedResults: MultiMetricResults = {};
      requiredMetrics.forEach((metric, index) => {
        combinedResults[metric] = metricResults[index];
      });

      setResults(combinedResults);
    } catch (err) {
      console.error('Error creating chart:', err);
      setError(err instanceof Error ? err.message : 'Failed to create chart');
    } finally {
      setLoading(false);
    }
  };  return {
    availableMetrics,
    availableFilters,
    availableModels,
    filterValues,
    results,
    loading,
    error,
    createChart
  };
};

// Helper function to determine which metrics are needed for a chart configuration
const getRequiredMetrics = (config: ChartConfiguration): string[] => {
  const metrics: string[] = [];

  switch (config.chartType) {
    case 'bar':
      if (config.metric1) metrics.push(config.metric1);
      if (config.metric2) metrics.push(config.metric2);
      break;
    case 'scatter':
      if (config.xMetric) metrics.push(config.xMetric);
      if (config.yMetric) metrics.push(config.yMetric);
      break;
    case 'line':
      if (config.lineMetric) metrics.push(config.lineMetric);
      break;
  }

  // Remove duplicates
  return [...new Set(metrics)];
};
