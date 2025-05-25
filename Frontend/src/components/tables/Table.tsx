import Button from '@/components/controls/Button';
import Container from '@/components/layouts/Container';
import Loading from '@/components/Loading';
import { Icon } from '@iconify/react';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  Row,
  Table,
  useReactTable
} from '@tanstack/react-table';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

/**
 * Props for the DataTable component
 * @template T The type of data being displayed in the table
 */
interface DataTableProps<T> {
  /** Array of data items to be displayed in the table */
  data?: T[];
  /** Column definitions for the table */
  columns: ColumnDef<T>[];
  /** Handler for row click events */
  onRowClick?: (row: Row<T>) => void;
  /** Function that returns custom class names for rows */
  rowClassName?: (row: Row<T>) => string;
  /** Whether the table is in a loading state */
  isLoading?: boolean;
  /** Number of items to display per page */
  pageSize?: number;
  /** Total number of pages available */
  pageCount?: number;
  /** Current active page (zero-indexed) */
  currentPage?: number;
  /** Handler for page change events */
  onPageChange?: (page: number) => void;
  /** Current sort state */
  sort?: { column: string; direction: 'asc' | 'desc' };
  /** Handler for sort change events */
  onSort?: (sort: { column: string; direction: 'asc' | 'desc' }) => void;
}

/**
 * Represents the sort state for a column
 */
type SortState = {
  /** Column ID being sorted */
  column: string;
  /** Sort direction */
  direction: 'asc' | 'desc';
};

/**
 * Renders the header section of the table with sorting capabilities
 * @template T The type of data being displayed in the table
 * @param props Component props
 * @returns Table header component
 */
function TableHeader<T>({
  table,
  sort,
  onSort
}: {
  /** The table instance */
  table: Table<T>;
  /** Current sort state */
  sort?: SortState;
  /** Handler for sort change events */
  onSort?: (sort: SortState) => void;
}) {
  return (
    <thead>
      {table.getHeaderGroups().map((headerGroup) => (
        <tr key={headerGroup.id}>
          {headerGroup.headers.map((header) => (
            <th
              key={header.id}
              className={clsx(
                'h-12 px-4 text-left align-middle font-medium',
                'text-gray-700 dark:text-gray-300',
                header.column.getCanSort() &&
                  header.column.columnDef.enableSorting &&
                  'cursor-pointer select-none hover:text-blue-600 dark:hover:text-blue-400'
              )}
              onClick={
                header.column.getCanSort() && header.column.columnDef.enableSorting
                  ? () => {
                      const newDirection =
                        sort?.column !== header.column.id
                          ? 'asc'
                          : sort.direction === 'asc'
                            ? 'desc'
                            : 'asc';
                      onSort?.({
                        column: header.column.id,
                        direction: newDirection
                      });
                    }
                  : undefined
              }
            >
              <div className="flex items-center space-x-2">
                <span>
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </span>
                {header.column.getCanSort() && header.column.columnDef.enableSorting && (
                  <Icon
                    icon={
                      sort?.column !== header.column.id
                        ? 'material-symbols:arrow-range-rounded'
                        : sort.direction === 'asc'
                          ? 'material-symbols:arrow-upward-rounded'
                          : 'material-symbols:arrow-downward-rounded'
                    }
                  />
                )}
              </div>
            </th>
          ))}
        </tr>
      ))}
    </thead>
  );
}

/**
 * Renders a loading overlay that appears on top of the table when loading
 * @returns Loading overlay component
 */
function LoadingOverlay() {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-gray-800/50 z-10">
      <Loading />
    </div>
  );
}

/**
 * Renders the body section of the table with support for loading states and empty data
 * @template T The type of data being displayed in the table
 * @param props Component props
 * @returns Table body component
 */
