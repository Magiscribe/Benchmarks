import { Link } from 'react-router-dom';

/**
 * Represents a single link item in the LinkStack
 */
export interface LinkItem {
  /** Optional prefix text displayed before the link */
  prefixText?: string;
  /** The text for the link itself */
  linkText: string;
  /** The destination URL for the link */
  to: string;
  /** Optional CSS class names to apply to the link */
  linkClassName?: string;
  /** Optional CSS class names to apply to the prefix text */
  prefixClassName?: string;
}

/**
 * Properties for the LinkStack component
 */
export interface LinkStackProps {
  /** Array of link items to display */
  links: LinkItem[];
  /** Optional CSS class name for the container */
  className?: string;
  /** Display links horizontally or vertically. Default is false (vertical) */
  horizontal?: boolean;
}

/**
 * LinkStack - A flexible component for displaying a collection of links
 *
 * @example
 * ```tsx
 * <LinkStack
 *   links={[
 *     { prefixText: 'New?', linkText: 'Create Account', to: '/auth/sign-up' },
 *     { linkText: 'Forgot Password?', to: '/auth/reset' }
 *   ]}
 * />
 * ```
 */
export default function LinkStack({
  links,
  className = 'flex flex-col items-center gap-2 mt-6',
  horizontal = false
}: LinkStackProps) {
  // If no links provided, don't render anything
  if (!links || links.length === 0) return null;

  return (
    <div className={className}>
      {links.map((link, index) => (
        <div
          key={index}
          className={horizontal ? 'inline-flex items-center gap-2 mx-2' : 'flex items-center gap-2'}
        >
          {link.prefixText && (
            <span className={link.prefixClassName || 'text-gray-600 dark:text-gray-400'}>
              {link.prefixText}
            </span>
          )}
          <Link className={link.linkClassName || 'link'} to={link.to}>
            {link.linkText}
          </Link>
        </div>
      ))}
    </div>
  );
}
