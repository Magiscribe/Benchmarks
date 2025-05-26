import { MultiMetricResults } from '../../types/dashboard';

interface ResultsTableProps {
  results: MultiMetricResults | null;
  selectedMetrics: string[];
  selectedTestType: string;
  sortField: string;
  sortDirection: 'asc' | 'desc';
  onSort: (field: string) => void;
  loading?: boolean;
}

export default function ResultsTable({
  results,
  selectedMetrics,
  selectedTestType,
  sortField,
  sortDirection,
  onSort,
  loading = false
}: ResultsTableProps) {
  const getSortedResults = () => {
    if (!results || selectedMetrics.length === 0) return [];
    
    // Get all models from the first metric's results
    const firstMetric = selectedMetrics[0];
    const models = Object.keys(results[firstMetric]?.results || {});
    
    const resultEntries = models.map(model => {
      const modelData: any = { model };
      
      // Add metric values for each selected metric
      selectedMetrics.forEach(metric => {
        const metricResult = results[metric]?.results[model];
        modelData[`${metric}_value`] = metricResult?.metric_value || 0;
        modelData[`${metric}_count`] = metricResult?.sample_count || 0;
      });
      
      return modelData;
    });

    return resultEntries.sort((a, b) => {
      let aValue, bValue;
      
      if (sortField === 'model') {
        aValue = a.model;
        bValue = b.model;
      } else {
        aValue = a[sortField] || 0;
        bValue = b[sortField] || 0;
      }
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      return sortDirection === 'asc' 
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          <div className="space-y-2">
            {[1,2,3,4,5].map(i => (
              <div key={i} className="h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!results || selectedMetrics.length === 0) {
    return null;
  }

  const sortedResults = getSortedResults();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <h4 className="text-lg font-medium text-gray-900 dark:text-white">
          Multi-Metric Results for {selectedTestType}
        </h4>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {sortedResults.length} models, {selectedMetrics.length} metrics
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th 
                onClick={() => onSort('model')}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
              >
                <div className="flex items-center space-x-1">
                  <span>Model</span>
                  {sortField === 'model' && (
                    <span className="text-blue-500">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              {selectedMetrics.map((metricName) => (
                <th 
                  key={metricName}
                  onClick={() => onSort(`${metricName}_value`)}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                >
                  <div className="flex items-center space-x-1">
                    <span>{metricName}</span>
                    {sortField === `${metricName}_value` && (
                      <span className="text-blue-500">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {sortedResults.map((result) => (
              <tr key={result.model} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {result.model}
                </td>
                {selectedMetrics.map((metricName) => (
                  <td key={metricName} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div>
                      <div className="font-medium">
                        {result[`${metricName}_value`]?.toFixed(4) || 'N/A'}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        ({result[`${metricName}_count`] || 0} samples)
                      </div>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
