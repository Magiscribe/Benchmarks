import { Metric, MetricParameter } from '../../types/dashboard';

interface MetricSelectorProps {
  availableMetrics: Metric[];
  selectedMetrics: string[];
  availableParameters: Record<string, MetricParameter[]>;
  parameterValues: Record<string, Record<string, any>>;
  onMetricSelect: (metric: string) => void;
  onSelectAll: () => void;
  onSelectNone: () => void;
  onParameterChange: (metric: string, paramName: string, value: any) => void;
}

export default function MetricSelector({
  availableMetrics,
  selectedMetrics,
  availableParameters,
  parameterValues,
  onMetricSelect,
  onSelectAll,
  onSelectNone,
  onParameterChange
}: MetricSelectorProps) {
  if (availableMetrics.length === 0) {
    return (
      <div className="text-gray-500 dark:text-gray-400">
        Choose a test type first
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Metrics ({availableMetrics.length})
        </label>
        <div className="space-x-2">
          <button
            onClick={onSelectAll}
            className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Select All
          </button>
          <button
            onClick={onSelectNone}
            className="text-xs px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Select None
          </button>
        </div>
      </div>
      
      <div className="space-y-2 max-h-40 overflow-y-auto">
        {availableMetrics.map((metric) => (
          <label key={metric.name} className="flex items-start space-x-3">
            <input
              type="checkbox"
              checked={selectedMetrics.includes(metric.name)}
              onChange={() => onMetricSelect(metric.name)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
            />
            <div className="flex-1">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {metric.displayName}
              </span>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {metric.description}
              </p>
            </div>
          </label>
        ))}
      </div>
      
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Selected: {selectedMetrics.length} of {availableMetrics.length} metrics
      </p>

      {/* Selected Metrics with Parameters */}
      {selectedMetrics.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">
            Selected Metrics ({selectedMetrics.length})
          </h4>
          
          <div className="space-y-4">
            {selectedMetrics.map((metricName) => {
              const metric = availableMetrics.find(m => m.name === metricName);
              const parameters = availableParameters[metricName] || [];
              
              return (
                <div key={metricName} className="p-3 bg-white dark:bg-gray-800 rounded border">
                  <div className="mb-2">
                    <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                      {metric?.displayName || metricName}
                    </h5>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {metric?.description}
                    </p>
                  </div>
                  
                  {/* Parameter Inputs for this metric */}
                  {parameters.length > 0 && (
                    <div className="mt-3">
                      <h6 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Parameters ({parameters.length})
                      </h6>
                      <div className="space-y-2">
                        {parameters.map((param) => (
                          <div key={param.name} className="grid grid-cols-1 md:grid-cols-3 gap-2 items-center">
                            <div>
                              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                                {param.name}
                              </label>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {param.description}
                              </p>
                            </div>
                            <div>
                              <input
                                type={param.type === 'number' ? 'number' : 'text'}
                                value={parameterValues[metricName]?.[param.name] ?? param.default}
                                onChange={(e) => onParameterChange(
                                  metricName,
                                  param.name, 
                                  param.type === 'number' ? parseFloat(e.target.value) || param.default : e.target.value
                                )}
                                className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                placeholder={`Default: ${param.default}`}
                              />
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              Default: {param.default}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
