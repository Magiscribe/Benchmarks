import { TestType } from '../../types/dashboard';

interface TestSelectorProps {
  testTypes: TestType[];
  selectedTestType: string;
  onSelectTestType: (testType: string) => void;
  loading: boolean;
}

export default function TestSelector({ testTypes, selectedTestType, onSelectTestType, loading }: TestSelectorProps) {
  const availableTests = testTypes.filter(t => t.available);
  const selectedTest = testTypes.find(t => t.name === selectedTestType);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
      </div>
    );
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Test Type
      </label>
      <select
        value={selectedTestType}
        onChange={(e) => onSelectTestType(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">Select a test type...</option>
        {availableTests.map((test) => (
          <option key={test.name} value={test.name}>
            {test.displayName || test.name}
          </option>
        ))}
      </select>
      
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
  );
}
