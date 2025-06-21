import { MultiMetricResults } from '../types/dashboard';
import { ChartConfiguration, ChartDataset, ChartDataPoint, FlatResult } from '../types/charts';

// Helper function to flatten MultiMetricResults into a more workable format
export const flattenResults = (results: MultiMetricResults): FlatResult[] => {
  const flatResults: FlatResult[] = [];
  const metricNames = Object.keys(results);
  
  // Get all unique models across all metrics
  const allModels = new Set<string>();
  metricNames.forEach(metric => {
    results[metric].results.forEach(result => {
      allModels.add(result.model);
    });
  });

  // Create a flat result for each model
  Array.from(allModels).forEach(model => {
    const flatResult: FlatResult = {
      model,
      metrics: {},
      groupings: undefined
    };

    // Collect metric values for this model
    metricNames.forEach(metric => {
      const modelResult = results[metric].results.find(r => r.model === model);
      if (modelResult) {
        flatResult.metrics[metric] = modelResult.value;
        // Use groupings from the first metric that has them
        if (!flatResult.groupings && modelResult.groupings && modelResult.groupings.length > 0) {
          flatResult.groupings = modelResult.groupings;
        }
      }
    });

    flatResults.push(flatResult);
  });

  return flatResults;
};

export const transformDataForChart = (
  results: MultiMetricResults,
  config: ChartConfiguration
): { datasets: ChartDataset[], labels?: string[] } => {
  switch (config.chartType) {
    case 'bar':
      return transformForBar(flattenResults(results), config);
    case 'scatter':
      return transformForScatter(flattenResults(results), config);
    case 'line':
      return transformForLineFromOriginal(results, config);
    default:
      return { datasets: [], labels: [] };
  }
};

// Bar chart: Models on X-axis, 1-2 metrics on Y-axis
const transformForBar = (
  results: FlatResult[],
  config: ChartConfiguration
): { datasets: ChartDataset[], labels?: string[] } => {
  if (!config.metric1) {
    return { datasets: [], labels: [] };
  }

  // Sort models by their primary metric values (ascending order)
  const modelsWithValues = results
    .map(r => ({
      model: r.model,
      value: r.metrics[config.metric1!] || 0
    }))
    .sort((a, b) => a.value - b.value); // Sort by value ascending
  
  const models = modelsWithValues.map(item => item.model);
  const datasets: ChartDataset[] = [];

  // Primary metric dataset
  const primaryData: ChartDataPoint[] = models.map(model => {
    const result = results.find(r => r.model === model);
    return {
      x: model,
      y: result?.metrics[config.metric1!] || 0,
      model,
      metric: config.metric1!
    };
  });

  datasets.push({
    label: config.metric1,
    data: primaryData,
    backgroundColor: 'rgba(54, 162, 235, 0.8)',
    borderColor: 'rgba(54, 162, 235, 1)',
    yAxisID: 'y1'
  });

  // Secondary metric dataset (if provided)
  if (config.metric2) {
    const secondaryData: ChartDataPoint[] = models.map(model => {
      const result = results.find(r => r.model === model);
      return {
        x: model,
        y: result?.metrics[config.metric2!] || 0,
        model,
        metric: config.metric2!
      };
    });

    datasets.push({
      label: config.metric2,
      data: secondaryData,
      backgroundColor: 'rgba(255, 99, 132, 0.8)',
      borderColor: 'rgba(255, 99, 132, 1)',
      yAxisID: 'y2'
    });
  }

  return {
    datasets,
    labels: models
  };
};

// Scatter plot: Metric vs Metric
const transformForScatter = (
  results: FlatResult[],
  config: ChartConfiguration
): { datasets: ChartDataset[], labels?: string[] } => {
  if (!config.xMetric || !config.yMetric) {
    return { datasets: [], labels: [] };
  }

  const data: ChartDataPoint[] = results
    .filter(result => 
      result.metrics[config.xMetric!] !== undefined && 
      result.metrics[config.yMetric!] !== undefined
    )
    .map(result => ({
      x: result.metrics[config.xMetric!],
      y: result.metrics[config.yMetric!],
      model: result.model,
      metric: `${config.xMetric} vs ${config.yMetric}`
    }));

  return {
    datasets: [{
      label: `${config.xMetric} vs ${config.yMetric}`,
      data,
      backgroundColor: 'rgba(75, 192, 192, 0.6)',
      borderColor: 'rgba(75, 192, 192, 1)'
    }]
  };
};

