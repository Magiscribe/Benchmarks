import { Icon } from '@iconify/react';
import clsx from 'clsx';
import { Children, cloneElement, isValidElement, ReactElement, SelectHTMLAttributes } from 'react';

/**
 * Props interface for the Select component.
 * @interface SelectProps
 * @extends {SelectHTMLAttributes<HTMLSelectElement>} - Inherits standard HTML select attributes
 */
interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  /**
   * If true, the select will take up the full width of its container
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Size variant for the select element
   * @default 'md'
   */
  sizeVariant?: 'xs' | 'sm' | 'md' | 'lg';

  /**
   * Style variant for the select element
   * @default 'default'
   */
  variant?: 'default' | 'minimal';
  
  /**
   * Optional label text to display above the select
   */
  label?: string;
}

// Size-specific styles
const sizeStyles = {
  xs: 'px-2 py-1 text-xs',
  sm: 'px-2.5 py-1.5 text-sm',
  md: 'px-3 py-2 text-base',
  lg: 'px-4 py-2.5 text-lg'
};

// Variant-specific styles
const variantStyles = {
  default: 'bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600',
  minimal: 'bg-transparent dark:bg-transparent border-0'
};

/**
 * A styled select component that supports both light and dark themes using only Tailwind CSS.
 * This version also ensures proper text colors for option elements in dark mode.
 *
 * @component
 * @param {SelectProps} props - The component props
 * @returns {JSX.Element} A styled select element with properly themed options
 */
export default function Select({
  fullWidth,
  className,
  sizeVariant = 'md',
  variant = 'default',
  children,
  label,
  ...props
}: SelectProps) {
  // Apply proper text color classes to option elements
  // This helps with dark mode compatibility
  const styledChildren = Children.map(children, (child) => {
    if (isValidElement(child) && child.type === 'option') {
      return cloneElement(
        child as ReactElement,
        {
          className: clsx(
            'text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-700',
            'hover:bg-gray-100 dark:hover:bg-gray-600',
            (child as ReactElement<HTMLOptionElement & { className?: string }>).props.className
          )
        } as React.HTMLAttributes<HTMLOptionElement>
      );
    }
    return child;
  });

  return (
    <div className={clsx('inline-block', { 'w-full': fullWidth }, className)}>
      {label && <label className="block text-sm font-medium mb-1">{label}</label>}
      <div className="relative inline-block w-full">
        <select
          className={clsx(
            // Base styles
            'appearance-none rounded-xl w-full text-gray-800 dark:text-gray-200',
            'focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-500',

            // Size styles
            sizeStyles[sizeVariant],

            // Variant styles
            variantStyles[variant],

            // Right padding for the dropdown icon
            'pr-8',

            // Option color theming - these don't work perfectly in all browsers
            // but help with some native appearances
            '[&>option]:bg-white [&>option]:dark:bg-gray-700',
            '[&>option]:text-gray-800 [&>option]:dark:text-gray-200'
          )}
          {...props}
        >
          {styledChildren}
        </select>

        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
          <Icon icon="material-symbols:arrow-drop-down" className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
