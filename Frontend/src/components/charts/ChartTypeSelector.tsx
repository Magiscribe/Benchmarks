import React, { useEffect } from 'react';
import { ChartConfiguration, ChartType } from '../../types/charts';
import { Metric, FilterColumn } from '../../types/dashboard';

interface ChartTypeSelectorProps {
  availableMetrics: Metric[];
  availableCategories: FilterColumn[];
  config: ChartConfiguration;
  onConfigChange: (config: ChartConfiguration) => void;
  selectedBenchmark?: string;
}

export const ChartTypeSelector: React.FC<ChartTypeSelectorProps> = ({
  availableMetrics,
  availableCategories,
  config,
  onConfigChange
}) => {
  const handleChartTypeChange = (chartType: ChartType) => {
    // Reset all metric selections when changing chart type
    onConfigChange({
      chartType,
      metric1: undefined,
      metric2: undefined,
      xMetric: undefined,
      yMetric: undefined,
      categorical: undefined,
      lineMetric: undefined
    });
  };

  const handleMetricChange = (field: keyof ChartConfiguration, value: string) => {
    onConfigChange({
      ...config,
      [field]: value
    });
  };
  const handleCategoricalChange = (value: string) => {
    onConfigChange({
      ...config,
      categorical: value
    });
  };

  // Auto-select first available options when metrics/categories become available
  useEffect(() => {
    if (availableMetrics.length > 0) {
      const firstMetric = availableMetrics[0];
      const secondMetric = availableMetrics.length > 1 ? availableMetrics[1] : null;
      const firstCategory = availableCategories.length > 0 ? availableCategories[0] : null;

      // Only auto-select if current config is empty for the required fields
      let needsUpdate = false;
      const updates: Partial<ChartConfiguration> = {};      if (config.chartType === 'bar') {
        if (!config.metric1) {
          updates.metric1 = firstMetric.id;
          needsUpdate = true;
        }
        // Don't auto-select secondary metric - leave as placeholder
      } else if (config.chartType === 'scatter') {
        if (!config.xMetric) {
          updates.xMetric = firstMetric.id;
          needsUpdate = true;
        }
        if (!config.yMetric && secondMetric) {
          updates.yMetric = secondMetric.id;
          needsUpdate = true;
        } else if (!config.yMetric) {
          updates.yMetric = firstMetric.id;
          needsUpdate = true;
        }
      } else if (config.chartType === 'line') {
        if (!config.categorical && firstCategory) {
          updates.categorical = firstCategory.name;
          needsUpdate = true;
        }
        if (!config.lineMetric) {
          updates.lineMetric = firstMetric.id;
          needsUpdate = true;
        }
      }

      if (needsUpdate) {
        onConfigChange({
          ...config,
          ...updates
        });
      }
    }
  }, [availableMetrics, availableCategories, config, onConfigChange]);

  return (
    <div className="space-y-6">      {/* Chart Type Selection */}
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Chart Type <span className="text-red-500">*</span>
        </label>
        <select
          value={config.chartType}
          onChange={(e) => handleChartTypeChange(e.target.value as ChartType)}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="bar">Bar Chart</option>
          <option value="scatter">Scatter Plot</option>
          <option value="line">Line Chart</option>
        </select>
      </div>

      {/* Bar Chart Configuration */}
      {config.chartType === 'bar' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Primary Metric <span className="text-red-500">*</span>
            </label>            <select
              value={config.metric1 || (availableMetrics.length > 0 ? availableMetrics[0].id : '')}
              onChange={(e) => handleMetricChange('metric1', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              {availableMetrics.map((metric) => (
                <option key={metric.id} value={metric.id}>
                  {metric.name}
                </option>
              ))}
            </select>            {availableMetrics.length > 0 && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {config.metric1 
                  ? availableMetrics.find(m => m.id === config.metric1)?.description
                  : availableMetrics[0]?.description
                }
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Secondary Metric (Optional)
            </label>            <select
              value={config.metric2 || ''}
              onChange={(e) => handleMetricChange('metric2', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select secondary metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric.id} value={metric.id}>
                  {metric.name}
                </option>
              ))}
            </select>
            {config.metric2 && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {availableMetrics.find(m => m.id === config.metric2)?.description}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Scatter Chart Configuration */}
      {config.chartType === 'scatter' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              X-Axis Metric <span className="text-red-500">*</span>
            </label>            <select
              value={config.xMetric || (availableMetrics.length > 0 ? availableMetrics[0].id : '')}
              onChange={(e) => handleMetricChange('xMetric', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              {availableMetrics.map((metric) => (
                <option key={metric.id} value={metric.id}>
                  {metric.name}
                </option>
              ))}            </select>
            {availableMetrics.length > 0 && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {config.xMetric 
                  ? availableMetrics.find(m => m.id === config.xMetric)?.description
                  : availableMetrics[0]?.description
                }
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Y-Axis Metric <span className="text-red-500">*</span>
            </label>            <select
              value={config.yMetric || (availableMetrics.length > 1 ? availableMetrics[1].id : availableMetrics.length > 0 ? availableMetrics[0].id : '')}
              onChange={(e) => handleMetricChange('yMetric', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              {availableMetrics.map((metric) => (
                <option key={metric.id} value={metric.id}>
                  {metric.name}
                </option>
              ))}            </select>
            {availableMetrics.length > 0 && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {config.yMetric 
                  ? availableMetrics.find(m => m.id === config.yMetric)?.description
                  : availableMetrics[0]?.description
                }
              </p>
            )}
          </div>
        </div>
      )}

      {/* Line Chart Configuration */}
      {config.chartType === 'line' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Category (X-Axis) <span className="text-red-500">*</span>
            </label>            <select              value={config.categorical || (availableCategories.length > 0 ? availableCategories[0].name : '')}
              onChange={(e) => handleCategoricalChange(e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              {availableCategories.map((category) => (
                <option key={category.name} value={category.name}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Metric (Y-Axis) <span className="text-red-500">*</span>
            </label>            <select
              value={config.lineMetric || (availableMetrics.length > 0 ? availableMetrics[0].id : '')}
              onChange={(e) => handleMetricChange('lineMetric', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              {availableMetrics.map((metric) => (
                <option key={metric.id} value={metric.id}>
                  {metric.name}
                </option>
              ))}            </select>
            {availableMetrics.length > 0 && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {config.lineMetric 
                  ? availableMetrics.find(m => m.id === config.lineMetric)?.description
                  : availableMetrics[0]?.description
                }
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
