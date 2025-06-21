import React, { useState, useMemo } from 'react';
import { Benchmark } from '../../types/dashboard';
import { ChartConfiguration } from '../../types/charts';
import { ChartTypeSelector } from './ChartTypeSelector';
import { DynamicChart } from './DynamicChart';
import { useChartFirstData } from '../../hooks/useChartFirstData';

interface ChartBuilderProps {
  benchmarks: Benchmark[];
  selectedBenchmark?: string;
  onBenchmarkChange?: (benchmarkId: string) => void;
}

export const ChartBuilder: React.FC<ChartBuilderProps> = ({
  benchmarks, 
  selectedBenchmark: propSelectedBenchmark, 
  onBenchmarkChange 
}) => {  const [selectedBenchmark, setSelectedBenchmark] = useState<string>(propSelectedBenchmark || '');
  const [chartConfig, setChartConfig] = useState<ChartConfiguration>({ chartType: 'bar' });
  const [advancedFilters, setAdvancedFilters] = useState<{
    selectedModels: string[];
    selectedFilters: Record<string, string[]>;
  }>({ selectedModels: [], selectedFilters: {} });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  // Update local state when prop changes or auto-select first benchmark
  React.useEffect(() => {
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
  };const {
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

  // Auto-configure chart and generate when data becomes available
  React.useEffect(() => {
    if (selectedBenchmark && availableMetrics.length > 0 && availableModels.length > 0) {
      // Auto-configure chart with first available options
      const firstMetric = availableMetrics[0];
      const secondMetric = availableMetrics.length > 1 ? availableMetrics[1] : null;
      const firstCategory = availableFilters.length > 0 ? availableFilters[0] : null;

      let newConfig: ChartConfiguration = { chartType: 'bar' };
        // Configure based on chart type
      if (chartConfig.chartType === 'bar') {
        newConfig = {
          chartType: 'bar',
          metric1: firstMetric.id
          // Don't auto-select secondary metric - leave as placeholder
        };
      } else if (chartConfig.chartType === 'scatter' && availableMetrics.length >= 2) {
        newConfig = {
          chartType: 'scatter',
          xMetric: firstMetric.id,
          yMetric: secondMetric?.id || firstMetric.id
        };
      } else if (chartConfig.chartType === 'line' && firstCategory) {
        newConfig = {
          chartType: 'line',
          categorical: firstCategory.name,
          lineMetric: firstMetric.id
        };
      }

      // Only update if configuration has changed
      const configChanged = JSON.stringify(newConfig) !== JSON.stringify(chartConfig);
      if (configChanged) {
        setChartConfig(newConfig);
        
        // Auto-generate chart after a short delay to ensure state is updated
        setTimeout(() => {
          const modelsToUse = advancedFilters.selectedModels.length > 0 
            ? advancedFilters.selectedModels 
            : availableModels;
          const filtersToUse = Object.keys(advancedFilters.selectedFilters).length > 0
            ? advancedFilters.selectedFilters
            : {};
          
          createChart(newConfig, modelsToUse, filtersToUse);
        }, 100);
      }
    }
  }, [selectedBenchmark, availableMetrics, availableModels, availableFilters, chartConfig.chartType]);

  // Reset filters when benchmark changes
  React.useEffect(() => {
    setAdvancedFilters({
      selectedModels: [],
      selectedFilters: {}
    });
  }, [selectedBenchmark]);
  const canCreateChart = useMemo(() => {
    if (!selectedBenchmark || availableMetrics.length === 0) return false;
    
    switch (chartConfig.chartType) {
      case 'bar':
        return !!chartConfig.metric1;
      case 'scatter':
        return !!chartConfig.xMetric && !!chartConfig.yMetric;
      case 'line':
        return !!chartConfig.categorical && !!chartConfig.lineMetric;
      default:
        return false;
    }
  }, [selectedBenchmark, chartConfig, availableMetrics]);
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
  };  return (
    <div className="space-y-6">
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Configuration */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <div className="space-y-6">
              {/* Benchmark Selection */}
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
                  Benchmark <span className="text-red-500">*</span>
                </label>                <select
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
                    {benchmarks.find(t => t.id === selectedBenchmark)?.description}
                  </p>
                )}
              </div>              {/* Chart Configuration */}
              {selectedBenchmark && (
                <ChartTypeSelector
                  availableMetrics={availableMetrics}
                  availableCategories={availableFilters}
                  config={chartConfig}
                  onConfigChange={setChartConfig}
                  selectedBenchmark={selectedBenchmark}
                />
              )}

              {/* Error Display */}
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-red-800 dark:text-red-300">Error</h4>
                  <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Chart Display */}
        <div className="lg:col-span-2">
          {/* Header with Create Chart Button */}
          <div className="flex justify-end mb-4">
            {selectedBenchmark && (
              <button
                onClick={handleCreateChart}
                disabled={!canCreateChart || loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Creating Chart...' : 'Create Chart'}
              </button>
            )}
          </div>

          {/* Chart Display */}
          {results && Object.keys(results).length > 0 && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <DynamicChart results={results} config={chartConfig} />
            </div>
          )}

          {/* No Chart Message */}
          {!results && !loading && !error && selectedBenchmark && (
            <div className="bg-gray-50 dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                Chart Ready
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Configure your chart settings and click "Create Chart" to begin.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Options Row */}
      {selectedBenchmark && (
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
                    onClick={() => setExpandedSections(prev => ({ ...prev, models: !prev.models }))
                    }
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
