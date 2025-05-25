import { Icon } from '@iconify/react';
import { FC } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

interface BreadcrumbProps {
  /** Custom back button label */
  backLabel?: string;
}

/**
 * Breadcrumb component displays a back navigation button
 * @component
 * @param {BreadcrumbProps} props - Component properties
 * @param {string} [props.backLabel='Back'] - Custom label for the back button
 * @returns {JSX.Element | null} Rendered breadcrumb navigation or null if on homepage
 * @example
 * ```tsx
 * <Breadcrumb backLabel="Go Back" />
 * ```
 */
const Breadcrumb: FC<BreadcrumbProps> = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const isHomePage = location.pathname === '/';

  if (isHomePage) {
    return null;
  }

  return (
    <nav className="w-full">
      <button onClick={() => navigate(-1)} className="flex items-center link font-bold">
        <Icon icon="material-symbols:arrow-left-alt-rounded" className="w-4 h-4 mr-1" />
        {t('common.back')}
      </button>
    </nav>
  );
};

export default Breadcrumb;
