// Dashboard-specific types
export interface TestType {
  name: string;
  displayName?: string;
  description: string;
  available: boolean;
}

export interface FilterColumn {
  name: string;
  type: 'identifier' | 'categorical';
  description: string;
}

export interface Metric {
  name: string;
  displayName: string;
  description: string;
}

export interface MetricParameter {
  name: string;
  type: string;
  default: any;
  description: string;
}

export interface ModelResult {
  metric_value: number;
  sample_count: number;
}

export interface GroupedResult {
  model: string;
  group_values: Record<string, string>;
  data: ModelResult;
}

export interface ResultsResponse {
  results: GroupedResult[];
  test_type: string;
  metric: string;
  group_by?: string[];
}

export interface MultiMetricResults {
  [metric: string]: ResultsResponse;
}

export interface ResultsRequest {
  models: string[];
  filters?: Record<string, string[]>;
  parameters?: Record<string, any>;
}
