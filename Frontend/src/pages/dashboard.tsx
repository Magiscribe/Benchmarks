import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
import { JSX, useEffect, useState } from 'react';

// Simple interface for test types
interface TestType {
  name: string;
  displayName?: string;
  description: string;
  available: boolean;
}

// Interface for filter columns
interface FilterColumn {
  name: string;
  type: 'identifier' | 'categorical';
  description: string;
}

// Interface for metrics
interface Metric {
  name: string;
  displayName: string;
  description: string;
}

// Interface for metric parameters
interface MetricParameter {
  name: string;
  type: string;
  default: any;
  description: string;
}

// Interface for results
interface ModelResult {
  metric_value: number;
  sample_count: number;
}

interface ResultsResponse {
  results: Record<string, ModelResult>;
  test_type: string;
  metric: string;
}

/**
 * Simple Dashboard for Test Selection
 * @returns {JSX.Element} The rendered dashboard page
 */
export default function Dashboard(): JSX.Element {  const [testTypes, setTestTypes] = useState<TestType[]>([]);
  const [selectedTestType, setSelectedTestType] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [availableFilters, setAvailableFilters] = useState<FilterColumn[]>([]);
  const [filterValues, setFilterValues] = useState<Record<string, string[]>>({});
  const [selectedFilterValues, setSelectedFilterValues] = useState<Record<string, string[]>>({});  const [availableMetrics, setAvailableMetrics] = useState<Metric[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<string>('');
  const [availableParameters, setAvailableParameters] = useState<MetricParameter[]>([]);
  const [parameterValues, setParameterValues] = useState<Record<string, any>>({});
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [sortField, setSortField] = useState<'model' | 'metric_value'>('model');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // API base URL
  const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

  // Load test types on component mount
  useEffect(() => {
    fetchTestTypes();
  }, []);  // Load models when test type changes
  useEffect(() => {
    if (selectedTestType) {
      fetchAvailableModels(selectedTestType);
      fetchAvailableFilters(selectedTestType);
      fetchAvailableMetrics(selectedTestType);
    } else {
      setAvailableModels([]);
      setSelectedModels([]);
      setAvailableFilters([]);
      setFilterValues({});
      setSelectedFilterValues({});      setAvailableMetrics([]);
      setSelectedMetric('');
      setAvailableParameters([]);
      setParameterValues({});
    }
  }, [selectedTestType]);

  // Load parameters when selected metric changes
  useEffect(() => {
    if (selectedTestType && selectedMetric) {
      fetchAvailableParameters(selectedTestType, selectedMetric);
    } else {
      setAvailableParameters([]);
      setParameterValues({});
    }
  }, [selectedTestType, selectedMetric]);

  const fetchTestTypes = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/available-tests`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: TestType[] = await response.json();
      setTestTypes(data);
      
      // Auto-select first available test type
      const firstAvailable = data.find(t => t.available);
      if (firstAvailable) {
        setSelectedTestType(firstAvailable.name);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load test types: ${errorMessage}`);
      console.error('Error fetching test types:', err);
    } finally {
      setLoading(false);
    }
  };
  const fetchAvailableModels = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-models/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const models: string[] = await response.json();
      setAvailableModels(models);
      // Select all models by default
      setSelectedModels(models);
    } catch (err) {
      console.error('Error fetching available models:', err);
      setAvailableModels([]);
      setSelectedModels([]);
    }
  };
  const fetchAvailableFilters = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-filters/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const filters: FilterColumn[] = await response.json();
      setAvailableFilters(filters);
      
      // Fetch values for each filter
      const filterValuesMap: Record<string, string[]> = {};
      const selectedValuesMap: Record<string, string[]> = {};
      
      for (const filter of filters) {
        try {
          const valuesResponse = await fetch(`${API_BASE}/available-filter-values/${testType}/${filter.name}`);
          if (valuesResponse.ok) {
            const values: string[] = await valuesResponse.json();
            filterValuesMap[filter.name] = values;
            // Select all values by default
            selectedValuesMap[filter.name] = [...values];
          }
        } catch (err) {
          console.error(`Error fetching values for filter ${filter.name}:`, err);
          filterValuesMap[filter.name] = [];
          selectedValuesMap[filter.name] = [];
        }
      }
      
      setFilterValues(filterValuesMap);
      setSelectedFilterValues(selectedValuesMap);    } catch (err) {
      console.error('Error fetching available filters:', err);
      setAvailableFilters([]);
      setFilterValues({});
      setSelectedFilterValues({});
    }
  };
  const fetchAvailableMetrics = async (testType: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-metrics/${testType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const metrics: Metric[] = await response.json();
      setAvailableMetrics(metrics);
      // Auto-select first metric by default
      if (metrics.length > 0) {
        setSelectedMetric(metrics[0].name);
      }
    } catch (err) {
      console.error('Error fetching available metrics:', err);
      setAvailableMetrics([]);
      setSelectedMetric('');
    }
  };

  const fetchAvailableParameters = async (testType: string, metricName: string) => {
    try {
      const response = await fetch(`${API_BASE}/available-parameters/${testType}/${metricName}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const parameters: MetricParameter[] = await response.json();
      setAvailableParameters(parameters);
      
      // Set default parameter values
      const defaultValues: Record<string, any> = {};
      parameters.forEach(param => {
        defaultValues[param.name] = param.default;
      });
      setParameterValues(defaultValues);
    } catch (err) {
      console.error('Error fetching available parameters:', err);
      setAvailableParameters([]);
      setParameterValues({});
    }
  };

  const fetchResults = async () => {
    if (!selectedTestType || !selectedMetric || selectedModels.length === 0) {
      return;
    }

    try {
      setResultsLoading(true);
      const response = await fetch(`${API_BASE}/results/${selectedTestType}/${selectedMetric}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selected_models: selectedModels,
          selected_filters: selectedFilterValues,
          parameter_values: parameterValues,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ResultsResponse = await response.json();
      setResults(data);
    } catch (err) {
      console.error('Error fetching results:', err);
      setResults(null);
    } finally {
      setResultsLoading(false);
    }
  };

  const handleModelSelection = (model: string) => {
    setSelectedModels(prev => 
      prev.includes(model) 
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  };

  const selectAllModels = () => {
    setSelectedModels([...availableModels]);
  };
  const selectNoModels = () => {
    setSelectedModels([]);
  };

  const handleFilterValueSelection = (filterName: string, value: string) => {
    setSelectedFilterValues(prev => ({
      ...prev,
      [filterName]: prev[filterName]?.includes(value)
        ? prev[filterName].filter(v => v !== value)
        : [...(prev[filterName] || []), value]
    }));
  };

  const selectAllFilterValues = (filterName: string) => {
    setSelectedFilterValues(prev => ({
      ...prev,
      [filterName]: [...(filterValues[filterName] || [])]
    }));
  };
  const selectNoFilterValues = (filterName: string) => {
    setSelectedFilterValues(prev => ({
      ...prev,
      [filterName]: []
    }));
  };

  const handleParameterValueChange = (paramName: string, value: any) => {
    setParameterValues(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleSort = (field: 'model' | 'metric_value') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortedResults = () => {
    if (!results) return [];
    
    const resultEntries = Object.entries(results.results).map(([model, result]) => ({
      model,
      ...result,
    }));

    return resultEntries.sort((a, b) => {
      let aValue, bValue;
      
      if (sortField === 'model') {
        aValue = a.model;
        bValue = b.model;
      } else {
        aValue = a.metric_value;
        bValue = b.metric_value;
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

  // Get the selected test type object
  const selectedTest = testTypes.find(t => t.name === selectedTestType);

  if (loading) {
    return (
      <Container>
        <Section title="Loading">
          <div className="flex items-center justify-center py-12">
            <div className="text-lg">Loading test types...</div>
          </div>
        </Section>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Section title="Error">
          <div className="flex items-center justify-center py-12">
            <div className="text-red-500">Error: {error}</div>
            <button 
              onClick={fetchTestTypes}
              className="ml-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </Section>
      </Container>
    );
  }

  return (
    <Container>
      <Section title="Test Selection">
        <div className="space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Benchmark Test Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Select a test to view its details
            </p>
          </div>          {/* Test Type and Metrics Selection */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Test Configuration
            </h2>
            <div className="space-y-4">
              {/* Dropdowns Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Test Type Dropdown */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Select Test Type
                  </label>
                  <select
                    value={selectedTestType}
                    onChange={(e) => setSelectedTestType(e.target.value)}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-lg"
                  >
                    <option value="">Choose a test...</option>
                    {testTypes
                      .filter(test => test.available)
                      .map((test) => (
                        <option key={test.name} value={test.name}>
                          {test.displayName || test.name}
                        </option>
                      ))}
                  </select>
                </div>

                {/* Metrics Dropdown */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Select Metric
                  </label>
                  <select
                    value={selectedMetric}
                    onChange={(e) => setSelectedMetric(e.target.value)}
                    disabled={!selectedTestType || availableMetrics.length === 0}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <option value="">Choose a metric...</option>
                    {availableMetrics.map((metric) => (
                      <option key={metric.name} value={metric.name}>
                        {metric.displayName}
                      </option>
                    ))}
                  </select>
                </div>
              </div>              {/* Display selected test and metric descriptions */}
              {selectedTest && (
                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    {selectedTest.displayName || selectedTest.name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {selectedTest.description}
                  </p>
                </div>
              )}
                {selectedMetric && availableMetrics.length > 0 && (
                <div className="mt-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white mb-1">
                    Selected Metric: {availableMetrics.find(m => m.name === selectedMetric)?.displayName}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {availableMetrics.find(m => m.name === selectedMetric)?.description}
                  </p>
                  
                  {/* Parameter Inputs */}
                  {availableParameters.length > 0 && (
                    <div className="mt-3">
                      <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                        Parameters ({availableParameters.length})
                      </h5>
                      <div className="space-y-3">
                        {availableParameters.map((param) => (
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
                                value={parameterValues[param.name] ?? param.default}
                                onChange={(e) => handleParameterValueChange(
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
              )}

              {/* Models Selection */}
              {selectedTestType && availableModels.length > 0 && (
                <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-md font-medium text-gray-900 dark:text-white">
                      Available Models ({availableModels.length})
                    </h4>
                    <div className="flex gap-2">
                      <button
                        onClick={selectAllModels}
                        className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-200 rounded hover:bg-blue-200 dark:hover:bg-blue-700"
                      >
                        Select All
                      </button>
                      <button
                        onClick={selectNoModels}
                        className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                      >
                        Select None
                      </button>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-40 overflow-y-auto">
                    {availableModels.map((model) => (
                      <label key={model} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedModels.includes(model)}
                          onChange={() => handleModelSelection(model)}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                          {model}
                        </span>
                      </label>
                    ))}
                  </div>
                  
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    Selected: {selectedModels.length} of {availableModels.length} models
                  </p>
                </div>
              )}              {selectedTestType && availableModels.length === 0 && (
                <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">
                    No models found for this test type. Check if results CSV exists.
                  </p>
                </div>
              )}              {/* Available Filters */}
              {selectedTestType && availableFilters.length > 0 && (
                <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">
                    Available Filters ({availableFilters.length})
                  </h4>
                  
                  <div className="space-y-4">
                    {availableFilters.map((filter) => (
                      <div 
                        key={filter.name} 
                        className="p-3 bg-white dark:bg-gray-800 rounded border"
                      >
                        <div className="flex items-start space-x-3 mb-3">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            filter.type === 'identifier' 
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                              : 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100'
                          }`}>
                            {filter.type}
                          </span>
                          <div className="flex-1">
                            <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                              {filter.name}
                            </h5>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {filter.description}
                            </p>
                          </div>
                        </div>
                        
                        {/* Filter Values Selection */}
                        {filterValues[filter.name] && filterValues[filter.name].length > 0 && (
                          <div className="mt-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                                Values ({filterValues[filter.name].length})
                              </span>
                              <div className="flex gap-1">
                                <button
                                  onClick={() => selectAllFilterValues(filter.name)}
                                  className="text-xs px-2 py-1 bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-200 rounded hover:bg-green-200 dark:hover:bg-green-700"
                                >
                                  All
                                </button>
                                <button
                                  onClick={() => selectNoFilterValues(filter.name)}
                                  className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                                >
                                  None
                                </button>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1 max-h-32 overflow-y-auto p-2 bg-gray-50 dark:bg-gray-900 rounded">
                              {filterValues[filter.name].map((value) => (
                                <label key={value} className="flex items-center space-x-1 cursor-pointer text-xs">
                                  <input
                                    type="checkbox"
                                    checked={selectedFilterValues[filter.name]?.includes(value) || false}
                                    onChange={() => handleFilterValueSelection(filter.name, value)}
                                    className="h-3 w-3 text-green-600 border-gray-300 rounded focus:ring-green-500"
                                  />
                                  <span className="text-gray-700 dark:text-gray-300 truncate">
                                    {value}
                                  </span>
                                </label>
                              ))}
                            </div>
                            
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              Selected: {selectedFilterValues[filter.name]?.length || 0} of {filterValues[filter.name].length} values
                            </p>
                          </div>
                        )}
                        
                        {filterValues[filter.name] && filterValues[filter.name].length === 0 && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">
                            No values available for this filter
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedTestType && availableFilters.length === 0 && (
                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900/20 rounded-lg">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No filterable columns found for this test type.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Results Section */}
          <div className="space-y-4">
            {/* Get Results Button */}
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Results</h3>
              <button
                onClick={fetchResults}
                disabled={!selectedTestType || !selectedMetric || selectedModels.length === 0 || resultsLoading}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {resultsLoading ? 'Loading...' : 'Get Results'}
              </button>
            </div>

            {/* Results Table */}
            {results && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
                <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                    {results.metric} Results for {results.test_type}
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {Object.keys(results.results).length} models
                  </p>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                          onClick={() => handleSort('model')}
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
                        <th
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                          onClick={() => handleSort('metric_value')}
                        >
                          <div className="flex items-center space-x-1">
                            <span>Metric Value</span>
                            {sortField === 'metric_value' && (
                              <span className="text-blue-500">
                                {sortDirection === 'asc' ? '↑' : '↓'}
                              </span>
                            )}
                          </div>
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Sample Count
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {getSortedResults().map((result) => (
                        <tr key={result.model} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {result.model}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {result.metric_value.toFixed(4)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {result.sample_count}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* No Results Message */}
            {!results && !resultsLoading && selectedTestType && selectedMetric && selectedModels.length > 0 && (
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  Click "Get Results" to fetch metric calculations for the selected configuration.
                </p>
              </div>
            )}

            {/* Selection Requirements Message */}
            {(!selectedTestType || !selectedMetric || selectedModels.length === 0) && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                      Selection Required
                    </h3>
                    <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                      <p>To get results, please ensure you have:</p>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        <li>Selected a test type</li>
                        <li>Selected a metric</li>
                        <li>Selected at least one model</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Unavailable Tests */}
          {testTypes.some(t => !t.available) && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Unavailable Tests
              </h2>
              <div className="space-y-2">
                {testTypes
                  .filter(test => !test.available)
                  .map((test) => (
                    <div 
                      key={test.name}
                      className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg opacity-60"
                    >
                      <h3 className="font-medium text-gray-700 dark:text-gray-300">
                        {test.displayName || test.name}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {test.description}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          )}          {/* Debug Info */}
          <div className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Debug Info</h3>            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <p>API URL: {API_BASE}</p>
              <p>Selected Test Type: {selectedTestType || 'None'}</p>
              <p>Total Test Types: {testTypes.length}</p>
              <p>Available Test Types: {testTypes.filter(t => t.available).length}</p>
              <p>Available Models: {availableModels.length}</p>
              <p>Selected Models: {selectedModels.length}</p>              <p>Available Metrics: {availableMetrics.length}</p>
              <p>Selected Metric: {selectedMetric || 'None'}</p>
              <p>Available Parameters: {availableParameters.length}</p>
              <p>Available Filters: {availableFilters.length}</p>
              {availableParameters.length > 0 && (
                <div className="mt-2">
                  <p className="font-medium">Parameter Values:</p>
                  {availableParameters.map((param) => (
                    <p key={param.name} className="ml-2">
                      {param.name}: {parameterValues[param.name] ?? param.default} (default: {param.default})
                    </p>
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
        </div>
      </Section>
    </Container>
  );
}
