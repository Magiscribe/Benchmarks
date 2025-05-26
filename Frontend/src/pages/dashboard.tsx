import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
import Loading from '@/components/Loading';
import TestSelector from '@/components/dashboard/TestSelector';
import MetricSelector from '@/components/dashboard/MetricSelector';
import ModelSelector from '@/components/dashboard/ModelSelector';
import FilterSelector from '@/components/dashboard/FilterSelector';
import GroupBySelector from '@/components/dashboard/GroupBySelector';
import ResultsTable from '@/components/dashboard/ResultsTable';
import DebugInfo from '@/components/dashboard/DebugInfo';
import { useDashboardData } from '@/hooks/useDashboardData';
import { useModels } from '@/hooks/useModels';
import { useMetrics } from '@/hooks/useMetrics';
import { useFilters } from '@/hooks/useFilters';
import { useGroupBy } from '@/hooks/useGroupBy';
import { useResults } from '@/hooks/useResults';

export default function Dashboard() {
  // Dashboard data (test types, selection, loading, error)
  const {
    testTypes,
    selectedTestType,
    setSelectedTestType,
    loading,
    error,
    refetch: refetchTestTypes
  } = useDashboardData();

  // Models
  const {
    availableModels,
    selectedModels,
    handleModelSelection,
    selectAllModels,
    selectNoModels,
    setSelectedModels
  } = useModels(selectedTestType);

  // Metrics and parameters
  const {
    availableMetrics,
    selectedMetrics,
    availableParameters,
    parameterValues,
    handleMetricSelection,
    selectAllMetrics,
    selectNoMetrics,
    handleParameterValueChange,
    setSelectedMetrics
  } = useMetrics(selectedTestType);

  // Filters
  const {
    availableFilters,
    filterValues,
    selectedFilterValues,
    handleFilterValueSelection,
    selectAllFilterValues,
    selectNoFilterValues
  } = useFilters(selectedTestType);

  // Group By
  const {
    availableGroupBy,
    selectedGroupBy,
    handleGroupBySelect,
    selectAllGroupBy,
    selectNoGroupBy
  } = useGroupBy(selectedTestType);

  // Results
  const {
    results,
    resultsLoading,
    sortField,
    sortDirection,
    fetchResults,
    handleSort
  } = useResults();

  // Get the selected test type object
  const selectedTest = testTypes.find(t => t.name === selectedTestType);

  // Prepare request for results
  const canFetchResults = !!selectedTestType && selectedMetrics.length > 0 && selectedModels.length > 0;
  const handleFetchResults = () => {
    if (!canFetchResults) return;
    fetchResults(
      selectedTestType,
      selectedMetrics,
      {
        models: selectedModels,
        filters: selectedFilterValues,
        parameters: Object.fromEntries(
          selectedMetrics.map(metric => [metric, parameterValues[metric] || {}])
        )
      },
      selectedGroupBy
    );
  };

  if (loading) {
    return (
      <Container>
        <Section title="Loading">
          <div className="flex items-center justify-center py-12">
            <Loading className="w-8 h-8 mr-3" />
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
              onClick={refetchTestTypes}
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
          </div>

          {/* Test Type and Metrics Selection */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Test Configuration
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Test Type Dropdown */}
                <TestSelector
                  testTypes={testTypes}
                  selectedTestType={selectedTestType}
                  onSelectTestType={setSelectedTestType}
                  loading={loading}
                />
                {/* Metrics Selection */}
                <MetricSelector
                  availableMetrics={availableMetrics}
                  selectedMetrics={selectedMetrics}
                  availableParameters={availableParameters}
                  parameterValues={parameterValues}
                  onMetricSelect={handleMetricSelection}
                  onSelectAll={selectAllMetrics}
                  onSelectNone={selectNoMetrics}
                  onParameterChange={handleParameterValueChange}
                />
              </div>
              {/* Selected Test Description */}
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
            </div>
          </div>

          {/* Models Selection */}
          <ModelSelector
            availableModels={availableModels}
            selectedModels={selectedModels}
            onModelSelect={handleModelSelection}
            onSelectAll={selectAllModels}
            onSelectNone={selectNoModels}
          />

          {/* Filters Selection */}
          <FilterSelector
            availableFilters={availableFilters}
            filterValues={filterValues}
            selectedFilterValues={selectedFilterValues}
            onFilterValueSelect={handleFilterValueSelection}
            onSelectAllValues={selectAllFilterValues}
            onSelectNoValues={selectNoFilterValues}
          />

          {/* Group By Selection */}
          <GroupBySelector
            availableGroupBy={availableGroupBy}
            selectedGroupBy={selectedGroupBy}
            onGroupBySelect={handleGroupBySelect}
            onSelectAll={selectAllGroupBy}
            onSelectNone={selectNoGroupBy}
          />

          {/* Results Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Results</h3>
              <button
                onClick={handleFetchResults}
                disabled={!canFetchResults || resultsLoading}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {resultsLoading ? 'Loading...' : `Get Results (${selectedMetrics.length} metrics)`}
              </button>
            </div>
            <ResultsTable
              results={results}
              selectedMetrics={selectedMetrics}
              selectedTestType={selectedTestType}
              sortField={sortField}
              sortDirection={sortDirection}
              onSort={handleSort}
              loading={resultsLoading}
            />
            {/* No Results Message */}
            {!results && !resultsLoading && canFetchResults && (
              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  Click "Get Results" to fetch metric calculations for the selected configuration.
                </p>
              </div>
            )}
            {/* Selection Requirements Message */}
            {!canFetchResults && (
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
                        <li>Selected at least one metric</li>
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
          )}

          {/* Debug Info */}
          <DebugInfo
            selectedTestType={selectedTestType}
            testTypes={testTypes}
            availableModels={availableModels}
            selectedModels={selectedModels}
            availableMetrics={availableMetrics}
            selectedMetrics={selectedMetrics}
            availableParameters={availableParameters}
            parameterValues={parameterValues}
            availableFilters={availableFilters}
            selectedFilterValues={selectedFilterValues}
            filterValues={filterValues}
            availableGroupBy={availableGroupBy}
            selectedGroupBy={selectedGroupBy}
          />
        </div>
      </Section>
    </Container>
  );
}
