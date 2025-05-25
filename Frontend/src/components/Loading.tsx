import clsx from 'clsx';

/**
 * Loading spinner component with dark mode support
 * @param props Component props
 * @returns Loading spinner component
 */
export default function Loading({ className }: { className?: string } = {}) {
  return (
    <div
      className={clsx(
        'w-5 h-5 border-2 border-t-transparent rounded-full animate-spin mx-auto',
        'border-blue-500 dark:border-blue-400',
        className
      )}
    />
  );
}
