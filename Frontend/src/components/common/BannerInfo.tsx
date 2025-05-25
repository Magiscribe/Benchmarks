import React from 'react';
import clsx from 'clsx';

interface BannerProps {
  title: string;
  subtitle?: string;
  className?: string;
  gradient?: 'blue' | 'purple' | 'green';
  children?: React.ReactNode;
}

export const Banner = ({
  title,
  subtitle,
  className,
  gradient = 'blue',
  children
}: BannerProps) => {
  const gradientClasses = {
    blue: 'from-blue-600 to-blue-800',
    purple: 'from-purple-600 to-indigo-800',
    green: 'from-emerald-500 to-teal-700'
  };

  return (
    <div
      className={clsx(
        'w-full py-12 px-6 text-white bg-gradient-to-r rounded-lg mb-8 shadow-lg',
        gradientClasses[gradient],
        className
      )}
    >
      <h1 className="text-3xl font-bold mb-2">{title}</h1>
      {subtitle && <p className="text-xl opacity-90 mb-6">{subtitle}</p>}
      {children}
    </div>
  );
};
