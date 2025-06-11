// filepath: c:\Users\JacobSchwartz\Documents\Magiscribe\Benchmarks\Frontend\src\types\charts.ts

export type ChartType = 'bar' | 'scatter' | 'line';

export interface ChartConfiguration {
  chartType: ChartType;
  // Bar chart: Models on X, 1-2 metrics on Y
  metric1?: string;
  metric2?: string;
  // Scatter chart: Metric vs Metric
  xMetric?: string;
  yMetric?: string;
  // Line chart: Categorical on X, Metric on Y (per model)
  categorical?: string;
  lineMetric?: string;
  // Parameter values for metrics
  parameterValues?: Record<string, Record<string, any>>;
}

export interface ChartValidation {
  isValid: boolean;
  errors: string[];
}

export interface ChartDataPoint {
  x: string | number;
  y: number;
  model?: string;
  metric?: string;
  value?: number;
}

export interface ChartDataset {
  label: string;
  data: ChartDataPoint[];
  borderColor?: string;
  backgroundColor?: string;
  yAxisID?: string;
}

// Flattened result for easier chart processing
export interface FlatResult {
  model: string;
  metrics: Record<string, number>;
  groupValues?: Record<string, string>;
}
