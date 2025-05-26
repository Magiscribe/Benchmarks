import { TestType, MetricParameter } from '../../types/dashboard';

interface DebugInfoProps {
  selectedTestType: string;
  testTypes: TestType[];
  availableModels: string[];
  selectedModels: string[];
  availableMetrics: any[];
  selectedMetrics: string[];
  availableParameters: Record<string, MetricParameter[]>;
  parameterValues: Record<string, Record<string, any>>;
  availableFilters: any[];
  selectedFilterValues: Record<string, string[]>;
  filterValues: Record<string, string[]>;
}

export default function DebugInfo({
  selectedTestType,
  testTypes,
  availableModels,
  selectedModels,
  availableMetrics,
  selectedMetrics,
  availableParameters,
  parameterValues,
  availableFilters,
  selectedFilterValues,
  filterValues
}: DebugInfoProps) {
  const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

  return (
    <div className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Debug Info</h3>
      
      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
        <p>API URL: {API_BASE}</p>
        <p>Selected Test Type: {selectedTestType || 'None'}</p>
        <p>Total Test Types: {testTypes.length}</p>
        <p>Available Test Types: {testTypes.filter(t => t.available).length}</p>
        <p>Available Models: {availableModels.length}</p>
        <p>Selected Models: {selectedModels.length}</p>
        <p>Available Metrics: {availableMetrics.length}</p>
        <p>Selected Metrics: {selectedMetrics.length}</p>
        <p>Available Parameters: {Object.keys(availableParameters).length}</p>
        <p>Available Filters: {availableFilters.length}</p>
        
        {Object.keys(availableParameters).length > 0 && (
          <div className="mt-2">
            <p className="font-medium">Parameter Values:</p>
            {Object.entries(availableParameters).map(([metric, params]) => (
              <div key={metric} className="ml-2">
                <p className="font-medium text-blue-600 dark:text-blue-400">{metric}:</p>
                {params.map((param) => (
                  <p key={param.name} className="ml-4">
                    {param.name}: {parameterValues[metric]?.[param.name] ?? param.default} (default: {param.default})
                  </p>
                ))}
              </div>
            ))}
          </div>
        )}
        
        {availableFilters.length > 0 && (
          <div className="mt-2">
            <p className="font-medium">Filter Selections:</p>
            {availableFilters.map((filter) => (
              <p key={filter.name} className="ml-2">
                {filter.name}: {selectedFilterValues[filter.name]?.length || 0} of {filterValues[filter.name]?.length || 0} selected
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
