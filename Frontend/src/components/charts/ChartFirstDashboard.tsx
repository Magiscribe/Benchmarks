import React, { useState, useMemo } from 'react';
import { Benchmark } from '../../types/dashboard';
import { ChartConfiguration } from '../../types/charts';
import { ChartConfigurationFirst } from './ChartConfigurationFirst';
import { DynamicChart } from './DynamicChart';
import { useChartFirstData } from '../../hooks/useChartFirstData';

interface ChartFirstDashboardProps {
  benchmarks: Benchmark[];
}

export const ChartFirstDashboard: React.FC<ChartFirstDashboardProps> = ({ benchmarks }) => {  const [selectedBenchmark, setselectedBenchmark] = useState<string>('');
  const [chartConfig, setChartConfig] = useState<ChartConfiguration>({ chartType: 'bar' });
  const [advancedFilters, setAdvancedFilters] = useState<{
    selectedModels: string[];
    selectedFilters: Record<string, string[]>;
  }>({ selectedModels: [], selectedFilters: {} });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});  const {
    availableMetrics,
    availableFilters,
    availableModels,
    filterValues,
    results,
    loading,
    error,
    createChart
  } = useChartFirstData(selectedBenchmark);// Auto-select all models when they become available
  React.useEffect(() => {
    if (availableModels.length > 0 && advancedFilters.selectedModels.length === 0) {
      setAdvancedFilters(prev => ({
        ...prev,
        selectedModels: [...availableModels]
      }));
    }
  }, [availableModels]);

  // Auto-select all filter values when they become available
  React.useEffect(() => {
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
    }
  }, [filterValues]);

  // Reset filters when test type changes
  React.useEffect(() => {
    setAdvancedFilters({
      selectedModels: [],
      selectedFilters: {}
    });
  }, [selectedBenchmark]);

  const canCreateChart = useMemo(() => {
    if (!selectedBenchmark) return false;
    
    switch (chartConfig.chartType) {
      case 'bar':
        return !!chartConfig.metric1;
      case 'scatter':
        return !!chartConfig.xMetric && !!chartConfig.yMetric && chartConfig.xMetric !== chartConfig.yMetric;
      case 'line':
        return !!chartConfig.categorical && !!chartConfig.lineMetric;
      default:
        return false;
    }
  }, [selectedBenchmark, chartConfig]);
  const handleCreateChart = async () => {
    if (!canCreateChart) return;

    // Use selected models (default to all if none selected)
    const modelsToUse = advancedFilters.selectedModels.length > 0 
      ? advancedFilters.selectedModels 
      : availableModels;

    // Use selected filter values (default to empty if none selected)
    const filtersToUse = Object.keys(advancedFilters.selectedFilters).length > 0
      ? advancedFilters.selectedFilters
      : {};

    await createChart(chartConfig, modelsToUse, filtersToUse);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Chart Builder
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Configure your visualization and we'll fetch the data
        </p>
      </div>

      {/* Chart Configuration Panel */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <div className="space-y-6">
          {/* Test Type Selection */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Test Type <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedBenchmark}
              onChange={(e) => setselectedBenchmark(e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
            >
              <option value="">Select a test type...</option>              {benchmarks.map(benchmark => (
                <option key={benchmark.id} value={benchmark.id}>
                  {benchmark.name}
                </option>
              ))}
            </select>
            {selectedBenchmark && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {benchmarks.find(t => t.id === selectedBenchmark)?.description}
              </p>
            )}
          </div>          {/* Chart Configuration */}
          {selectedBenchmark && (            <ChartConfigurationFirst
              availableMetrics={availableMetrics}
              availableCategories={availableFilters}
              config={chartConfig}
              onConfigChange={setChartConfig}
              selectedBenchmark={selectedBenchmark}
            />
          )}

          {/* Advanced Filters Toggle */}
          {selectedBenchmark && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
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
              </button>              {showAdvanced && (
                <div className="mt-4 space-y-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">                  {/* Model Selection */}
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
                      <>
                        <div className="border border-gray-200 dark:border-gray-600 rounded p-3 bg-white dark:bg-gray-800">
                          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-1 max-h-32 overflow-y-auto">
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
                  </div>                  {/* Filter Selection */}
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
                            
                            {values.length > 0 ? (
                              <div className="border border-gray-200 dark:border-gray-600 rounded p-3 bg-white dark:bg-gray-800">
                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-x-4 gap-y-1 max-h-32 overflow-y-auto">
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

          {/* Create Chart Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={handleCreateChart}
              disabled={!canCreateChart || loading}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium text-lg"
            >
              {loading ? 'Creating Chart...' : 'Create Chart'}
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-300">Error</h3>
          <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
        </div>
      )}

      {/* Chart Display */}
      {results && Object.keys(results).length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Your Chart
          </h2>
          <DynamicChart results={results} config={chartConfig} />
        </div>
      )}

      {/* No Chart Message */}
      {!results && !loading && !error && (
        <div className="bg-gray-50 dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ready to Create Your Chart
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Configure your chart above and click "Create Chart" to visualize your data.
          </p>
        </div>
      )}
    </div>
  );
};
