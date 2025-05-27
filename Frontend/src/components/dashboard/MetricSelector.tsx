import { useState } from 'react';
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
  // Track temporary input states during editing (only for number inputs)
  const [editingInputs, setEditingInputs] = useState<Record<string, string>>({});
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
        </div>      </div>
        <div className="space-y-2">
        {availableMetrics.map((metric) => (
          <div key={metric.name} className="space-y-2">
            <label className="flex items-start space-x-3">
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
            
            {/* Parameter inputs - show when metric is selected and has parameters */}
            {selectedMetrics.includes(metric.name) && 
             availableParameters[metric.name] && 
             availableParameters[metric.name].length > 0 && (
              <div className="ml-7 space-y-2 bg-gray-50 dark:bg-gray-700 p-3 rounded-md">
                <div className="text-xs font-medium text-gray-600 dark:text-gray-400">
                  Parameters for {metric.displayName}:
                </div>
                {availableParameters[metric.name].map((param) => (
                  <div key={param.name} className="space-y-1">
                    <label className="block text-xs text-gray-600 dark:text-gray-400">
                      {param.description}
                    </label>                    <input
                      type={param.type === 'number' ? 'number' : 'text'}
                      value={
                        param.type === 'number' 
                          ? editingInputs[`${metric.name}-${param.name}`] ?? 
                            (parameterValues[metric.name]?.[param.name]?.toString() ?? param.default.toString())
                          : parameterValues[metric.name]?.[param.name] ?? param.default
                      }
                      onChange={(e) => {
                        const inputValue = e.target.value;
                        if (param.type === 'number') {
                          // For number inputs, track the raw string in temporary state
                          const inputKey = `${metric.name}-${param.name}`;
                          setEditingInputs(prev => ({ 
                            ...prev, 
                            [inputKey]: inputValue 
                          }));
                          
                          // Allow empty string or valid number strings (including partial decimals like "0." or ".5")
                          if (inputValue === '' || inputValue === '.' || /^-?\d*\.?\d*$/.test(inputValue)) {
                            // For valid inputs (including empty), update parameter state immediately
                            onParameterChange(metric.name, param.name, inputValue);
                          }
                        } else {
                          onParameterChange(metric.name, param.name, inputValue);
                        }
                      }}
                      onBlur={(e) => {
                        if (param.type === 'number') {
                          const inputValue = e.target.value;
                          const inputKey = `${metric.name}-${param.name}`;
                          
                          // Clear temporary editing state
                          setEditingInputs(prev => {
                            const { [inputKey]: _, ...rest } = prev;
                            return rest;
                          });
                          
                          // Convert to final number value
                          if (inputValue === '' || inputValue === '.') {
                            // If empty or just a dot, use default
                            onParameterChange(metric.name, param.name, param.default);
                          } else {
                            const numValue = parseFloat(inputValue);
                            const finalValue = isNaN(numValue) ? param.default : numValue;
                            onParameterChange(metric.name, param.name, finalValue);
                          }
                        }
                      }}
                      onFocus={() => {
                        if (param.type === 'number') {
                          // When focusing, set temporary state to current value
                          const inputKey = `${metric.name}-${param.name}`;
                          const currentValue = parameterValues[metric.name]?.[param.name];
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
            )}
          </div>
        ))}
      </div>
      
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Selected: {selectedMetrics.length} of {availableMetrics.length} metrics
      </p>
    </div>
  );
}
