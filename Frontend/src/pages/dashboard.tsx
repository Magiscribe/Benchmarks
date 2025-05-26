import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
// import MetricChart from '@/components/charts/MetricChart';
import { JSX, useEffect, useState } from 'react';

// API Types based on new documentation
interface TestType {
  name: string;
  displayName?: string;
  description: string;
  available: boolean;
}

interface FilterColumn {
  column: string;
  type: string;
  displayName: string;
  description: string;
  operators: string[];
  values: string[];
}

interface FilterCapabilities {
  test_type: string;
  columns: FilterColumn[];
}

interface MetricDefinition {
  name: string;
  displayName: string;
  description: string;
  parameters: any[];
}

interface TestConfig {
  testType: string;
  description: string;
  columns: any[];
  metrics: MetricDefinition[];
}

interface FilterCondition {
  column: string;
  operator: string;
  values?: string[];
}

interface FilterGroup {
  operator: 'AND' | 'OR';
  conditions?: FilterCondition[];
}

interface Filters {
  groups?: FilterGroup[];
}

interface MetricResult {
  name?: string;
  displayName?: string;
  description?: string;
  value?: number;
}

interface FilteredDataResponse {
  test_type: string;
  total_rows: number;
  filtered_rows: number;
  execution_time_ms: number;
  metrics?: { [key: string]: MetricResult };
}

interface ChartData {
  testType: string;
  metrics?: { [key: string]: MetricResult };
  filters?: Filters;
}

/**
 * Dynamic Chart Builder Dashboard for LLM Benchmark Analysis
 * @returns {JSX.Element} The rendered dashboard page
 */
