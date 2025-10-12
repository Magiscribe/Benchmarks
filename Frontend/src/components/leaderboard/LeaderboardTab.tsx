import React, { useState, useEffect, useMemo } from 'react';
import { Benchmark } from '../../types/dashboard';
import { useChartFirstData } from '../../hooks/useChartFirstData';

interface LeaderboardTabProps {
  benchmarks: Benchmark[];
  selectedBenchmark?: string;
  onBenchmarkChange?: (benchmarkId: string) => void;
}

interface LeaderboardData {
  model: string;
  [metricId: string]: string | number;
}

type SortConfig = {
  key: string;
  direction: 'asc' | 'desc';
} | null;

export const LeaderboardTab: React.FC<LeaderboardTabProps> = ({
  benchmarks,
  selectedBenchmark: propSelectedBenchmark,
  onBenchmarkChange
}) => {  const [selectedBenchmark, setSelectedBenchmark] = useState<string>(propSelectedBenchmark || '');
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortConfig, setSortConfig] = useState<SortConfig>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [isRequestInFlight, setIsRequestInFlight] = useState(false);
  const [retryCount, setRetryCount] = useState(0);  const [advancedFilters, setAdvancedFilters] = useState<{
    selectedModels: string[];
    selectedFilters: Record<string, string[]>;
  }>({ selectedModels: [], selectedFilters: {} });
  const [visibleMetrics, setVisibleMetrics] = useState<string[]>([]);

  // Update local state when prop changes or auto-select first benchmark
  useEffect(() => {
    if (propSelectedBenchmark && propSelectedBenchmark !== selectedBenchmark) {
      setSelectedBenchmark(propSelectedBenchmark);
    } else if (!propSelectedBenchmark && benchmarks.length > 0 && !selectedBenchmark) {
      // Auto-select first benchmark if none is selected and benchmarks are available
      const firstBenchmark = benchmarks[0].id;
      setSelectedBenchmark(firstBenchmark);
      if (onBenchmarkChange) {
        onBenchmarkChange(firstBenchmark);
      }
    }
  }, [propSelectedBenchmark, benchmarks]);

  // Handle benchmark change
  const handleBenchmarkChange = (benchmarkId: string) => {
    setSelectedBenchmark(benchmarkId);
    if (onBenchmarkChange) {
      onBenchmarkChange(benchmarkId);
    }
  };

  // Get available data from the hook
  const {
    availableMetrics,
    availableFilters,
    availableModels,
    filterValues,
  } = useChartFirstData(selectedBenchmark);

  // Auto-select all models when they become available
  useEffect(() => {
    if (availableModels.length > 0 && advancedFilters.selectedModels.length === 0) {
      setAdvancedFilters(prev => ({
        ...prev,
        selectedModels: [...availableModels]
      }));
    }
  }, [availableModels]);

  // Auto-select all filter values when they become available
  useEffect(() => {
    if (Object.keys(filterValues).length > 0) {
      setAdvancedFilters(prev => {
        const newSelectedFilters = { ...prev.selectedFilters };
        let hasChanges = false;

        Object.entries(filterValues).forEach(([filterName, values]) => {
          if (!newSelectedFilters[filterName] || newSelectedFilters[filterName].length === 0) {
            newSelectedFilters[filterName] = [...values];
            hasChanges = true;
          }
        });

        return hasChanges ? { ...prev, selectedFilters: newSelectedFilters } : prev;
      });
    }  }, [filterValues]);  // Auto-select only the first metric when available metrics change (initial load case)
  useEffect(() => {
    if (availableMetrics.length > 0 && visibleMetrics.length === 0 && selectedBenchmark) {
      setVisibleMetrics([availableMetrics[0].id]);
    }
  }, [availableMetrics, visibleMetrics.length, selectedBenchmark]);// Reset filters when benchmark changes
  useEffect(() => {
    setAdvancedFilters({
      selectedModels: [],
      selectedFilters: {}
    });
    setVisibleMetrics([]);
    setLeaderboardData([]);
    setSortConfig(null);
    setIsRequestInFlight(false); // Reset request state on benchmark change
    
    // Auto-select first metric for the new benchmark if available
    if (availableMetrics.length > 0) {
      setVisibleMetrics([availableMetrics[0].id]);
    }
  }, [selectedBenchmark, availableMetrics.length]);

  // Fetch leaderboard data with batched API calls per metric
  const fetchLeaderboardData = async () => {
    if (!selectedBenchmark || availableMetrics.length === 0) return;
    
    // Prevent duplicate requests
    if (isRequestInFlight) return;

    setLoading(true);
    setError(null);
    setIsRequestInFlight(true);

    try {
      const API_BASE = `${import.meta.env.VITE_API_URL}`;
      
      // Use selected models (default to all if none selected)
      const modelsToUse = advancedFilters.selectedModels.length > 0 
        ? advancedFilters.selectedModels 
        : availableModels;

      // Use selected filter values (default to empty if none selected)
      const filtersToUse = Object.keys(advancedFilters.selectedFilters).length > 0
        ? advancedFilters.selectedFilters
        : {};      // Batch API calls - one request per visible metric for ALL models at once
      const visibleMetricsToFetch = availableMetrics.filter(metric => visibleMetrics.includes(metric.id));
      const metricPromises = visibleMetricsToFetch.map(async (metric) => {
        try {
          const response = await fetch(`${API_BASE}/benchmarks/${selectedBenchmark}/metrics/${metric.id}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              models: modelsToUse, // ALL models at once instead of one at a time
              filters: filtersToUse
            })
          });

          if (!response.ok) {
            console.error(`HTTP ${response.status} for metric ${metric.name}`);
            return { metric, error: `HTTP ${response.status}` };
          }

          const data = await response.json();
          return { metric, data };
        } catch (err) {
          console.error(`Error fetching metric ${metric.name}:`, err);
          return { metric, error: err instanceof Error ? err.message : 'Unknown error' };
        }
      });

      // Wait for all metric requests to complete in parallel
      const metricResults = await Promise.all(metricPromises);

      // Build leaderboard data structure
      const leaderboard: LeaderboardData[] = [];
      
      // Initialize each model's data
      modelsToUse.forEach(model => {
        leaderboard.push({ model });
      });

      // Process each metric's results
      metricResults.forEach(({ metric, data, error }) => {
        if (error) {
          // If metric failed, mark all models as 'Error' for this metric
          leaderboard.forEach(modelData => {
            modelData[metric.id] = 'Error';
          });
          return;
        }

        if (!data?.results || !Array.isArray(data.results)) {
          // If no results, mark all models as 'N/A' for this metric
          leaderboard.forEach(modelData => {
            modelData[metric.id] = 'N/A';
          });
          return;
        }

        // Map metric results to models
        const resultsByModel = new Map();
        data.results.forEach((result: any) => {
          if (result.model && typeof result.value !== 'undefined') {
            resultsByModel.set(result.model, result.value);
          }
        });

        // Update leaderboard with metric values
        leaderboard.forEach(modelData => {
          const value = resultsByModel.get(modelData.model);
          if (typeof value === 'number') {
            modelData[metric.id] = Number(value.toFixed(4));
          } else if (value !== undefined) {
            modelData[metric.id] = value;
          } else {
            modelData[metric.id] = 'N/A';
          }
        });
      });

      setLeaderboardData(leaderboard);
    } catch (err) {
      console.error('Error fetching leaderboard data:', err);
      setError('Failed to fetch leaderboard data. Please check your connection and try again.');
    } finally {
      setLoading(false);
      setIsRequestInFlight(false);
    }
  };
  // Manual refresh function  
  const handleRefresh = () => {
    setRetryCount(prev => prev + 1);
    setError(null);
    fetchLeaderboardData();
  };  // Fetch data when benchmark and filters change
  useEffect(() => {
    if (selectedBenchmark && availableMetrics.length > 0 && availableModels.length > 0 && visibleMetrics.length > 0) {
      fetchLeaderboardData();
    }
  }, [
    selectedBenchmark, 
    availableMetrics.length, 
    availableModels.length,
    JSON.stringify(advancedFilters), // Stringify to compare actual content
    JSON.stringify(visibleMetrics), // Include visible metrics changes
    retryCount
  ]);

  // Set initial sort by first visible metric when data loads
  useEffect(() => {
    if (leaderboardData.length > 0 && visibleMetrics.length > 0 && !sortConfig) {
      const firstMetricId = visibleMetrics[0];
      const firstMetric = availableMetrics.find(m => m.id === firstMetricId);
      
      if (firstMetric) {
        // Determine sort direction based on metric description
        const description = firstMetric.description.toLowerCase();
        let direction: 'asc' | 'desc' = 'desc'; // Default to descending
        
        if (description.includes('lower is better')) {
          direction = 'asc'; // Lower is better = ascending sort (smallest at top)
        } else if (description.includes('higher is better')) {
          direction = 'desc'; // Higher is better = descending sort (largest at top)
        }
        
        setSortConfig({
          key: firstMetricId,
          direction
        });
      }
    }
  }, [leaderboardData, visibleMetrics, sortConfig, availableMetrics]);

  // Sort the leaderboard data
  const sortedData = useMemo(() => {
    if (!sortConfig) return leaderboardData;

    return [...leaderboardData].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      // Handle string comparison (model names)
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        if (sortConfig.direction === 'asc') {
          return aValue.localeCompare(bValue);
        } else {
          return bValue.localeCompare(aValue);
        }
      }

      // Handle numeric comparison
      const aNum = typeof aValue === 'number' ? aValue : (aValue === 'N/A' || aValue === 'Error' ? -Infinity : parseFloat(String(aValue)));
      const bNum = typeof bValue === 'number' ? bValue : (bValue === 'N/A' || bValue === 'Error' ? -Infinity : parseFloat(String(bValue)));

      if (sortConfig.direction === 'asc') {
        return aNum - bNum;
      } else {
        return bNum - aNum;
      }
    });
  }, [leaderboardData, sortConfig]);

  // Handle column header click for sorting
  const handleSort = (key: string) => {
    setSortConfig(current => {
      if (current && current.key === key) {
        // Toggle direction
        return { key, direction: current.direction === 'asc' ? 'desc' : 'asc' };
      } else {
        // New column, default to descending for metrics, ascending for model names
        return { key, direction: key === 'model' ? 'asc' : 'desc' };
      }
    });
  };

  const getSortIcon = (key: string) => {
    if (!sortConfig || sortConfig.key !== key) {
      return (
        <svg className="w-4 h-4 ml-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }

    if (sortConfig.direction === 'asc') {
      return (
        <svg className="w-4 h-4 ml-1 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      );
    } else {
      return (
        <svg className="w-4 h-4 ml-1 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      );
    }
  };

  return (
    <div className="space-y-6">          {/* Benchmark Selection */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 max-w-md">
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Benchmark <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedBenchmark}
              onChange={(e) => handleBenchmarkChange(e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
            >
              {benchmarks.map(benchmark => (
                <option key={benchmark.id} value={benchmark.id}>
                  {benchmark.name}
                </option>
              ))}
            </select>
            {selectedBenchmark && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {benchmarks.find(b => b.id === selectedBenchmark)?.description}
              </p>
            )}
          </div>

          {/* Visible Metrics Selector */}
          {selectedBenchmark && availableMetrics.length > 0 && (
            <div className="flex-1 max-w-md">
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
                Visible Metrics
              </label>
              <div className="border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 p-3 max-h-32 overflow-y-auto">
                <div className="space-y-2">
                  {availableMetrics.map((metric) => (
                    <label key={metric.id} className="flex items-center text-sm">
                      <input
                        type="checkbox"
                        checked={visibleMetrics.includes(metric.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setVisibleMetrics(prev => [...prev, metric.id]);
                          } else {
                            setVisibleMetrics(prev => prev.filter(id => id !== metric.id));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2 flex-shrink-0"
                      />
                      <span className="text-gray-700 dark:text-gray-300" title={metric.description}>
                        {metric.name}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {visibleMetrics.length} of {availableMetrics.length} metrics selected
              </p>
            </div>
          )}
          
          {selectedBenchmark && (
            <div className="flex-shrink-0 pt-6">
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Leaderboard Table */}
      {selectedBenchmark && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">          {loading && (
            <div className="p-8 text-center">
              <div className="animate-spin inline-block w-6 h-6 border-2 border-current border-t-transparent text-blue-600 rounded-full" role="status" aria-label="loading">
                <span className="sr-only">Loading...</span>
              </div>
              <p className="mt-2 text-blue-700 dark:text-blue-300">
                Loading leaderboard data...
              </p>              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Fetching {visibleMetrics.length} metrics for {advancedFilters.selectedModels.length > 0 ? advancedFilters.selectedModels.length : availableModels.length} models
              </p>
            </div>
          )}          {error && (
            <div className="p-6">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-red-800 dark:text-red-300">Error</h4>
                    <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
                  </div>
                  <button
                    onClick={handleRefresh}
                    disabled={loading}
                    className="ml-3 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:bg-red-400 disabled:cursor-not-allowed"
                  >
                    Retry
                  </button>
                </div>
              </div>
            </div>
          )}

          {!loading && !error && sortedData.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full">                <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                  <tr>
                    <th
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      onClick={() => handleSort('model')}
                    >
                      <div className="flex items-center">
                        Model
                        {getSortIcon('model')}
                      </div>
                    </th>                    {availableMetrics.filter(metric => visibleMetrics.includes(metric.id)).map(metric => (
                      <th
                        key={metric.id}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors group relative"
                        onClick={() => handleSort(metric.id)}
                        title={metric.description || metric.name}
                      >
                        <div className="flex items-center">
                          {metric.name}
                          {getSortIcon(metric.id)}
                        </div>
                        {/* Tooltip */}
                        {metric.description && (
                          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white dark:text-gray-200 text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                            {metric.description}
                            <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                          </div>
                        )}
                      </th>
                    ))}
                  </tr></thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-600">                  {sortedData.map((row, index) => (
                    <tr 
                      key={row.model} 
                      className={
                        index % 2 === 0 
                          ? 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors' 
                          : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors'
                      }
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                        {row.model}
                      </td>                      {availableMetrics.filter(metric => visibleMetrics.includes(metric.id)).map(metric => (
                        <td key={metric.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                          <span className={
                            row[metric.id] === 'N/A' 
                              ? 'text-gray-400 dark:text-gray-500 italic' 
                              : row[metric.id] === 'Error' 
                                ? 'text-red-500 dark:text-red-400 font-medium'
                                : ''
                          }>
                            {row[metric.id]}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!loading && !error && sortedData.length === 0 && selectedBenchmark && (
            <div className="p-8 text-center">
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                No Data Available
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                No leaderboard data found for the selected Benchmark.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Advanced Options */}
      {selectedBenchmark && availableModels.length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
          >
            <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Options</span>
            <svg
              className={`ml-2 h-4 w-4 transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAdvanced && (
            <div className="mt-4 space-y-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
              {/* Model Selection */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <button
                    onClick={() => setExpandedSections(prev => ({ ...prev, models: !prev.models }))}
                    className="flex items-center text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    <span>Models</span>
                    <svg
                      className={`ml-2 h-4 w-4 transform transition-transform ${expandedSections.models ? 'rotate-180' : ''}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <button
                    onClick={() => {
                      const allSelected = advancedFilters.selectedModels.length === availableModels.length;
                      setAdvancedFilters(prev => ({
                        ...prev,
                        selectedModels: allSelected ? [] : [...availableModels]
                      }));
                    }}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 font-medium"
                  >
                    {advancedFilters.selectedModels.length === availableModels.length ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
                {expandedSections.models && (
                  <>                    <div className="border border-gray-200 dark:border-gray-600 rounded p-3 bg-white dark:bg-gray-800">
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-1 max-h-32 overflow-y-auto">
                        {availableModels.map((model: string) => (
                          <label key={model} className="flex items-center text-sm">
                            <input
                              type="checkbox"
                              checked={advancedFilters.selectedModels.includes(model)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setAdvancedFilters(prev => ({
                                    ...prev,
                                    selectedModels: [...prev.selectedModels, model]
                                  }));
                                } else {
                                  setAdvancedFilters(prev => ({
                                    ...prev,
                                    selectedModels: prev.selectedModels.filter(m => m !== model)
                                  }));
                                }
                              }}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2 flex-shrink-0"
                            />
                            <span className="text-gray-700 dark:text-gray-300 truncate" title={model}>
                              {model}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {advancedFilters.selectedModels.length} of {availableModels.length} models selected
                    </div>
                  </>
                )}
              </div>

              {/* Filter Selection */}
              {availableFilters.map((filter: any) => {
                const values = filterValues[filter.name] || [];
                const selectedValues = advancedFilters.selectedFilters[filter.name] || [];
                const allSelected = selectedValues.length === values.length;
                const isExpanded = expandedSections[`filter-${filter.name}`];

                return (
                  <div key={filter.name}>
                    <div className="flex items-center justify-between mb-2">
                      <button
                        onClick={() => setExpandedSections(prev => ({ ...prev, [`filter-${filter.name}`]: !prev[`filter-${filter.name}`] }))}
                        className="flex items-center text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400"
                      >
                        <span>{filter.name}</span>
                        <svg
                          className={`ml-2 h-4 w-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <button
                        onClick={() => {
                          setAdvancedFilters(prev => ({
                            ...prev,
                            selectedFilters: {
                              ...prev.selectedFilters,
                              [filter.name]: allSelected ? [] : [...values]
                            }
                          }));
                        }}
                        className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 font-medium"
                      >
                        {allSelected ? 'Deselect All' : 'Select All'}
                      </button>
                    </div>
                    {isExpanded && (
                      <>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                          {filter.description}
                        </div>
                        
                        {values.length > 0 ? (                          <div className="border border-gray-200 dark:border-gray-600 rounded p-3 bg-white dark:bg-gray-800">
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-1 max-h-32 overflow-y-auto">
                              {values.map((value: string) => (
                                <label key={value} className="flex items-center text-sm">
                                  <input
                                    type="checkbox"
                                    checked={selectedValues.includes(value)}
                                    onChange={(e) => {
                                      setAdvancedFilters(prev => {
                                        const currentValues = prev.selectedFilters[filter.name] || [];
                                        const newValues = e.target.checked
                                          ? [...currentValues, value]
                                          : currentValues.filter(v => v !== value);
                                        
                                        return {
                                          ...prev,
                                          selectedFilters: {
                                            ...prev.selectedFilters,
                                            [filter.name]: newValues
                                          }
                                        };
                                      });
                                    }}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2 flex-shrink-0"
                                  />
                                  <span className="text-gray-700 dark:text-gray-300 truncate" title={value}>
                                    {value}
                                  </span>
                                </label>
                              ))}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                              {selectedValues.length} of {values.length} values selected
                            </div>
                          </div>
                        ) : (
                          <div className="p-3 border border-gray-200 dark:border-gray-600 rounded bg-gray-100 dark:bg-gray-800">
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Loading filter values...
                            </p>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