// Line chart: Categorical on X-axis, Metric on Y-axis (per model)
// This function works with the original MultiMetricResults to preserve categorical grouping
const transformForLineFromOriginal = (
  results: MultiMetricResults,
  config: ChartConfiguration
): { datasets: ChartDataset[], labels?: string[] } => {
  if (!config.categorical || !config.lineMetric) {
    return { datasets: [], labels: [] };
  }

  // Get the metric data from the original results
  const metricResults = results[config.lineMetric];
  if (!metricResults || !metricResults.results || metricResults.results.length === 0) {
    return { datasets: [], labels: [] };  }
    // For line charts, we need access to grouping data from the raw results
  // Since the new backend structure uses groupings as an array, we'll need to handle this differently
  // For now, we'll assume categorical grouping is the first element in the groupings array
  const categoryValues = Array.from(new Set(
    metricResults.results
      .filter(result => result.groupings && result.groupings.length > 0)
      .map(result => result.groupings[0])
  ));
  // Sort category values - handle numeric vs alphabetic sorting
  const sortedCategoryValues = categoryValues.sort((a, b) => {
    // Try to parse as numbers first
    const numA = parseFloat(a);
    const numB = parseFloat(b);
    
    // If both are valid numbers, sort numerically
    if (!isNaN(numA) && !isNaN(numB)) {
      return numA - numB;
    }
    
    // Otherwise, sort alphabetically
    return a.localeCompare(b);
  });

  if (sortedCategoryValues.length === 0) {
    return { datasets: [], labels: [] };
  }

  // Get all unique models
  const models = Array.from(new Set(metricResults.results.map(r => r.model))).sort();
  const datasets: ChartDataset[] = models.map((model, index) => {
    const data: ChartDataPoint[] = sortedCategoryValues.map(category => {
      // Find the data point for this model and category
      const dataPoint = metricResults.results.find(result => 
        result.model === model && 
        result.groupings && result.groupings[0] === category
      );
      
      return {
        x: category,
        y: dataPoint?.value || 0,
        model,
        metric: config.lineMetric!
      };
    });

    // Generate different colors for each model
    const hue = (index * 137.508) % 360; // Golden angle approximation for good color distribution
    const color = `hsl(${hue}, 70%, 50%)`;

    return {
      label: model,
      data,
      borderColor: color,
      backgroundColor: color.replace('50%', '20%'),
      fill: false
    };
  });
  return {
    datasets,
    labels: sortedCategoryValues
  };
};

// Helper functions for chart options based on configuration
export const getChartOptions = (config: ChartConfiguration) => {
  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false as const, // Disable all animations for instant rendering
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: getChartTitle(config)
      }
    }
  };

  switch (config.chartType) {
    case 'bar':
      return {
        ...baseOptions,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Models'
            }
          },
          y1: {
            type: 'linear' as const,
            display: true,
            position: 'left' as const,
            title: {
              display: true,
              text: config.metric1 || 'Primary Metric'
            }
          },
          ...(config.metric2 && {
            y2: {
              type: 'linear' as const,
              display: true,
              position: 'right' as const,
              title: {
                display: true,
                text: config.metric2
              },
              grid: {
                drawOnChartArea: false,
              },
            }
          })
        }
      };

    case 'scatter':
      return {
        ...baseOptions,
        scales: {
          x: {
            title: {
              display: true,
              text: config.xMetric || 'X Metric'
            }
          },
          y: {
            title: {
              display: true,
              text: config.yMetric || 'Y Metric'
            }
          }
        }
      };

    case 'line':
      return {
        ...baseOptions,
        scales: {
          x: {
            title: {
              display: true,
              text: config.categorical || 'Category'
            }
          },
          y: {
            title: {
              display: true,
              text: config.lineMetric || 'Metric'
            }
          }
        }
      };

    default:
      return baseOptions;
  }
};

const getChartTitle = (config: ChartConfiguration): string => {
  switch (config.chartType) {
    case 'bar':
      const metrics = [config.metric1, config.metric2].filter(Boolean).join(' & ');
      return `${metrics} by Model`;
    case 'scatter':
      return `${config.xMetric} vs ${config.yMetric}`;
    case 'line':
      return `${config.lineMetric} by ${config.categorical} (per Model)`;
    default:
      return 'Chart';
  }
};
