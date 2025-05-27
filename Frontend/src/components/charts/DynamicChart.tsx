import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Scatter } from 'react-chartjs-2';
import { MultiMetricResults } from '../../types/dashboard';
import { ChartConfiguration } from '../../types/charts';
import { transformDataForChart, getChartOptions } from '../../utils/chartTransforms';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

interface DynamicChartProps {
  results: MultiMetricResults;
  config: ChartConfiguration;
}

export const DynamicChart: React.FC<DynamicChartProps> = ({ results, config }) => {
  const { datasets, labels } = transformDataForChart(results, config);
  const options = getChartOptions(config);

  const chartData = {
    labels,
    datasets: datasets.map(dataset => ({
      ...dataset,
      data: dataset.data.map(point => ({
        x: point.x,
        y: point.y
      }))
    }))
  };

  // Custom tooltip for better data display
  const customOptions = {
    ...options,
    plugins: {
      ...options.plugins,
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const point = datasets[context.datasetIndex]?.data[context.dataIndex];
            if (!point) return '';

            if (config.chartType === 'scatter') {
              return `${point.model}: (${context.parsed.x?.toFixed(2)}, ${context.parsed.y?.toFixed(2)})`;
            }

            return `${context.dataset.label}: ${context.parsed.y?.toFixed(2) || 'N/A'}`;
          }
        }
      }
    }
  };

  const renderChart = () => {
    switch (config.chartType) {
      case 'bar':
        return <Bar data={chartData} options={customOptions} />;
      case 'line':
        return <Line data={chartData} options={customOptions} />;
      case 'scatter':
        return <Scatter data={chartData} options={customOptions} />;
      default:
        return <Bar data={chartData} options={customOptions} />;
    }
  };

  if (!results || Object.keys(results).length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">No data available for chart</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="h-96">
        {renderChart()}
      </div>
      
      {/* Chart Info */}
      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex flex-wrap gap-4">
          <span><strong>Type:</strong> {config.chartType}</span>
          <span><strong>Data Points:</strong> {datasets.reduce((sum, ds) => sum + ds.data.length, 0)}</span>
        </div>
      </div>
    </div>
  );
};