export default function Dashboard(): JSX.Element {
  // State for test types and configuration
  const [testTypes, setTestTypes] = useState<TestType[]>([]);
  const [selectedTestType, setSelectedTestType] = useState<string>('');
  const [testConfig, setTestConfig] = useState<TestConfig | null>(null);
  const [filterCapabilities, setFilterCapabilities] = useState<FilterCapabilities | null>(null);
  
  // State for dynamic filters
  const [selectedFilters, setSelectedFilters] = useState<{ [column: string]: string[] }>({});
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
    // State for chart data and UI
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [selectedChartMetric, setSelectedChartMetric] = useState<string>('');
  const [chartType, setChartType] = useState<'bar' | 'line'>('bar');

  // API base URL
  const API_BASE = `${import.meta.env.VITE_API_URL}/api/data`;

  // Initialize the dashboard
  useEffect(() => {
    initializeDashboard();
  }, []);

  // Load test configuration when test type changes
  useEffect(() => {
    if (selectedTestType) {
      loadTestConfiguration(selectedTestType);
    }
  }, [selectedTestType]);

  const initializeDashboard = async () => {
    try {
      setLoading(true);
      await fetchTestTypes();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to initialize dashboard: ${errorMessage}`);
      console.error('Error initializing dashboard:', err);
    } finally {
      setLoading(false);
    }
  };
  const fetchTestTypes = async () => {
    try {
      const response = await fetch(`${API_BASE}/test-types`);
      
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
      console.error('Error fetching test types:', err);
      throw err;
    }
  };
  const loadTestConfiguration = async (testType: string) => {
    try {
      setError(null);      // Fetch test configuration
      const configResponse = await fetch(`${API_BASE}/config/${testType}`);
      if (!configResponse.ok) {
        throw new Error(`Failed to fetch config: ${configResponse.status}`);
      }
      const config: TestConfig = await configResponse.json();
      setTestConfig(config);

      // Fetch filter capabilities
      const filterResponse = await fetch(`${API_BASE}/filter-capabilities/${testType}`);
      if (!filterResponse.ok) {
        throw new Error(`Failed to fetch filters: ${filterResponse.status}`);
      }
      const filters: FilterCapabilities = await filterResponse.json();
      setFilterCapabilities(filters);      // Reset selections
      setSelectedFilters({});
      setSelectedMetrics([]);
      setChartData([]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load test configuration: ${errorMessage}`);
      console.error('Error loading test configuration:', err);
    }
  };

  const executeMetrics = async () => {
    if (!selectedTestType || selectedMetrics.length === 0) {
      setError('Please select a test type and at least one metric');
      return;
    }

    try {
      setIsExecuting(true);
      setError(null);

      // Build filter object
      const filterGroups: FilterGroup[] = [];
      const conditions: FilterCondition[] = [];

      Object.entries(selectedFilters).forEach(([column, values]) => {
        if (values.length > 0) {
          conditions.push({
            column,
            operator: values.length === 1 ? 'equals' : 'in',
            values
          });
        }
      });

      if (conditions.length > 0) {
        filterGroups.push({
          operator: 'AND',
          conditions
        });
      }

      const requestBody = {
        test_type: selectedTestType,
        filters: { groups: filterGroups },        metrics: selectedMetrics
      };

      const response = await fetch(`${API_BASE}/filtered`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }      const data: FilteredDataResponse = await response.json();
      
      // Add to chart data
      const newChartData: ChartData = {
        testType: selectedTestType,
        metrics: data.metrics || {},
        filters: { groups: filterGroups || [] }
      };

      setChartData(prev => [...prev, newChartData]);
      
      // Auto-select first metric for chart if none selected
      if (!selectedChartMetric && selectedMetrics.length > 0) {
        setSelectedChartMetric(selectedMetrics[0]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to execute metrics: ${errorMessage}`);
      console.error('Error executing metrics:', err);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleFilterChange = (column: string, values: string[]) => {
    setSelectedFilters(prev => ({
      ...prev,
      [column]: values
    }));
  };

  const handleMetricToggle = (metric: string) => {
    setSelectedMetrics(prev => 
      prev.includes(metric) 
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    );
  };  if (loading) {
    return (
      <Container>
        <Section title="Loading">
          <div className="flex items-center justify-center py-12">
            <div className="text-lg">Loading benchmark data...</div>
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
              onClick={initializeDashboard}
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
      <Section title="LLM Benchmark Chart Builder">
        <div className="space-y-6">
          {/* Header */}          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Dynamic Chart Builder
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Build custom visualizations from LLM benchmark data using advanced filtering and metrics
            </p>
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
                How to use:
              </h3>
              <ol className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                <li>1. Select a test type (Eye_Test, Coordinate_Grid, etc.)</li>
                <li>2. Apply filters to narrow down the data (optional)</li>
                <li>3. Choose metrics to calculate</li>
                <li>4. Execute to generate results</li>
                <li>5. Visualize results with interactive charts</li>
              </ol>
            </div>
          </div>

          {/* Test Type Selection */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              1. Select Test Type
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {testTypes.map((testType) => (
                <button
                  key={testType.name}
                  onClick={() => setSelectedTestType(testType.name)}
                  disabled={!testType.available}
                  className={`p-4 rounded-lg border-2 text-left transition-colors ${
                    selectedTestType === testType.name
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : testType.available
                      ? 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      : 'border-gray-100 dark:border-gray-800 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {testType.displayName || testType.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {testType.description}
                  </p>
                  {!testType.available && (
                    <span className="inline-block mt-2 px-2 py-1 text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                      Not Available
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>          {/* Filter Builder */}
          {filterCapabilities && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                2. Configure Filters
              </h2>              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filterCapabilities.columns?.map((column) => (
                  <div key={column.column} className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {column.displayName}
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {column.description}
                    </p>                    <select
                      multiple
                      value={selectedFilters[column.column] || []}
                      onChange={(e) => {
                        const values = Array.from(e.target.selectedOptions, option => option.value);
                        handleFilterChange(column.column, values);
                      }}
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      size={Math.min(5, column.values?.length || 0)}                    >
                      {column.values?.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Selected: {(selectedFilters[column.column] || []).length} of {column.values?.length || 0}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}          {/* Metrics Selection */}
          {testConfig && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                3. Select Metrics
              </h2>              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {testConfig.metrics?.map((metric) => (
                  <label key={metric.name} className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedMetrics.includes(metric.name)}
                      onChange={() => handleMetricToggle(metric.name)}
                      className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {metric.displayName}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {metric.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Execute Button */}
          {selectedTestType && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    4. Execute Analysis
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Generate metrics with current filters ({selectedMetrics.length} metrics selected)
                  </p>
                </div>
                <button
                  onClick={executeMetrics}
                  disabled={isExecuting || selectedMetrics.length === 0}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                    isExecuting || selectedMetrics.length === 0
                      ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {isExecuting ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                      <span>Executing...</span>
                    </div>
                  ) : (
                    'Execute Metrics'
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Results Display */}
          {chartData.length > 0 && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Analysis Results
                </h2>                <button
                  onClick={() => {
                    setChartData([]);
                    setSelectedChartMetric('');
                  }}
                  className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  Clear All
                </button>
              </div>              <div className="space-y-4">
                {chartData.map((result, index) => {
                  return (
                    <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          Result Set #{index + 1}
                        </h3>
                        <button
                          onClick={() => setChartData(prev => prev.filter((_, i) => i !== index))}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Remove
                        </button>
                      </div>
                      
                      {/* Applied Filters */}
                      <div className="mb-3">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Applied Filters:
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {!result.filters?.groups || result.filters.groups.length === 0 ? (
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs">
                              No filters applied
                            </span>                          ) : (
                            result.filters.groups.flatMap(group => 
                              (group.conditions || []).map((condition, condIndex) => (
                                <span 
                                  key={condIndex}
                                  className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs"
                                >
                                  {condition.column}: {condition.values?.join(', ')}
                                </span>
                              ))
                            )
                          )}
                        </div>
                      </div>

                      {/* Metrics Results */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {result.metrics && Object.entries(result.metrics).map(([key, metric]) => (
                          <div key={key} className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {metric?.displayName || key}
                            </h4>
                            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                              {typeof metric?.value === 'number' 
                                ? (metric.value < 1 ? (metric.value * 100).toFixed(2) + '%' : metric.value.toFixed(3))
                                : metric?.value || 'N/A'
                              }
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {metric?.description || 'No description available'}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>          )}

          {/* Chart Visualization */}
          {chartData.length > 0 && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Chart Visualization
                </h2>
                <div className="flex items-center space-x-4">
                  {/* Chart Type Selector */}
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Chart Type:
                    </label>
                    <select
                      value={chartType}
                      onChange={(e) => setChartType(e.target.value as 'bar' | 'line')}
                      className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    >
                      <option value="bar">Bar Chart</option>
                      <option value="line">Line Chart</option>
                    </select>
                  </div>

                  {/* Metric Selector */}
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Metric:
                    </label>
                    <select
                      value={selectedChartMetric}
                      onChange={(e) => setSelectedChartMetric(e.target.value)}
                      className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    >
                      <option value="">Select metric to visualize</option>                      {/* Get unique metrics from all chart data */}
                      {Array.from(
                        new Set(
                          chartData.flatMap(result => result.metrics ? Object.keys(result.metrics) : [])
                        )
                      ).map(metricKey => {
                        const metric = chartData.find(result => result.metrics?.[metricKey])?.metrics?.[metricKey];
                        return (
                          <option key={metricKey} value={metricKey}>
                            {metric?.displayName || metricKey}
                          </option>
                        );
                      })}
                    </select>
                  </div>
                </div>
              </div>              {selectedChartMetric ? (
                <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-center">
                    <p className="text-gray-500 dark:text-gray-400 mb-2">
                      Chart visualization coming soon!
                    </p>
                    <p className="text-sm text-gray-400 dark:text-gray-500">
                      Selected: {chartData.find(d => d.metrics?.[selectedChartMetric])?.metrics?.[selectedChartMetric]?.displayName || selectedChartMetric}
                    </p>
                  </div>
                </div>
                // <MetricChart 
                //   data={chartData}
                //   chartType={chartType}
                //   metricKey={selectedChartMetric}
                //   title={`${chartData.find(d => d.metrics?.[selectedChartMetric])?.metrics?.[selectedChartMetric]?.displayName || selectedChartMetric} Comparison`}
                // />
              ) : (
                <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <p className="text-gray-500 dark:text-gray-400">
                    Select a metric to visualize your results
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Debug Info */}
          <div className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Debug Info</h3>
            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <p>API URL: {API_BASE}</p>
              <p>Selected Test Type: {selectedTestType || 'None'}</p>
              <p>Test Types Loaded: {testTypes.length}</p>
              <p>Filter Capabilities: {filterCapabilities ? 'Loaded' : 'Not loaded'}</p>
              <p>Test Config: {testConfig ? 'Loaded' : 'Not loaded'}</p>
              <p>Selected Filters: {Object.keys(selectedFilters).length}</p>
              <p>Selected Metrics: {selectedMetrics.length}</p>
              <p>Chart Results: {chartData.length}</p>
              {error && <p className="text-red-500">Error: {error}</p>}
            </div>
          </div>
        </div>
      </Section>
    </Container>
  );
}
