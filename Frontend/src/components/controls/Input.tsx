import clsx from 'clsx';
import { InputHTMLAttributes } from 'react';

/**
 * Props interface for the Input component.
 * @interface InputProps
 * @extends {InputHTMLAttributes<HTMLInputElement>} - Inherits standard HTML input attributes
 */
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * If true, the input will take up the full width of its container
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Optional label text to display above the input
   */
  label?: string;
}

/**
 * A styled input component that supports both light and dark themes.
 *
 * @component
 * @param {InputProps} props - The component props
 * @param {boolean} [props.fullWidth=false] - Whether the input should take full width
 * @param {string} [props.className] - Additional CSS classes to apply
 * @param {string} [props.label] - Optional label text
 * @returns {JSX.Element} A styled input element with optional label
 *
 * @example
 * // Basic usage
 * <Input placeholder="Enter text here" />
 *
 * @example
 * // Full width input with label
 * <Input label="Email Address" fullWidth type="email" placeholder="Enter your email" />
 */
export default function Input({ fullWidth, className, label, ...props }: InputProps) {
  return (
    <div className="flex flex-col">
      {label && <label className="block text-sm font-medium mb-1">{label}</label>}
      <input
        className={clsx(
          // Light theme styles
          'bg-white text-gray-800 placeholder:text-gray-500 focus:ring-blue-400',
          // Dark theme styles
          'dark:bg-gray-700 dark:text-gray-200 dark:placeholder:text-gray-400 dark:focus:ring-blue-500',
          // Common styles
          'border-0 rounded-xl p-3 my-2 focus:ring-2 focus:outline-hidden',
          // Conditional styles
          'disabled:opacity-60',
          {
            'w-full': fullWidth
          },
          className
        )}
        {...props}
      />
    </div>
  );
}
