import { AnimatePresence, motion } from 'motion/react';
import { Link, useNavigate } from 'react-router-dom';
import { FC, useState } from 'react';
import { useAuth } from '@/providers/AuthProvider';
import { useDarkMode } from '@/hooks/DarkMode';
import Logo from '../Logo';
import { Icon } from '@iconify/react';
import Button from '@/components/controls/Button';
import { JSX } from 'react';
import LangSwitcher from '../LangSwitcher';

/**
 * Props for the Navbar component
 * @interface NavbarProps
 * @property {string} title - The main title to display in the logo
 * @property {string} company - The company name to display in the logo
 */
interface NavbarProps {
  title: string;
  company: string;
}

/**
 * Props for user menu components
 * @interface UserMenuProps
 * @property {string} username - The username to display
 * @property {() => void} onSignAction - Callback function for sign in/out action
 * @property {boolean} authenticated - Whether the user is authenticated
 * @property {boolean} isDark - Current dark mode state
 * @property {() => void} toggleDarkMode - Function to toggle dark mode
 */
interface UserMenuProps {
  username: string;
  onSignAction: () => void;
  authenticated: boolean;
  isDark: boolean;
  toggleDarkMode: () => void;
}

/**
 * Mobile menu component that displays user information and sign in/out button
 * @component
 * @param {UserMenuProps} props - Component properties
 * @returns {JSX.Element} Mobile menu with user information and actions
 */
const MobileMenu: FC<UserMenuProps> = ({
  username,
  onSignAction,
  authenticated,
  isDark,
  toggleDarkMode
}) => (
  <div className="px-2 pt-2 pb-3 space-y-1">
    {authenticated && (
      <div className="px-3 py-2 flex items-center gap-3">
        <UserAvatar username={username} />
      </div>
    )}
    <div className="flex gap-2">
      <Button onClick={onSignAction}>{authenticated ? 'Sign Out' : 'Sign In'}</Button>
      <Button
        onClick={toggleDarkMode}
        aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      >
        <Icon
          icon={isDark ? 'material-symbols:light-mode' : 'material-symbols:dark-mode'}
          className="h-5 w-5"
        />
      </Button>
    </div>
  </div>
);

/**
 * Desktop menu component that displays user information and sign in/out button
 * @component
 * @param {UserMenuProps} props - Component properties
 * @returns {JSX.Element} Desktop menu with user information and actions
 */
const DesktopMenu: FC<UserMenuProps> = ({
  username,
  onSignAction,
  authenticated,
  isDark,
  toggleDarkMode
}) => (
  <div className="hidden sm:flex items-center gap-4">
    {authenticated && (
      <div className="flex items-center gap-3">
        <UserAvatar username={username} />
      </div>
    )}
    <Button size="sm" variant="transparent" onClick={onSignAction}>
      {authenticated ? 'Sign Out' : 'Sign In'}
    </Button>
    <Button
      variant="transparent"
      onClick={toggleDarkMode}
      aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      <Icon
        icon={isDark ? 'material-symbols:light-mode' : 'material-symbols:dark-mode'}
        className="h-4 w-4"
      />
    </Button>
    <LangSwitcher />
  </div>
);

/**
 * User avatar component that displays the first letter of the username
 * @component
 * @param {{ username: string }} props - Component properties
 * @returns {JSX.Element} Circular avatar with user initial
 */
const UserAvatar: FC<{ username: string }> = ({ username }) => (
  <Link
    to="/auth/settings"
    className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center"
  >
    <span className="text-white font-medium text-sm">{username.charAt(0).toUpperCase()}</span>
  </Link>
);

/**
 * Main navigation bar component that provides application navigation and user controls
 * @component
 * @param {NavbarProps} props - Component properties
 * @returns {JSX.Element} Navigation bar with logo, user menu, and mobile responsiveness
 * @example
 * ```tsx
 * <Navbar
 *   title="AppName"
 *   company="CompanyName"
 * />
 * ```
 */
export default function Navbar({ title, company }: NavbarProps): JSX.Element {
  const { user, userAttributes, loaded, signOut } = useAuth();
  const { isDark, toggleDarkMode } = useDarkMode();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const authenticated = !!(user && loaded);
  const username = userAttributes?.given_name ?? userAttributes?.email ?? 'User';

  const handleSignAction = () => {
    if (authenticated) {
      signOut();
      navigate('/');
    } else {
      navigate('/auth/sign-in');
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0, y: -100 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -100 }}
        transition={{ duration: 0.25 }}
        className="bg-white/40 dark:bg-gray-900/70 backdrop-blur-sm fixed top-0 left-0 w-full shadow-md z-50"
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/">
              <Logo title={title} company={company} />
            </Link>

            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="sm:hidden p-2 rounded-md text-gray-400 hover:text-white"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMobileMenuOpen ? (
                  <Icon icon="material-symbols:close-rounded" />
                ) : (
                  <Icon icon="material-symbols:menu-rounded" />
                )}
              </svg>
            </button>

            <DesktopMenu
              username={username}
              onSignAction={handleSignAction}
              authenticated={authenticated}
              isDark={isDark}
              toggleDarkMode={toggleDarkMode}
            />
          </div>

          <AnimatePresence>
            {isMobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="sm:hidden border-t border-gray-700"
              >
                <MobileMenu
                  username={username}
                  onSignAction={handleSignAction}
                  authenticated={authenticated}
                  isDark={isDark}
                  toggleDarkMode={toggleDarkMode}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
