import React from 'react';
import { ChartConfiguration, ChartType } from '../../types/charts';
import { Metric, FilterColumn } from '../../types/dashboard';

interface ChartConfigurationFirstProps {
  availableMetrics: Metric[];
  availableCategories: FilterColumn[];
  config: ChartConfiguration;
  onConfigChange: (config: ChartConfiguration) => void;
  selectedBenchmark?: string;
}

export const ChartConfigurationFirst: React.FC<ChartConfigurationFirstProps> = ({
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

  return (
    <div className="space-y-6">
      {/* Chart Type Selection */}
      <div>
        <label className="block text-sm font-medium mb-3 text-gray-900 dark:text-gray-100">
          Chart Type <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { value: 'bar', label: 'Bar Chart', description: 'Compare metrics across models' },
            { value: 'scatter', label: 'Scatter Plot', description: 'Metric vs metric comparison' },
            { value: 'line', label: 'Line Chart', description: 'Trends across categories' }
          ].map((chartType) => (
            <div
              key={chartType.value}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                config.chartType === chartType.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
              }`}
              onClick={() => handleChartTypeChange(chartType.value as ChartType)}
            >
              <h3 className="font-medium text-gray-900 dark:text-gray-100">{chartType.label}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{chartType.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bar Chart Configuration */}
      {config.chartType === 'bar' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Primary Metric <span className="text-red-500">*</span>
            </label>
            <select
              value={config.metric1 || ''}
              onChange={(e) => handleMetricChange('metric1', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select primary metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric.name} value={metric.name}>
                  {metric.displayName}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Secondary Metric (Optional)
            </label>
            <select
              value={config.metric2 || ''}
              onChange={(e) => handleMetricChange('metric2', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select secondary metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric.name} value={metric.name}>
                  {metric.displayName}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Scatter Chart Configuration */}
      {config.chartType === 'scatter' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              X-Axis Metric <span className="text-red-500">*</span>
            </label>
            <select
              value={config.xMetric || ''}
              onChange={(e) => handleMetricChange('xMetric', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select X-axis metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric.name} value={metric.name}>
                  {metric.displayName}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Y-Axis Metric <span className="text-red-500">*</span>
            </label>
            <select
              value={config.yMetric || ''}
              onChange={(e) => handleMetricChange('yMetric', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select Y-axis metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric.name} value={metric.name}>
                  {metric.displayName}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Line Chart Configuration */}
      {config.chartType === 'line' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Category (X-Axis) <span className="text-red-500">*</span>
            </label>
            <select
              value={config.categorical || ''}
              onChange={(e) => handleCategoricalChange(e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select category...</option>
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
            </label>
            <select
              value={config.lineMetric || ''}
              onChange={(e) => handleMetricChange('lineMetric', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric.name} value={metric.name}>
                  {metric.displayName}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  );
};
