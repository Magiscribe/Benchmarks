import { FC } from 'react';

interface LogoProps {
  /** The main title text */
  title: string;
  /** The company name that appears after the divider */
  company: string;
  /** The subtitle text that appears below */
  subtitle?: string;
}

/**
 * Logo component displays the GenAI Accelerator brand logo
 * @component
 * @param {LogoProps} props - Component properties
 * @param {string} [props.title] - The main title text
 * @param {string} [props.company] - The company name
 * @returns {JSX.Element} Rendered logo with company name and title
 * @example
 * ```tsx
 * <Logo />
 * <Logo title="CustomFlow" company="ACME"  />
 * ```
 */
const Logo: FC<LogoProps> = ({ title, company }) => {
  return (
    <div className="flex flex-col leading-tight">
      <span className="text-gray-800 dark:text-gray-200 font-display text-2xl font-bold tracking-tight">
        {company} | <span className="font-thin">{title}</span>
      </span>
    </div>
  );
};

export default Logo;
