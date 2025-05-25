import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
import { JSX, useEffect, useState } from 'react';

interface AccuracyData {
  model: string;
  accuracy: number;
  total_correct: number;
  total_attempts: number;
}

interface FiltersData {
  models: string[];
  fonts: string[];
  sizes: number[];
}

/**
 * Dashboard page component for LLM Eye Test results
 * @returns {JSX.Element} The rendered dashboard page
 */
export default function Dashboard(): JSX.Element {
  const [filters, setFilters] = useState<FiltersData | null>(null);
  const [accuracyData, setAccuracyData] = useState<AccuracyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch filters on mount
  useEffect(() => {
    fetchFilters();
    fetchAccuracy();
  }, []);
  const fetchFilters = async () => {
    try {
      console.log('Fetching from:', `${import.meta.env.VITE_API_URL}/api/filters`);
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/filters`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Expected JSON but got:', text);
        throw new Error('Server returned non-JSON response');
      }
      
      const data = await response.json();
      console.log('Filters data:', data);
      setFilters(data);    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to fetch filters: ${errorMessage}`);
      console.error('Error fetching filters:', err);
    }
  };
  const fetchAccuracy = async () => {
    try {
      setLoading(true);
      console.log('Fetching accuracy from:', `${import.meta.env.VITE_API_URL}/api/accuracy`);
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/accuracy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}), // Empty filter for all data
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Expected JSON but got:', text);
        throw new Error('Server returned non-JSON response');
      }
      
      const data = await response.json();
      console.log('Accuracy data:', data);
      setAccuracyData(data.data || []);    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to fetch accuracy data: ${errorMessage}`);
      console.error('Error fetching accuracy:', err);
    } finally {
      setLoading(false);
    }
  };
  if (loading) {
    return (
      <Container>
        <Section title="Loading">
          <div className="flex items-center justify-center py-12">
            <div className="text-lg">Loading LLM Eye Test data...</div>
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
          </div>
        </Section>
      </Container>
    );
  }
  return (
    <Container>
      <Section title="LLM Eye Test Dashboard">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              LLM Eye Test Results
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Performance analysis of different language models on eye test benchmarks
            </p>
          </div>

          {/* Stats Cards */}
          {filters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Models Tested</h3>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                  {filters.models.length}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Font Types</h3>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                  {filters.fonts.length}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Font Sizes</h3>
                <p className="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">
                  {filters.sizes.length}
                </p>
              </div>
            </div>
          )}

          {/* Accuracy Results Table */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Model Accuracy</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Correct
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Total
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {accuracyData.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {item.model}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.accuracy > 0.8 
                            ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                            : item.accuracy > 0.6
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                            : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                        }`}>
                          {(item.accuracy * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {item.total_correct}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {item.total_attempts}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Debug Info */}
          <div className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Debug Info</h3>            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <p>API URL: {import.meta.env.VITE_API_URL}</p>
              <p>Auth Disabled: {String(import.meta.env.VITE_ENABLE_COGNITO_LOGIN !== 'true' && import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER !== 'true')}</p>
              <p>Filters loaded: {filters ? 'Yes' : 'No'}</p>
              <p>Accuracy data count: {accuracyData.length}</p>
              {error && <p className="text-red-500">Error: {error}</p>}
              <div className="mt-2 space-x-2">
                <button 
                  onClick={fetchFilters}
                  className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
                >
                  Test Filters API
                </button>
                <button 
                  onClick={fetchAccuracy}
                  className="px-3 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600"
                >
                  Test Accuracy API
                </button>
              </div>
            </div>
          </div>

          {/* API Status */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              API Status: Connected to {import.meta.env.VITE_API_URL}
            </p>
          </div>
        </div>
      </Section>
    </Container>
  );
}
