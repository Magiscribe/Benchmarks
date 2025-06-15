import React from 'react';

export const LeaderboardTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          🏆 Model Leaderboard
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Compare model performance across different metrics and test types.
        </p>
      </div>

      {/* Placeholder Content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-8">
        <div className="text-center">
          <div className="mb-4">
            <span className="text-6xl">🚧</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Leaderboard Coming Soon
          </h3>
          <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
            We're building a comprehensive leaderboard that will show model rankings across 
            different metrics and test types. This will include sortable tables, filtering 
            options, and detailed performance comparisons.
          </p>
          <div className="mt-6 inline-flex items-center px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg">
            <span className="mr-2">⏳</span>
            In Development
          </div>
        </div>
      </div>

      {/* Preview of what's coming */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Planned Features:
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex items-start space-x-3">
            <span className="text-green-500">✅</span>
            <div>
              <h5 className="font-medium text-gray-900 dark:text-white">Model Rankings</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">Sortable table by performance metrics</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-green-500">✅</span>
            <div>
              <h5 className="font-medium text-gray-900 dark:text-white">Test Type Filtering</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">Filter results by specific test types</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-green-500">✅</span>
            <div>
              <h5 className="font-medium text-gray-900 dark:text-white">Metric Comparison</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">Side-by-side metric comparisons</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-yellow-500">⏳</span>
            <div>
              <h5 className="font-medium text-gray-900 dark:text-white">Export Options</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">Download leaderboard data as CSV/JSON</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-yellow-500">⏳</span>
            <div>
              <h5 className="font-medium text-gray-900 dark:text-white">Historical Tracking</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">Track performance changes over time</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-yellow-500">⏳</span>
            <div>
              <h5 className="font-medium text-gray-900 dark:text-white">Custom Metrics</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">User-defined evaluation criteria</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