function TableBody<T>({
  table,
  columns,
  onRowClick,
  rowClassName
}: {
  /** The table instance */
  table: Table<T>;
  /** Column definitions for the table */
  columns: ColumnDef<T>[];
  /** Handler for row click events */
  onRowClick?: (row: Row<T>) => void;
  /** Function that returns custom class names for rows */
  rowClassName?: (row: Row<T>) => string;
}) {
  const { t } = useTranslation();

  if (!table.getRowModel().rows?.length) {
    return (
      <tbody>
        <tr>
          <td
            colSpan={columns.length}
            className="h-24 text-center text-gray-600 dark:text-gray-300"
          >
            {t('common.table.noResults')}
          </td>
        </tr>
      </tbody>
    );
  }

  return (
    <tbody>
      {table.getRowModel().rows.map((row) => (
        <tr
          key={row.id}
          className={clsx('hover:bg-blue-200 dark:hover:bg-gray-700/50', rowClassName?.(row))}
          onClick={() => onRowClick?.(row)}
        >
          {row.getVisibleCells().map((cell) => (
            <td key={cell.id} className="p-4 text-gray-600 dark:text-gray-300">
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );
}

/**
 * Renders the pagination controls for the table
 * @param props Component props
 * @returns Pagination component or null if pagination is not needed
 */
function TablePagination({
  currentPage,
  pageCount,
  onPageChange,
  dataEmpty
}: {
  /** Current active page (zero-indexed) */
  currentPage: number;
  /** Total number of pages available */
  pageCount: number;
  /** Handler for page change events */
  onPageChange?: (page: number) => void;
  /** Whether the data array is empty */
  dataEmpty: boolean;
}) {
  const { t } = useTranslation();

  if (pageCount <= 1) return null;

  return (
    <div
      className={clsx(
        'flex items-center justify-between px-4 py-3',
        'border-t border-gray-300 dark:border-gray-700'
      )}
    >
      <div className="text-sm text-gray-600 dark:text-gray-400">
        {t('common.table.pagination.page', { current: currentPage + 1, total: pageCount })}
      </div>
      <div className="flex items-center space-x-2">
        <Button
          variant="transparent"
          size="sm"
          onClick={() => onPageChange?.(currentPage - 1)}
          disabled={currentPage === 0}
        >
          {t('common.table.pagination.previous')}
        </Button>
        <Button
          variant="transparent"
          size="sm"
          onClick={() => onPageChange?.(currentPage + 1)}
          disabled={currentPage >= pageCount - 1 || dataEmpty}
        >
          {t('common.table.pagination.next')}
        </Button>
      </div>
    </div>
  );
}

/**
 * A reusable data table component with support for sorting, pagination, and row selection
 * @template T The type of data being displayed in the table
 * @param props Component props
 * @returns DataTable component
 */
export function DataTable<T extends object>({
  data = [],
  columns,
  onRowClick,
  rowClassName,
  isLoading,
  pageSize = 10,
  pageCount = 1,
  currentPage = 0,
  onPageChange,
  sort,
  onSort
}: DataTableProps<T>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    pageCount,
    state: {
      pagination: {
        pageIndex: currentPage,
        pageSize
      },
      sorting: sort ? [{ id: sort.column, desc: sort.direction === 'desc' }] : []
    },
    onPaginationChange: (updater) => {
      if (typeof updater === 'function') {
        const newState = updater({ pageIndex: currentPage, pageSize });
        onPageChange?.(newState.pageIndex);
      }
    },
    manualPagination: true,
    enableSorting: true,
    manualSorting: true
  });

  return (
    <Container>
      <div className="relative">
        {isLoading && <LoadingOverlay />}
        <table className="w-full caption-bottom text-sm">
          <TableHeader table={table} sort={sort} onSort={onSort} />
          <TableBody
            table={table}
            columns={columns}
            onRowClick={onRowClick}
            rowClassName={rowClassName}
          />
        </table>
      </div>

      <TablePagination
        currentPage={currentPage}
        pageCount={pageCount}
        onPageChange={onPageChange}
        dataEmpty={data.length === 0}
      />
    </Container>
  );
}
