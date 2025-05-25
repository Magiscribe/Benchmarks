import Footer, { FooterLink } from '@/components/layouts/Footer';
import Navbar from '@/components/layouts/Navbar';
import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

/**
 * Layout component that provides the main page structure for the application.
 *
 * This component renders the main layout structure including:
 * - A container with styling for both light and dark modes
 * - The main content area via Outlet from react-router-dom
 * - The navigation bar with localized title and company
 * - The footer with localized text and configured links
 *
 * @returns {JSX.Element} The rendered layout component
 */
export default function Layout() {
  const { t } = useTranslation();

  return (
    <div className="bg-gray-300 dark:bg-gray-900 min-h-screen">
      <div className="container mx-auto flex flex-col items-center">
        <div className="flex flex-col w-full container justify-center items-center px-2 sm:px-6 lg:px-8 py-20">
          <Outlet />
        </div>
        <Navbar title={t('site.name')} company={t('site.company')} />
        <Footer
          text={t('site.footer.title')}
          links={t('site.footer.links', { returnObjects: true }) as FooterLink[]}
        />
      </div>
    </div>
  );
}
