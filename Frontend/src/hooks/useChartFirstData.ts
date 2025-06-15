import { useState, useEffect } from 'react';
import { Metric, FilterColumn, MultiMetricResults, MetricParameter } from '../types/dashboard';
import { ChartConfiguration } from '../types/charts';

const API_BASE = `${import.meta.env.VITE_API_URL}/data`;

export const useChartFirstData = (testType: string) => {
  const [availableMetrics, setAvailableMetrics] = useState<Metric[]>([]);
  const [availableFilters, setAvailableFilters] = useState<FilterColumn[]>([]);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [filterValues, setFilterValues] = useState<Record<string, string[]>>({});
  const [results, setResults] = useState<MultiMetricResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all available options when test type changes
  useEffect(() => {    if (!testType) {
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
          fetch(`${API_BASE}/available-metrics/${testType}`),
          fetch(`${API_BASE}/available-filters/${testType}`),
          fetch(`${API_BASE}/available-models/${testType}`)
        ]);

        if (!metricsResponse.ok || !filtersResponse.ok || !modelsResponse.ok) {
          throw new Error('Failed to fetch configuration options');
        }        const [metrics, filters, models] = await Promise.all([
          metricsResponse.json(),
          filtersResponse.json(),
          modelsResponse.json()
        ]);

        setAvailableMetrics(metrics);
        setAvailableFilters(filters);
        setAvailableModels(models);        // Fetch filter values for each filter
        if (filters.length > 0) {
          const filterValuePromises = filters.map(async (filter: any) => {
            const response = await fetch(`${API_BASE}/available-filter-values/${testType}/${filter.name}`);
            if (response.ok) {
              const values = await response.json();
              return { filterName: filter.name, values };
            }
            return { filterName: filter.name, values: [] };
          });

          const filterValuesResults = await Promise.all(filterValuePromises);
          const filterValuesMap: Record<string, string[]> = {};
          filterValuesResults.forEach(({ filterName, values }) => {
            filterValuesMap[filterName] = values;
          });
          setFilterValues(filterValuesMap);
        }      } catch (err) {
        console.error('Error fetching options:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setAvailableMetrics([]);
        setAvailableFilters([]);
        setAvailableModels([]);
        setFilterValues({});
      }
    };    fetchOptions();
  }, [testType]);

  // Helper function to fetch parameters for a specific metric
  const fetchParametersForMetric = async (testType: string, metricName: string): Promise<MetricParameter[]> => {
    try {
      const response = await fetch(`${API_BASE}/available-parameters/${testType}/${metricName}`);
      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch (err) {
      console.error(`Error fetching parameters for metric ${metricName}:`, err);
      return [];
    }
  };

  const createChart = async (
    config: ChartConfiguration,
    selectedModels: string[],
    selectedFilters: Record<string, string[]>
  ) => {
    if (!testType) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Determine which metrics we need based on chart configuration
      const requiredMetrics = getRequiredMetrics(config);
      
      if (requiredMetrics.length === 0) {
        throw new Error('No metrics specified for chart');
      }      // Determine if we need grouping
      const groupBy = config.categorical ? [config.categorical] : undefined;

      // Flatten parameter values: from {metricName: {paramName: value}} to {paramName: value}
      const flattenedParameters: Record<string, any> = {};
      if (config.parameterValues) {
        Object.values(config.parameterValues).forEach(metricParams => {
          Object.assign(flattenedParameters, metricParams);
        });
      }

      // Prepare the request payload
      const requestPayload = {
        selected_models: selectedModels.length > 0 ? selectedModels : availableModels,
        selected_filters: selectedFilters,
        parameter_values: flattenedParameters
      };      // Fetch data for each required metric
      const metricPromises = requiredMetrics.map(async (metric) => {
        let endpoint = `${API_BASE}/results/${testType}/${metric}`;
        
        // Add group_by as query parameter if needed
        if (groupBy && groupBy.length > 0) {
          endpoint += `?group_by=${groupBy.join(',')}`;
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
    createChart,
    fetchParametersForMetric
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
