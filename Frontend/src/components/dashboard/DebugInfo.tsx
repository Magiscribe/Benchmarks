import { TestType, Metric, FilterColumn } from '@/types/dashboard';

interface DebugInfoProps {
  selectedTestType: string;
  testTypes: TestType[];
  availableModels: string[];
  selectedModels: string[];
  availableMetrics: Metric[];
  selectedMetrics: string[];
  availableParameters: Record<string, any>;
  parameterValues: Record<string, Record<string, any>>;
  availableFilters: FilterColumn[];
  selectedFilterValues: Record<string, string[]>;
  filterValues: Record<string, string[]>;
  availableGroupBy: FilterColumn[];
  selectedGroupBy: string[];
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
  filterValues,
  availableGroupBy,
  selectedGroupBy
}: DebugInfoProps) {
  const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        Debug Information
      </h2>
      <div className="space-y-4">
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Selected Test Type</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(selectedTestType, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Available Models</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(availableModels, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Selected Models</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(selectedModels, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Available Metrics</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(availableMetrics, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Selected Metrics</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(selectedMetrics, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Available Parameters</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(availableParameters, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Parameter Values</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(parameterValues, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Available Filters</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(availableFilters, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Selected Filter Values</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(selectedFilterValues, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Filter Values</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(filterValues, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Available Group By</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(availableGroupBy, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="font-medium text-gray-700 dark:text-gray-300">Selected Group By</h3>
          <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
            {JSON.stringify(selectedGroupBy, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
