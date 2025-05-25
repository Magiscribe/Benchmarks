import { motion } from 'motion/react';
import { ReactNode } from 'react';

/** Motion variants for fade-in animation with staggered children */
const motionVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

/**
 * Props for the Container component
 * @interface ContainerProps
 */
interface ContainerProps {
  /** Content to be rendered inside the container */
  children: ReactNode;
  /** When true, renders a transparent container without shadow */
  hidden?: boolean;
}

/**
 * A animated container component that wraps content with optional styling
 * @param {ContainerProps} props - Component properties
 * @returns {JSX.Element} Rendered container with animated content
 */
export default function Container({ children, hidden, ...props }: ContainerProps) {
  const containerStyle = hidden
    ? 'bg-transparent shadow-none w-full my-2'
    : 'bg-gray-100 dark:bg-gray-800 w-full rounded-2xl shadow-lg p-6 my-2';

  return (
    <div className={containerStyle}>
      <motion.div
        className="flex flex-col justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        variants={motionVariants}
        transition={{ duration: 0.25 }}
        {...props}
      >
        <div className="text-gray-700 dark:text-gray-200">{children}</div>
      </motion.div>
    </div>
  );
}
