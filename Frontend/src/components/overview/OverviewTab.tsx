import React, { useState, useEffect } from 'react';
import { Benchmark } from '../../types/dashboard';

interface OverviewTabProps {
  benchmarks: Benchmark[];
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

export const OverviewTab: React.FC<OverviewTabProps> = ({ benchmarks }) => {
  const [selectedBenchmark, setselectedBenchmark] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [selectedAssetId, setSelectedAssetId] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  const [visualization, setVisualization] = useState<VisualizationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const models = [
    'claude-3-5-haiku',
    'claude-3-5-sonnet', 
    'gpt-4o',
    'gemini-2.5-pro',
    'claude-4-sonnet'
  ];

  // Fetch available models when test type changes
  useEffect(() => {
    if (selectedBenchmark) {
      fetchAvailableModels(selectedBenchmark);
      fetchAvailableAssets(selectedBenchmark);
    } else {
      setAvailableModels([]);
      setAvailableAssets([]);
    }
    setSelectedModel('');
    setSelectedAssetId('');
    setVisualization(null);
  }, [selectedBenchmark]);

  const fetchAvailableModels = async (benchmark: string) => {
    try {
      const response = await fetch(`${API_BASE}/benchmarks/${benchmark}/models`);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data);
        // Auto-select first model if available
        if (data.length > 0) {
          setSelectedModel(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch available models:', err);
      // Fallback to predefined models
      setAvailableModels(models);
      setSelectedModel(models[0]);
    }
  };

  const fetchAvailableAssets = async (benchmark: string) => {
    try {
      const response = await fetch(`${API_BASE}/benchmarks/${benchmark}/assets`);
      if (response.ok) {
        const data = await response.json();
        setAvailableAssets(data);
        // Auto-select first asset if available
        if (data.length > 0) {
          setSelectedAssetId(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch available assets:', err);
      // Fallback placeholder assets
      const fallbackAssets = [
        'coordinate_grid_1748135594214',
        'coordinate_grid_1748135594245', 
        'coordinate_grid_1748135594251',
        'Arial_1747615332631'
      ];
      setAvailableAssets(fallbackAssets);
      setSelectedAssetId(fallbackAssets[0]);
    }
  };

  const generateVisualization = async () => {
    if (!selectedBenchmark || !selectedModel || !selectedAssetId) {
      setError('Please select test type, model, and asset ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/benchmarks/${selectedBenchmark}/visualizations/${selectedModel}/${selectedAssetId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setVisualization(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to load visualization: ${errorMessage}`);
      console.error('Visualization error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate when all selections are made
  useEffect(() => {
    if (selectedBenchmark && selectedModel && selectedAssetId) {
      generateVisualization();
    }
  }, [selectedBenchmark, selectedModel, selectedAssetId]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Column - Description and Controls */}
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            🎯 Visualization Overview
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Test the visualization endpoint that overlays model predictions on test images. 
            Select a test type, model, and asset to see how the model performs on specific examples.
          </p>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Test Type <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedBenchmark}
              onChange={(e) => setselectedBenchmark(e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none"
            >
              <option value="">Select test type...</option>              {benchmarks.map(benchmark => (
                <option key={benchmark.id} value={benchmark.id}>
                  {benchmark.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Model <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={!selectedBenchmark}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none disabled:opacity-50"
            >
              <option value="">Select model...</option>
              {availableModels.map(model => (
                <option key={model} value={model}>
                  {model.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Asset ID <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedAssetId}
              onChange={(e) => setSelectedAssetId(e.target.value)}
              disabled={!selectedBenchmark}
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none disabled:opacity-50"
            >
              <option value="">Select asset...</option>
              {availableAssets.map(asset => (
                <option key={asset} value={asset}>
                  {asset}
                </option>
              ))}
            </select>          </div>
        </div>
      </div>

      {/* Right Column - Visualization Display */}
      <div className="space-y-4">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-300">❌ Error</h3>
            <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-2">
              Make sure the backend is running on <code>http://localhost:8000</code>
            </p>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-gray-600 dark:text-gray-400">🔄 Generating visualization...</p>
            </div>
          </div>
        )}        {visualization && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 flex justify-center">
              <div className="w-full aspect-square max-w-full">
                <img 
                  src={`data:image/png;base64,${visualization.visualization_image}`}
                  alt="Visualization"
                  className="w-full h-full object-contain rounded border border-gray-200 dark:border-gray-600"
                />
              </div>
            </div>
          </div>
        )}

        {!loading && !error && !visualization && (
          <div className="flex items-center justify-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                Ready to Generate Visualization
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Select a test type, model, and asset to see the visualization.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
