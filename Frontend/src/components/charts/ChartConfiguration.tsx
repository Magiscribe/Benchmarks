import React from 'react';
import { ChartType } from '../../types/charts';
import { useChartConfiguration } from '../../hooks/useChartConfiguration';

interface ChartConfigurationProps {
  availableMetrics: string[];
  availableCategorical: string[];
  onConfigurationChange: (config: any, isValid: boolean) => void;
}

export const ChartConfiguration: React.FC<ChartConfigurationProps> = ({
  availableMetrics,
  availableCategorical,
  onConfigurationChange
}) => {
  const {
    config,
    validation,
    updateChartType,
    updateMetric1,
    updateMetric2,
    updateXMetric,
    updateYMetric,
    updateCategorical,
    updateLineMetric
  } = useChartConfiguration(availableMetrics, availableCategorical);

  React.useEffect(() => {
    onConfigurationChange(config, validation.isValid);
  }, [config, validation.isValid, onConfigurationChange]);
  const renderChartTypeSelector = () => (
    <div className="mb-4">
      <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">Chart Type</label>
      <div className="flex gap-2">
        {(['bar', 'scatter', 'line'] as ChartType[]).map((type) => (
          <button
            key={type}
            onClick={() => updateChartType(type)}
            className={`px-4 py-2 rounded capitalize transition-colors ${
              config.chartType === type
                ? 'bg-blue-500 text-white hover:bg-blue-600'
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
        </label>
        <select
          value={config.metric1 || ''}
          onChange={(e) => updateMetric1(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics.map((metric) => (
            <option key={metric} value={metric}>
              {metric}
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
          onChange={(e) => updateMetric2(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">None</option>
          {availableMetrics
            .filter(metric => metric !== config.metric1)
            .map((metric) => (
              <option key={metric} value={metric}>
                {metric}
              </option>
            ))}
        </select>
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
          onChange={(e) => updateXMetric(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics.map((metric) => (
            <option key={metric} value={metric}>
              {metric}
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
          onChange={(e) => updateYMetric(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics
            .filter(metric => metric !== config.xMetric)
            .map((metric) => (
              <option key={metric} value={metric}>
                {metric}
              </option>
            ))}
        </select>
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
          onChange={(e) => updateCategorical(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select categorical field...</option>
          {availableCategorical.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Metric <span className="text-red-500">*</span>
        </label>
        <select
          value={config.lineMetric || ''}
          onChange={(e) => updateLineMetric(e.target.value)}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
        >
          <option value="">Select metric...</option>
          {availableMetrics.map((metric) => (
            <option key={metric} value={metric}>
              {metric}
            </option>
          ))}
        </select>
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
    <div className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Chart Configuration</h3>
      
      {renderChartTypeSelector()}
      {renderConfigurationFields()}
      
      {validation.errors.length > 0 && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
          <h4 className="text-sm font-medium text-red-800 dark:text-red-300 mb-1">Configuration Errors:</h4>
          <ul className="text-sm text-red-700 dark:text-red-400 list-disc list-inside">
            {validation.errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
