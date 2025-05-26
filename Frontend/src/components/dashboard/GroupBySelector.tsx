import { FilterColumn } from '@/types/dashboard';

interface GroupBySelectorProps {
  availableGroupBy: FilterColumn[];
  selectedGroupBy: string[];
  onGroupBySelect: (columnName: string) => void;
  onSelectAll: () => void;
  onSelectNone: () => void;
}

export default function GroupBySelector({
  availableGroupBy,
  selectedGroupBy,
  onGroupBySelect,
  onSelectAll,
  onSelectNone
}: GroupBySelectorProps) {
  if (availableGroupBy.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Group By
        </h2>
        <div className="space-x-2">
          <button
            onClick={onSelectAll}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Select All
          </button>
          <button
            onClick={onSelectNone}
            className="px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Select None
          </button>
        </div>
      </div>
      <div className="space-y-2">
        {availableGroupBy.map((column) => (
          <div
            key={column.name}
            className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded"
          >
            <input
              type="checkbox"
              id={`group-by-${column.name}`}
              checked={selectedGroupBy.includes(column.name)}
              onChange={() => onGroupBySelect(column.name)}
              className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
            />
            <label
              htmlFor={`group-by-${column.name}`}
              className="flex-1 text-sm text-gray-700 dark:text-gray-300"
            >
              <div className="font-medium">{column.name}</div>
              <div className="text-gray-500 dark:text-gray-400 text-xs">
                {column.description}
              </div>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
} 