import React from 'react';
import { ChartConfiguration, ChartType } from '../../types/charts';
import { Metric, FilterColumn } from '../../types/dashboard';

interface ChartConfigurationFirstProps {
  availableMetrics: Metric[];
  availableCategories: FilterColumn[];
  config: ChartConfiguration;
  onConfigChange: (config: ChartConfiguration) => void;
}

export const ChartConfigurationFirst: React.FC<ChartConfigurationFirstProps> = ({
  availableMetrics,
  availableCategories,
  config,
  onConfigChange
}) => {  // Auto-select first metric for bar chart when metrics become available
  React.useEffect(() => {
    if (config.chartType === 'bar' && !config.metric1 && availableMetrics.length > 0) {
      onConfigChange({ ...config, metric1: availableMetrics[0].name });
    }
  }, [availableMetrics, config.chartType, config.metric1, config, onConfigChange]);

  const updateChartType = (chartType: ChartType) => {
    const newConfig: ChartConfiguration = { chartType };
    
    // Auto-select first available options based on chart type
    switch (chartType) {
      case 'bar':
        if (availableMetrics.length > 0) {
          newConfig.metric1 = availableMetrics[0].name;
        }
        break;
      case 'scatter':
        if (availableMetrics.length >= 2) {
          newConfig.xMetric = availableMetrics[0].name;
          newConfig.yMetric = availableMetrics[1].name;
        } else if (availableMetrics.length === 1) {
          newConfig.xMetric = availableMetrics[0].name;
        }
        break;
      case 'line':
        if (availableCategories.length > 0) {
          newConfig.categorical = availableCategories[0].name;
        }
        if (availableMetrics.length > 0) {
          newConfig.lineMetric = availableMetrics[0].name;
        }
        break;
    }
    
    onConfigChange(newConfig);
  };

  const updateConfig = (updates: Partial<ChartConfiguration>) => {
    onConfigChange({ ...config, ...updates });
  };

  const renderChartTypeSelector = () => (
    <div className="mb-6">
      <label className="block text-sm font-medium mb-3 text-gray-900 dark:text-gray-100">
        Chart Type <span className="text-red-500">*</span>
      </label>
      <div className="flex gap-3">
        {(['bar', 'scatter', 'line'] as ChartType[]).map((type) => (
          <button
            key={type}
            onClick={() => updateChartType(type)}
            className={`px-6 py-3 rounded-lg capitalize transition-colors font-medium ${
              config.chartType === type
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {type}
          </button>
        ))}
      </div>
    </div>
  );

  const renderBarChartConfiguration = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Primary Metric <span className="text-red-500">*</span>
        </label>        <select
          value={config.metric1 || ''}
          onChange={(e) => updateConfig({ metric1: e.target.value })}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          {availableMetrics.map((metric) => (
            <option key={metric.name} value={metric.name}>
              {metric.displayName}
            </option>
          ))}
        </select>
        {config.metric1 && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {availableMetrics.find(m => m.name === config.metric1)?.description}
          </p>
        )}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Secondary Metric (Optional)
        </label>
        <select
          value={config.metric2 || ''}
          onChange={(e) => updateConfig({ metric2: e.target.value || undefined })}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">None</option>
          {availableMetrics
            .filter(metric => metric.name !== config.metric1)
            .map((metric) => (
              <option key={metric.name} value={metric.name}>
                {metric.displayName}
              </option>
            ))}
        </select>
        {config.metric2 && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {availableMetrics.find(m => m.name === config.metric2)?.description}
          </p>
        )}
      </div>
    </div>
  );

  const renderScatterChartConfiguration = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          X-Axis Metric <span className="text-red-500">*</span>
        </label>
        <select
          value={config.xMetric || ''}
          onChange={(e) => updateConfig({ xMetric: e.target.value })}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics.map((metric) => (
            <option key={metric.name} value={metric.name}>
              {metric.displayName}
            </option>
          ))}
        </select>
        {config.xMetric && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {availableMetrics.find(m => m.name === config.xMetric)?.description}
          </p>
        )}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Y-Axis Metric <span className="text-red-500">*</span>
        </label>
        <select
          value={config.yMetric || ''}
          onChange={(e) => updateConfig({ yMetric: e.target.value })}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics
            .filter(metric => metric.name !== config.xMetric)
            .map((metric) => (
              <option key={metric.name} value={metric.name}>
                {metric.displayName}
              </option>
            ))}
        </select>
        {config.yMetric && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {availableMetrics.find(m => m.name === config.yMetric)?.description}
          </p>
        )}
      </div>
    </div>
  );

  const renderLineChartConfiguration = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Categorical Field <span className="text-red-500">*</span>
        </label>
        <select
          value={config.categorical || ''}
          onChange={(e) => updateConfig({ categorical: e.target.value })}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select categorical field...</option>
          {availableCategories.map((cat) => (
            <option key={cat.name} value={cat.name}>
              {cat.name}
            </option>
          ))}
        </select>
        {config.categorical && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {availableCategories.find(c => c.name === config.categorical)?.description}
          </p>
        )}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Metric <span className="text-red-500">*</span>
        </label>
        <select
          value={config.lineMetric || ''}
          onChange={(e) => updateConfig({ lineMetric: e.target.value })}
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics.map((metric) => (
            <option key={metric.name} value={metric.name}>
              {metric.displayName}
            </option>
          ))}
        </select>
        {config.lineMetric && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {availableMetrics.find(m => m.name === config.lineMetric)?.description}
          </p>
        )}
      </div>
    </div>
  );

  const renderConfigurationFields = () => {
    switch (config.chartType) {
      case 'bar':
        return renderBarChartConfiguration();
      case 'scatter':
        return renderScatterChartConfiguration();
      case 'line':
        return renderLineChartConfiguration();
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {renderChartTypeSelector()}
      {renderConfigurationFields()}
    </div>
  );
};
