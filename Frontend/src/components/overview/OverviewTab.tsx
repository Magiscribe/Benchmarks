import React, { useState, useEffect } from 'react';
import { Benchmark, Metric } from '../../types/dashboard';

interface OverviewTabProps {
  benchmarks: Benchmark[];
  selectedBenchmark?: string;
  onBenchmarkChange?: (benchmarkId: string) => void;
}

interface VisualizationData {
  benchmark_id: string;
  model: string;
  asset_id: string;
  visualization_image: string;
  metadata: {
    ground_truth: any;
    predictions: any;
    image_dimensions: {
      width: number;
      height: number;
    };
  };
}

const API_BASE = `${import.meta.env.VITE_API_URL}`;

export const OverviewTab: React.FC<OverviewTabProps> = ({ 
  benchmarks, 
  selectedBenchmark: propSelectedBenchmark, 
  onBenchmarkChange 
}) => {
  const [selectedBenchmark, setSelectedBenchmark] = useState<string>(propSelectedBenchmark || (benchmarks.length > 0 ? benchmarks[0].id : ''));  const [selectedModel, setSelectedModel] = useState<string>('');  const [selectedAssetId, setSelectedAssetId] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  const [availableMetrics, setAvailableMetrics] = useState<Metric[]>([]);
  const [selectedMetricForView, setSelectedMetricForView] = useState<string>('');
  const [visualizationData, setVisualizationData] = useState<VisualizationData | null>(null);const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [assetsLoading, setAssetsLoading] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  // Update local state when prop changes
  useEffect(() => {
    if (propSelectedBenchmark && propSelectedBenchmark !== selectedBenchmark) {
      setSelectedBenchmark(propSelectedBenchmark);
    } else if (!propSelectedBenchmark && benchmarks.length > 0 && !selectedBenchmark) {
      // Auto-select first benchmark if none is selected and benchmarks are available
      const firstBenchmark = benchmarks[0].id;
      setSelectedBenchmark(firstBenchmark);
      if (onBenchmarkChange) {
        onBenchmarkChange(firstBenchmark);
      }
    }
  }, [propSelectedBenchmark, benchmarks]);

  // Handle benchmark change
  const handleBenchmarkChange = (benchmarkId: string) => {
    setSelectedBenchmark(benchmarkId);
    if (onBenchmarkChange) {
      onBenchmarkChange(benchmarkId);
    }
  };  // Fetch available models when benchmark changes
  useEffect(() => {
    if (selectedBenchmark) {
      fetchAvailableModels(selectedBenchmark);
      fetchAvailableAssets(selectedBenchmark);
      fetchAvailableMetrics(selectedBenchmark);
    } else {
      setAvailableModels([]);
      setAvailableAssets([]);
      setAvailableMetrics([]);
    }    // Reset selections when benchmark changes
    setSelectedModel('');
    setSelectedAssetId('');
    setSelectedMetricForView('');
    setVisualizationData(null);
    setError(null); // Clear any previous errors
    setRetryCount(0); // Reset retry count
  }, [selectedBenchmark]);

  const fetchAvailableModels = async (benchmark: string) => {
    setModelsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/benchmarks/${benchmark}/models`);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data);
        // Auto-select first model if available
        if (data.length > 0) {
          setSelectedModel(data[0]);
        }
      } else {
        console.error('Failed to fetch models:', response.status);
        setAvailableModels([]);
      }
    } catch (err) {
      console.error('Error fetching models:', err);
      setAvailableModels([]);
    } finally {
      setModelsLoading(false);
    }
  };

  const fetchAvailableAssets = async (benchmark: string) => {
    setAssetsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/benchmarks/${benchmark}/assets`);
      if (response.ok) {
        const data = await response.json();
        setAvailableAssets(data);
        // Auto-select first asset if available
        if (data.length > 0) {
          setSelectedAssetId(data[0]);
        }
      } else {
        console.error('Failed to fetch assets:', response.status);
        setAvailableAssets([]);
      }
    } catch (err) {
      console.error('Error fetching assets:', err);
      setAvailableAssets([]);    } finally {
      setAssetsLoading(false);
    }
  };

  const fetchAvailableMetrics = async (benchmark: string) => {
    try {
      const response = await fetch(`${API_BASE}/benchmarks/${benchmark}/metrics`);
      if (response.ok) {
        const data = await response.json();
        setAvailableMetrics(data);
      } else {
        console.error('Failed to fetch metrics:', response.status);
        setAvailableMetrics([]);
      }
    } catch (err) {
      console.error('Error fetching metrics:', err);
      setAvailableMetrics([]);
    }
  };

  const fetchVisualization = async (isRetry = false) => {
    if (!selectedBenchmark || !selectedModel || !selectedAssetId) {
      setError('Please select benchmark, model, and asset ID');
      return;
    }

    // Don't fetch if we're still loading models or assets
    if (modelsLoading || assetsLoading) {
      return;
    }

    setLoading(true);
    if (!isRetry) {
      setError(null);
      setRetryCount(0);
    }

    try {
      const response = await fetch(`${API_BASE}/benchmarks/${selectedBenchmark}/visualizations/${selectedModel}/${selectedAssetId}`);
      
      if (response.ok) {
        const data = await response.json();
        setVisualizationData(data);
        setError(null); // Clear any previous errors on success
        setRetryCount(0);
      } else {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `Failed to fetch visualization (${response.status})`;
        console.error('Visualization fetch failed:', response.status, errorMessage);
        
        // Auto-retry once after a short delay if it's an asset not found error
        if (response.status === 404 && retryCount === 0 && !isRetry) {
          console.log('Asset not found, retrying in 1 second...');
          setRetryCount(1);
          setTimeout(() => {
            fetchVisualization(true);
          }, 1000);
          return;
        }
        
        setError(errorMessage);
      }
    } catch (err) {
      console.error('Error fetching visualization:', err);
      setError('An error occurred while fetching the visualization');
    } finally {
      setLoading(false);
    }
  };
  // Auto-fetch visualization when all selections are made and assets/models are loaded
  useEffect(() => {
    // Only auto-fetch if we have all required selections and aren't loading anything
    if (selectedBenchmark && selectedModel && selectedAssetId && !modelsLoading && !assetsLoading) {
      // Add a small delay to ensure all state updates have propagated
      const timer = setTimeout(() => {
        fetchVisualization();
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [selectedBenchmark, selectedModel, selectedAssetId, modelsLoading, assetsLoading, retryCount]);return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Controls */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
                  Benchmark <span className="text-red-500">*</span>
                </label>                <select
                  value={selectedBenchmark}
                  onChange={(e) => handleBenchmarkChange(e.target.value)}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
                >
                  {benchmarks.map(benchmark => (
                    <option key={benchmark.id} value={benchmark.id}>
                      {benchmark.name}
                    </option>
                  ))}
                </select>
                {selectedBenchmark && (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {benchmarks.find(b => b.id === selectedBenchmark)?.description}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
                  Model <span className="text-red-500">*</span>
                </label>                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  disabled={!selectedBenchmark || modelsLoading}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none disabled:opacity-50"
                >
                  {modelsLoading ? (
                    <option value="">Loading models...</option>
                  ) : (
                    <>
                      {availableModels.length === 0 && <option value="">No models available</option>}
                      {availableModels.map(model => (
                        <option key={model} value={model}>
                          {model.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </option>
                      ))}
                    </>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
                  Asset ID <span className="text-red-500">*</span>
                </label>                <select
                  value={selectedAssetId}
                  onChange={(e) => setSelectedAssetId(e.target.value)}
                  disabled={!selectedBenchmark || assetsLoading}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none disabled:opacity-50"
                >
                  {assetsLoading ? (
                    <option value="">Loading assets...</option>
                  ) : (
                    <>
                      {availableAssets.length === 0 && <option value="">No assets available</option>}
                      {availableAssets.map(asset => (
                        <option key={asset} value={asset}>
                          {asset}
                        </option>
                      ))}
                    </>
                  )}
                </select>
              </div>              {/* Error Display */}
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-red-800 dark:text-red-300">Error</h4>
                      <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
                    </div>
                    <button
                      onClick={() => fetchVisualization()}
                      disabled={loading}
                      className="ml-3 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:bg-red-400 disabled:cursor-not-allowed"
                    >
                      Retry
                    </button>
                  </div>
                </div>
              )}

              {/* Loading indicator for models/assets */}
              {(modelsLoading || assetsLoading) && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent text-blue-600 rounded-full mr-2"></div>
                    <p className="text-sm text-blue-700 dark:text-blue-400">
                      Loading {modelsLoading && assetsLoading ? 'models and assets' : modelsLoading ? 'models' : 'assets'}...
                    </p>                  </div>
                </div>
              )}              {/* Available Metrics */}
              {selectedBenchmark && availableMetrics.length > 0 && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
                      Available Metrics
                    </label>
                    <select
                      value={selectedMetricForView}
                      onChange={(e) => setSelectedMetricForView(e.target.value)}
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
                    >
                      <option value="">View available metrics...</option>
                      {availableMetrics.map((metric) => (
                        <option key={metric.id} value={metric.id}>
                          {metric.name}
                        </option>
                      ))}
                    </select>
                    {selectedMetricForView && (
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {availableMetrics.find(m => m.id === selectedMetricForView)?.description}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Visualization */}
        <div className="lg:col-span-2">          {/* Loading State */}
          {loading && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-8 text-center">
              <div className="animate-spin inline-block w-6 h-6 border-2 border-current border-t-transparent text-blue-600 rounded-full" role="status" aria-label="loading">
                <span className="sr-only">Loading...</span>
              </div>
              <p className="mt-2 text-blue-700 dark:text-blue-300">
                {retryCount > 0 ? 'Retrying visualization...' : 'Loading visualization...'}
              </p>
              {retryCount > 0 && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Sometimes assets need a moment to become available
                </p>
              )}
            </div>
          )}

          {/* Visualization Display */}
          {visualizationData && !loading && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex justify-center">
                <img
                  src={`data:image/png;base64,${visualizationData.visualization_image}`}
                  alt="Model prediction visualization"
                  className="max-w-full h-auto rounded-lg shadow border border-gray-200 dark:border-gray-700"
                  style={{ maxHeight: '600px' }}
                />
              </div>
            </div>
          )}          {/* Placeholder */}
          {!visualizationData && !loading && !error && (
            <div className="bg-gray-50 dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
              {modelsLoading || assetsLoading ? (
                <>
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Loading Options
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Please wait while we load the available {modelsLoading && assetsLoading ? 'models and assets' : modelsLoading ? 'models' : 'assets'}...
                  </p>
                </>
              ) : !selectedModel || !selectedAssetId ? (
                <>
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Ready to Visualize
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Select a model and asset to see the visualization.
                  </p>
                </>
              ) : (
                <>
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Loading Visualization
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Preparing visualization for {selectedModel} on asset {selectedAssetId}...
                  </p>
                </>
              )}
            </div>
          )}
        </div>      </div>
    </div>
  );
};
