import { motion } from 'motion/react';
import { ReactNode } from 'react';

interface SectionProps {
  title: string;
  subtitle?: string | ReactNode;
  children: ReactNode;
  className?: string;
  actions?: ReactNode;
}

export default function Section({
  title,
  subtitle,
  children,
  className = '',
  actions
}: SectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`overflow-hidden space-y-4 mt-4 mb-8 ${className}`}
    >
      <div className="mb-4 flex justify-between items-start border-t border-gray-300 dark:border-gray-600 pt-4">
        <div>
          <h2 className="text-xl font-semibold">{title}</h2>
          {subtitle && <p className="text-sm font-thin">{subtitle}</p>}
        </div>
        {actions && <div className="flex space-x-2">{actions}</div>}
      </div>
      {children}
    </motion.div>
  );
}
