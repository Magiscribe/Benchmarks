import { FilterColumn } from '../../types/dashboard';

interface FilterSelectorProps {
  availableFilters: FilterColumn[];
  filterValues: Record<string, string[]>;
  selectedFilterValues: Record<string, string[]>;
  onFilterValueSelect: (filterName: string, value: string) => void;
  onSelectAllValues: (filterName: string) => void;
  onSelectNoValues: (filterName: string) => void;
}

export default function FilterSelector({
  availableFilters,
  filterValues,
  selectedFilterValues,
  onFilterValueSelect,
  onSelectAllValues,
  onSelectNoValues
}: FilterSelectorProps) {
  if (availableFilters.length === 0) {
    return (
      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900/20 rounded-lg">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No filterable columns found for this test type.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
      <h4 className="text-md font-medium text-gray-900 dark:text-white mb-3">
        Available Filters ({availableFilters.length})
      </h4>
      
      <div className="space-y-4">
        {availableFilters.map((filter) => (
          <div 
            key={filter.name} 
            className="p-3 bg-white dark:bg-gray-800 rounded border"
          >
            <div className="flex items-center justify-between mb-2">
              <div>
                <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                  {filter.name}
                </h5>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {filter.description} ({filter.type})
                </p>
              </div>
              <div className="space-x-2">
                <button
                  onClick={() => onSelectAllValues(filter.name)}
                  className="text-xs px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  All
                </button>
                <button
                  onClick={() => onSelectNoValues(filter.name)}
                  className="text-xs px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  None
                </button>
              </div>
            </div>
            
            {filterValues[filter.name] && filterValues[filter.name].length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-32 overflow-y-auto">
                {filterValues[filter.name].map((value) => (
                  <label key={value} className="flex items-center space-x-2 text-xs">
                    <input
                      type="checkbox"
                      checked={selectedFilterValues[filter.name]?.includes(value) || false}
                      onChange={() => onFilterValueSelect(filter.name, value)}
                      className="h-3 w-3 text-green-600 border-gray-300 rounded focus:ring-green-500"
                    />
                    <span className="text-gray-700 dark:text-gray-300 truncate">
                      {value}
                    </span>
                  </label>
                ))}
              </div>
            )}
            
            {filterValues[filter.name] && filterValues[filter.name].length === 0 && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                No values available for this filter.
              </p>
            )}
            
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Selected: {selectedFilterValues[filter.name]?.length || 0} of {filterValues[filter.name]?.length || 0} values
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
