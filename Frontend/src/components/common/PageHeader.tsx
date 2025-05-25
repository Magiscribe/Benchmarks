/**
 * Props for the PageHeader component
 */
export interface PageHeaderProps {
  /** The main title text */
  title: string;
  /** The subtitle or description text */
  subtitle?: string;
  /** Optional additional className for the container */
  className?: string;
  /** Optional className for the title */
  titleClassName?: string;
  /** Optional className for the subtitle */
  subtitleClassName?: string;
}

/**
 * PageHeader - A reusable component for displaying a page title and subtitle
 *
 * @example
 * ```tsx
 * <PageHeader
 *   title="Welcome Back"
 *   subtitle="Sign in to your account"
 * />
 * ```
 */
export default function PageHeader({
  title,
  subtitle,
  className = 'w-full my-4',
  titleClassName = 'flex text-3xl font-bold leading-tight bg-clip-text',
  subtitleClassName = 'text-gray-600 dark:text-gray-400'
}: PageHeaderProps) {
  return (
    <div className={className}>
      <h1 className={titleClassName}>{title}</h1>
      {subtitle && <p className={subtitleClassName}>{subtitle}</p>}
    </div>
  );
}
