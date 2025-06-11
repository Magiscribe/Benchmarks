import React from 'react';
import { ChartConfiguration, ChartType } from '../../types/charts';
import { Metric, FilterColumn, MetricParameter } from '../../types/dashboard';

interface ChartConfigurationFirstProps {
  availableMetrics: Metric[];
  availableCategories: FilterColumn[];
  config: ChartConfiguration;
  onConfigChange: (config: ChartConfiguration) => void;
  onFetchParameters?: (testType: string, metricName: string) => Promise<MetricParameter[]>;
  selectedTestType?: string;
}

export const ChartConfigurationFirst: React.FC<ChartConfigurationFirstProps> = ({
  availableMetrics,
  availableCategories,
  config,
  onConfigChange,
  onFetchParameters,
  selectedTestType
}) => {
  const [parametersState, setParametersState] = React.useState<Record<string, MetricParameter[]>>({});
  const [editingInputs, setEditingInputs] = React.useState<Record<string, string>>({});  // Fetch parameters for a metric when needed
  const fetchParametersForMetric = async (metricName: string) => {
    if (!onFetchParameters || !selectedTestType || parametersState[metricName]) {
      return;
    }
    
    try {
      const parameters = await onFetchParameters(selectedTestType, metricName);
      setParametersState(prev => ({ ...prev, [metricName]: parameters }));
      
      // Initialize parameter values with defaults
      if (parameters.length > 0) {
        const currentValues = config.parameterValues || {};
        const metricDefaults: Record<string, any> = {};
        parameters.forEach(param => {
          metricDefaults[param.name] = param.default;
        });
        
        onConfigChange({
          ...config,
          parameterValues: {
            ...currentValues,
            [metricName]: { ...metricDefaults, ...currentValues[metricName] }
          }
        });
      }
    } catch (error) {
      console.error(`Error fetching parameters for ${metricName}:`, error);
    }
  };

  // Handle parameter value changes
  const handleParameterChange = (metricName: string, paramName: string, value: any) => {
    const currentValues = config.parameterValues || {};
    onConfigChange({
      ...config,
      parameterValues: {
        ...currentValues,
        [metricName]: {
          ...currentValues[metricName],
          [paramName]: value
        }
      }
    });
  };

  // Component to render parameter inputs for a given metric
  const renderParameterInputs = (metricName: string | undefined) => {
    if (!metricName) return null;
    
    const parameters = parametersState[metricName] || [];
    if (parameters.length === 0) return null;

    return (
      <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
        <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
          Parameters for {availableMetrics.find(m => m.name === metricName)?.displayName}:
        </div>
        {parameters.map((param) => (
          <div key={param.name} className="space-y-1">
            <label className="block text-xs text-gray-600 dark:text-gray-400">
              {param.description}
            </label>
            <input
              type={param.type === 'number' ? 'number' : 'text'}
              value={
                param.type === 'number' 
                  ? editingInputs[`${metricName}-${param.name}`] ?? 
                    (config.parameterValues?.[metricName]?.[param.name]?.toString() ?? param.default.toString())
                  : config.parameterValues?.[metricName]?.[param.name] ?? param.default
              }
              onChange={(e) => {
                const inputValue = e.target.value;
                if (param.type === 'number') {
                  const inputKey = `${metricName}-${param.name}`;
                  setEditingInputs(prev => ({ 
                    ...prev, 
                    [inputKey]: inputValue 
                  }));
                  
                  if (inputValue === '' || inputValue === '.' || /^-?\d*\.?\d*$/.test(inputValue)) {
                    handleParameterChange(metricName, param.name, inputValue);
                  }
                } else {
                  handleParameterChange(metricName, param.name, inputValue);
                }
              }}
              onBlur={(e) => {
                if (param.type === 'number') {
                  const inputValue = e.target.value;
                  const inputKey = `${metricName}-${param.name}`;
                  
                  setEditingInputs(prev => {
                    const { [inputKey]: _, ...rest } = prev;
                    return rest;
                  });
                  
                  if (inputValue === '' || inputValue === '.') {
                    handleParameterChange(metricName, param.name, param.default);
                  } else {
                    const numValue = parseFloat(inputValue);
                    const finalValue = isNaN(numValue) ? param.default : numValue;
                    handleParameterChange(metricName, param.name, finalValue);
                  }
                }
              }}
              onFocus={() => {
                if (param.type === 'number') {
                  const inputKey = `${metricName}-${param.name}`;
                  const currentValue = config.parameterValues?.[metricName]?.[param.name];
                  setEditingInputs(prev => ({ 
                    ...prev, 
                    [inputKey]: currentValue?.toString() ?? param.default.toString()
                  }));
                }
              }}
              className="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
              placeholder={`Default: ${param.default}`}
              step="any"
            />
          </div>
        ))}
      </div>
    );
  };

  // Auto-select first metric for bar chart when metrics become available
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
          onChange={(e) => {
            updateConfig({ metric1: e.target.value });
            if (e.target.value) {
              fetchParametersForMetric(e.target.value);
            }
          }}
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
        {renderParameterInputs(config.metric1)}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Secondary Metric (Optional)
        </label>        <select
          value={config.metric2 || ''}
          onChange={(e) => {
            const value = e.target.value || undefined;
            updateConfig({ metric2: value });
            if (value) {
              fetchParametersForMetric(value);
            }
          }}
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
        {renderParameterInputs(config.metric2)}
      </div>
    </div>
  );

  const renderScatterChartConfiguration = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          X-Axis Metric <span className="text-red-500">*</span>
        </label>        <select
          value={config.xMetric || ''}
          onChange={(e) => {
            updateConfig({ xMetric: e.target.value });
            if (e.target.value) {
              fetchParametersForMetric(e.target.value);
            }
          }}
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
        {renderParameterInputs(config.xMetric)}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
          Y-Axis Metric <span className="text-red-500">*</span>
        </label>        <select
          value={config.yMetric || ''}
          onChange={(e) => {
            updateConfig({ yMetric: e.target.value });
            if (e.target.value) {
              fetchParametersForMetric(e.target.value);
            }
          }}
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
        {renderParameterInputs(config.yMetric)}
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
        </label>        <select
          value={config.lineMetric || ''}
          onChange={(e) => {
            updateConfig({ lineMetric: e.target.value });
            if (e.target.value) {
              fetchParametersForMetric(e.target.value);
            }
          }}
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
        {renderParameterInputs(config.lineMetric)}
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
