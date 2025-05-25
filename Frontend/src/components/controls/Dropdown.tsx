import { Disclosure, DisclosureButton, DisclosurePanel, Transition } from '@headlessui/react';
import clsx from 'clsx';
import { Icon } from '@iconify/react';
import { ReactNode } from 'react';

/**
 * Props interface for the Dropdown component.
 * @interface DropdownProps
 */
interface DropdownProps {
  /**
   * The title/label to display on the disclosure button
   */
  title: string;

  /**
   * The content to display when the disclosure is open
   */
  children: ReactNode;

  /**
   * Optional default open state
   * @default false
   */
  defaultOpen?: boolean;

  /**
   * If true, the disclosure will take up the full width of its container
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Size variant for the disclosure element
   * @default 'md'
   */
  sizeVariant?: 'xs' | 'sm' | 'md' | 'lg';

  /**
   * Style variant for the disclosure element
   * @default 'default'
   */
  variant?: 'default' | 'minimal';

  /**
   * Additional CSS classes for the container
   */
  className?: string;

  /**
   * Additional CSS classes for the button
   */
  buttonClassName?: string;

  /**
   * Additional CSS classes for the panel
   */
  panelClassName?: string;
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
  default: 'bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600',
  minimal: 'bg-transparent dark:bg-transparent border-0'
};

/**
 * A styled disclosure component that expands/collapses content, styled to match other form controls.
 *
 * @component
 * @param {DropdownProps} props - The component props
 * @returns {JSX.Element} A styled disclosure component
 *
 * @example
 * // Basic usage
 * <Dropdown title="Advanced Options">
 *   <div className="p-4">
 *     <p>Advanced content goes here...</p>
 *   </div>
 * </Dropdown>
 */
export default function Dropdown({
  title,
  children,
  defaultOpen = false,
  fullWidth = false,
  sizeVariant = 'md',
  variant = 'default',
  className,
  buttonClassName,
  panelClassName
}: DropdownProps) {
  return (
    <div className={clsx('my-2 mx-1', { 'w-full': fullWidth }, className)}>
      <Disclosure defaultOpen={defaultOpen}>
        {({ open }) => (
          <>
            <DisclosureButton
              className={clsx(
                // Base styles
                'flex justify-between w-full rounded-xl text-gray-800 dark:text-gray-200',
                'focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-500',
                'text-left font-medium',

                // Size styles
                sizeStyles[sizeVariant],

                // Variant styles
                variantStyles[variant],

                // Custom button class
                buttonClassName
              )}
            >
              <span>{title}</span>
              <Icon
                icon={open ? 'material-symbols:arrow-drop-up' : 'material-symbols:arrow-drop-down'}
              />
            </DisclosureButton>
            <Transition
              enter="transition duration-100 ease-out"
              enterFrom="transform scale-95 opacity-0"
              enterTo="transform scale-100 opacity-100"
              leave="transition duration-75 ease-out"
              leaveFrom="transform scale-100 opacity-100"
              leaveTo="transform scale-95 opacity-0"
            >
              <DisclosurePanel
                className={clsx(
                  'mt-2 rounded-xl bg-gray-100 dark:bg-gray-800 p-3',
                  'border border-gray-300 dark:border-gray-600',
                  panelClassName
                )}
              >
                {children}
              </DisclosurePanel>
            </Transition>
          </>
        )}
      </Disclosure>
    </div>
  );
}
