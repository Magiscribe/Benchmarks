// Backend benchmark format
export interface Benchmark {
  id: string;
  name: string;
  description: string;
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



// Results data structures matching backend API contract
export interface ResultItem {
  model: string;
  groupings: string[];
  value: number;
}

export interface ResultsResponse {
  results: ResultItem[];
  metric: string;
}

export interface MultiMetricResults {
  [metric: string]: ResultsResponse;
}

export interface ResultsRequest {
  models: string[];
  filters?: Record<string, string[]>;
}
