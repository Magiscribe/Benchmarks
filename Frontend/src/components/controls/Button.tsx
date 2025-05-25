import clsx from 'clsx';
import { AnchorHTMLAttributes, ButtonHTMLAttributes, ElementType, ReactNode } from 'react';

// Define the polymorphic props pattern
type PolymorphicProps<E extends ElementType = ElementType> = {
  as?: E;
  children?: ReactNode;
  variant?: 'default' | 'danger' | 'secondary' | 'transparent';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
};

// Combine all possible HTML attributes that could be used
type ButtonComponentProps<E extends ElementType> = PolymorphicProps<E> &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, keyof PolymorphicProps> &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, keyof PolymorphicProps>;

// Variant-specific styles
const variantStyles = {
  default: 'bg-blue-600 text-white hover:bg-blue-700',
  danger: 'bg-red-500 text-white hover:bg-red-600',
  secondary: 'bg-gray-600 text-white hover:bg-gray-700',
  transparent:
    'bg-transparent text-gray-800 hover:bg-black/10 dark:text-gray-200 dark:hover:bg-white/10'
};

// Size-specific styles, excluding transparent which has special handling
const sizeStylesPadding = {
  xs: 'px-2 py-1',
  sm: 'px-3 py-1.5',
  md: 'px-4 py-2 t',
  lg: 'px-6 py-3'
};

const sizeStylesText = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg'
};

export default function Button<E extends ElementType = 'button'>({
  as,
  children,
  variant = 'default',
  size = 'md',
  fullWidth,
  className,
  ...props
}: ButtonComponentProps<E>) {
  const Component = as || 'button';
  
  return (
    <Component
      className={clsx(
        'font-semibold p-2 rounded-xl my-2',
        'disabled:opacity-60',
        'transition-colors duration-200',
        variantStyles[variant],
        // Apply text styles to all variants
        sizeStylesText[size],
        // Only apply size styles to non-transparent variants
        variant !== 'transparent' && sizeStylesPadding[size],
        {
          'flex-1': fullWidth,
          'inline-flex items-center justify-center': true, // Ensure good alignment for both buttons and links
        },
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}
