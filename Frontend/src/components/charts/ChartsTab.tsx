import React from 'react';
import { TestType } from '../../types/dashboard';
import { ChartFirstDashboard } from '../charts/ChartFirstDashboard';

interface ChartsTabProps {
  testTypes: TestType[];
}

export const ChartsTab: React.FC<ChartsTabProps> = ({ testTypes }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          📊 Chart Builder
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Create interactive charts and visualizations from your benchmark data. 
          Configure chart types, select metrics, and apply filters to analyze model performance.
        </p>
      </div>

      {/* Existing Chart Dashboard */}
      <ChartFirstDashboard testTypes={testTypes} />
    </div>
  );
};
