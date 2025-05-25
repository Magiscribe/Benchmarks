import React, { ReactNode } from 'react';
import clsx from 'clsx';

interface FeatureProps {
  title?: string;
  description?: string;
  icon?: ReactNode;
  className?: string;
  iconClassName?: string;
  children?: ReactNode;
  variant?: 'default' | 'compact' | 'list';
}

export const Feature = ({
  title,
  description,
  icon,
  className,
  iconClassName,
  children,
  variant = 'default'
}: FeatureProps) => {
  // Determine styling based on variant
  const containerClasses = clsx(
    'rounded-lg',
    'bg-gray-50 dark:bg-gray-700',
    variant === 'compact' ? 'p-4' : 'p-6',
    variant !== 'list' && 'shadow-md',
    className
  );

  const titleClasses = clsx('font-bold', variant === 'default' ? 'text-xl mb-2' : 'mb-1');

  // Compact variant with icon has a special layout
  const isCompactWithIcon = variant === 'compact' && icon;

  return (
    <div className={containerClasses}>
      {isCompactWithIcon ? (
        // Compact layout with icon
        <div className="flex items-center">
          <div className={clsx('mr-4', iconClassName)}>{icon}</div>
          <div>
            {title && <h3 className={titleClasses}>{title}</h3>}
            {description && <p>{description}</p>}
          </div>
        </div>
      ) : (
        // Standard layout
        <>
          {icon && <div className={iconClassName}>{icon}</div>}
          {title && <h3 className={titleClasses}>{title}</h3>}
          {description && <p>{description}</p>}
        </>
      )}

      {children}
    </div>
  );
};
