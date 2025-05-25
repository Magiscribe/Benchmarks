import clsx from 'clsx';
import { TextareaHTMLAttributes, useEffect, useRef } from 'react';

/**
 * Props interface for the TextArea component.
 * @interface TextAreaProps
 * @extends {TextareaHTMLAttributes<HTMLTextAreaElement>} - Inherits standard HTML textarea attributes
 */
interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  /**
   * If true, the textarea will take up the full width of its container
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Optional label text to display above the textarea
   */
  label?: string;

  /**
   * If true, the textarea will automatically adjust its height based on content
   * @default true
   */
  autoSize?: boolean;

  /**
   * Minimum number of rows to display
   * @default 3
   */
  minRows?: number;

  /**
   * Maximum number of rows before scrolling
   * @default 10
   */
  maxRows?: number;
}

/**
 * A styled textarea component that supports both light and dark themes and auto-resizes based on content.
 *
 * @component
 * @param {TextAreaProps} props - The component props
 * @param {boolean} [props.fullWidth=false] - Whether the textarea should take full width
 * @param {string} [props.className] - Additional CSS classes to apply
 * @param {string} [props.label] - Optional label text
 * @param {boolean} [props.autoSize=true] - Whether to auto-resize based on content
 * @param {number} [props.minRows=3] - Minimum number of rows
 * @param {number} [props.maxRows=10] - Maximum number of rows before scrolling
 * @returns {JSX.Element} A styled textarea element with auto-sizing capabilities
 *
 * @example
 * // Basic usage
 * <TextArea placeholder="Enter text here" />
 *
 * @example
 * // Full width textarea with label and custom rows
 * <TextArea label="Description" fullWidth minRows={5} placeholder="Write a description" />
 */
export default function TextArea({
  fullWidth = false,
  className,
  label,
  autoSize = true,
  minRows = 3,
  maxRows = 10,
  onChange,
  value,
  defaultValue,
  ...props
}: TextAreaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Function to adjust the height of the textarea
  const adjustHeight = () => {
    if (!autoSize || !textareaRef.current) return;

    const textarea = textareaRef.current;

    // Reset height to calculate the proper scrollHeight
    textarea.style.height = 'auto';

    // Calculate line height from computed styles
    const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight) || 20;

    // Calculate min and max heights
    const minHeight = minRows * lineHeight;
    const maxHeight = maxRows * lineHeight;

    // Set the height based on content, within min/max constraints
    const newHeight = Math.max(minHeight, Math.min(textarea.scrollHeight, maxHeight));
    textarea.style.height = `${newHeight}px`;

    // Add scrollbar if content exceeds max height
    textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
  };

  // Adjust height on mount and when content changes
  useEffect(() => {
    adjustHeight();
  }, [value, defaultValue]);

  // Custom onChange handler to adjust height after content changes
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (onChange) {
      onChange(e);
    }
    adjustHeight();
  };

  return (
    <div className="flex flex-col">
      {label && <label className="block text-sm font-medium mb-1">{label}</label>}
      <textarea
        ref={textareaRef}
        className={clsx(
          // Light theme styles
          'bg-white text-gray-800 placeholder:text-gray-500 focus:ring-blue-400',
          // Dark theme styles
          'dark:bg-gray-700 dark:text-gray-200 dark:placeholder:text-gray-400 dark:focus:ring-blue-500',
          // Common styles
          'border-0 rounded-xl p-3 my-2 focus:ring-2 focus:outline-hidden resize-none',
          // Conditional styles
          'disabled:opacity-60',
          {
            'w-full': fullWidth
          },
          className
        )}
        rows={minRows}
        onChange={handleChange}
        value={value}
        defaultValue={defaultValue}
        {...props}
      />
    </div>
  );
}
