import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { JSX } from 'react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement
);

interface MetricResult {
  name: string;
  displayName: string;
  description: string;
  value: number;
}

interface ChartData {
  testType: string;
  metrics: { [key: string]: MetricResult };
  filters: any;
}

interface MetricChartProps {
  data: ChartData[];
  chartType: 'bar' | 'line';
  metricKey: string;
  title?: string;
}

export default function MetricChart({ data, chartType, metricKey, title }: MetricChartProps): JSX.Element {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">No data available</p>
      </div>
    );
  }

  // Find the metric definition from the first data point
  const firstMetric = data[0].metrics[metricKey];
  if (!firstMetric) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <p className="text-gray-500 dark:text-gray-400">Metric "{metricKey}" not found</p>
      </div>
    );
  }

  // Prepare chart data
  const labels = data.map((_, index) => `Result Set ${index + 1}`);
  const values = data.map(d => d.metrics[metricKey]?.value || 0);

  const chartData = {
    labels,
    datasets: [
      {
        label: firstMetric.displayName,
        data: values,
        backgroundColor: chartType === 'bar' 
          ? 'rgba(59, 130, 246, 0.6)' 
          : 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: chartType === 'bar' ? 1 : 2,
        fill: chartType === 'line',
        tension: chartType === 'line' ? 0.4 : undefined,
      },
    ],
  };  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false as const, // Disable all animations for instant rendering
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title || firstMetric.displayName,
      },
      tooltip: {
        callbacks: {
          afterLabel: (context: any) => {
            const dataIndex = context.dataIndex;
            const resultData = data[dataIndex];
            
            // Show applied filters in tooltip
            const filterInfo = resultData.filters.groups
              .flatMap((group: any) => group.conditions)
              .map((condition: any) => `${condition.column}: ${condition.values.join(', ')}`)
              .join('\n');
            
            return filterInfo ? `Filters:\n${filterInfo}` : 'No filters applied';
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: firstMetric.displayName,
        },
      },
    },
  };

  const ChartComponent = chartType === 'bar' ? Bar : Line;

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <div className="h-96">
        <ChartComponent data={chartData} options={options} />
      </div>
      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p><strong>Description:</strong> {firstMetric.description}</p>
        <p><strong>Data Points:</strong> {data.length}</p>
      </div>
    </div>
  );
}
