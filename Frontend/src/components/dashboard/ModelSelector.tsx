interface ModelSelectorProps {
  availableModels: string[];
  selectedModels: string[];
  onModelSelect: (model: string) => void;
  onSelectAll: () => void;
  onSelectNone: () => void;
}

export default function ModelSelector({ 
  availableModels, 
  selectedModels, 
  onModelSelect, 
  onSelectAll, 
  onSelectNone 
}: ModelSelectorProps) {
  if (availableModels.length === 0) {
    return (
      <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
        <p className="text-sm text-yellow-700 dark:text-yellow-300">
          No models found for this test type. Check if results CSV exists.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-md font-medium text-gray-900 dark:text-white">
          Available Models ({availableModels.length})
        </h4>
        <div className="space-x-2">
          <button
            onClick={onSelectAll}
            className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Select All
          </button>
          <button
            onClick={onSelectNone}
            className="text-xs px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Select None
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-40 overflow-y-auto">
        {availableModels.map((model) => (
          <label key={model} className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={selectedModels.includes(model)}
              onChange={() => onModelSelect(model)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-gray-700 dark:text-gray-300 truncate">
              {model}
            </span>
          </label>
        ))}
      </div>
      
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Selected: {selectedModels.length} of {availableModels.length} models
      </p>
    </div>
  );
}
