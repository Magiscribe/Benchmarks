import { JSX } from 'react';

export interface FooterLink {
  /** The text to display for the link */
  label: string;
  /** The URL the link should navigate to */
  href: string;
  /** Whether the link should open in a new tab */
  external?: boolean;
}

export interface FooterProps {
  /** The name to display */
  text?: string;
  /** Additional copyright text */
  copyrightText?: string;
  /** Array of links to display in the footer */
  links?: FooterLink[];
}

/**
 * Footer component displays the copyright information and navigation links
 * @component
 * @param {FooterProps} props - Component properties
 * @param {string} [props.company='Magiscribe'] - The name to display
 * @param {string} [props.copyrightText] - Additional copyright text
 * @param {FooterLink[]} [props.links=[]] - Array of footer links
 * @returns {JSX.Element} Rendered footer with copyright information and links
 * @example
 * ```tsx
 * <Footer
 *   company="Magiscribe"
 *   copyrightText="All rights reserved"
 *   links={[
 *     { label: "Contact", href: "/contact" },
 *     { label: "IT Help", href: "https://help.example.com", external: true }
 *   ]}
 * />
 * ```
 */
export default function Footer({ text, links = [], copyrightText }: FooterProps): JSX.Element {
  return (
    <div className="fixed bottom-0 left-0 w-full px-4 py-3 sm:px-6 lg:px-8 bg-white/40 dark:bg-gray-900/70 backdrop-blur-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <span className="text-gray-800 dark:text-gray-400 text-sm tracking-wide">
          © {new Date().getFullYear()} {text}
          {copyrightText && ` • ${copyrightText}`}
        </span>

        {links.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            {links.map((link, index) => (
              <div key={link.href} className="flex items-center">
                {index > 0 && <span className="text-gray-600 mr-3">•</span>}
                <a
                  href={link.href}
                  target={link.external !== false ? '_blank' : undefined}
                  rel={link.external !== false ? 'noopener noreferrer' : undefined}
                  className="link text-sm"
                >
                  {link.label}
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
