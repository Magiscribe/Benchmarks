import React, { useState } from 'react';
import { MultiMetricResults } from '../../types/dashboard';
import { ChartConfiguration as ChartConfigType } from '../../types/charts';
import { ChartConfiguration } from './ChartConfiguration';
import { DynamicChart } from './DynamicChart';

interface ChartSectionProps {
  results: MultiMetricResults;
}

export const ChartSection: React.FC<ChartSectionProps> = ({ results }) => {
  const [chartConfig, setChartConfig] = useState<{
    config: ChartConfigType;
    validation: { isValid: boolean; errors: string[] };
  } | null>(null);
  // Extract available models and metrics from results
  const availableModels = React.useMemo(() => {
    if (!results || Object.keys(results).length === 0) return [];
    const models = new Set<string>();
    Object.values(results).forEach(metricResult => {
      metricResult.results.forEach(result => {
        models.add(result.model);
      });
    });
    return Array.from(models).sort();
  }, [results]);
  const availableMetrics = React.useMemo(() => {
    if (!results || Object.keys(results).length === 0) return [];
    return Object.keys(results).sort();
  }, [results]);

  // Extract available categorical fields from group_values
  const availableCategorical = React.useMemo(() => {
    if (!results || Object.keys(results).length === 0) return [];
    const categoricalFields = new Set<string>();
    Object.values(results).forEach(metricResult => {
      metricResult.results.forEach(result => {
        Object.keys(result.group_values).forEach(key => {
          categoricalFields.add(key);
        });
      });
    });
    return Array.from(categoricalFields).sort();
  }, [results]);
  const handleConfigurationChange = (config: ChartConfigType, isValid: boolean) => {
    setChartConfig({
      config,
      validation: { isValid, errors: [] }
    });
  };if (!results || Object.keys(results).length === 0) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8 text-center">
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">Chart Visualization</h3>
        <p className="text-gray-500 dark:text-gray-400">No benchmark results available. Run some benchmarks to see charts here.</p>
      </div>
    );
  }

  if (availableModels.length === 0 || availableMetrics.length === 0) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-8 text-center border border-yellow-200 dark:border-yellow-800">
        <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-2">Chart Visualization</h3>
        <p className="text-yellow-700 dark:text-yellow-300">
          Insufficient data for charting. Need at least one model with metrics.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Chart Visualization</h2>        <div className="text-sm text-gray-500 dark:text-gray-400">
          {availableModels.length} models • {availableMetrics.length} metrics • {availableCategorical.length} categories
        </div>
      </div>      <ChartConfiguration
        availableMetrics={availableMetrics}
        availableCategorical={availableCategorical}
        onConfigurationChange={handleConfigurationChange}
      />

      {chartConfig?.validation.isValid && chartConfig.config ? (
        <DynamicChart
          results={results}
          config={chartConfig.config}
        />      ) : (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8 text-center border-2 border-dashed border-gray-300 dark:border-gray-600">
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Configure Your Chart</h3>
          <p className="text-gray-500 dark:text-gray-400">
            Select your axes and chart type above to visualize your benchmark data.
          </p>
          {chartConfig && !chartConfig.validation.isValid && (
            <div className="mt-4 text-sm text-red-600 dark:text-red-400">
              Please fix the configuration issues above to display the chart.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
