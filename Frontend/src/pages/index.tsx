import Dropdown from '@/components/controls/Dropdown';
import { Feature } from '@/components/Feature';
import Container from '@/components/layouts/Container';
import Section from '@/components/Section';
import { useAuth } from '@/providers/AuthProvider';
import { JSX, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { Banner } from '@/components/common/BannerInfo';

/**
 * Home page component that redirects to dashboard
 * @returns {JSX.Element} The rendered home page
 */
export default function Page(): JSX.Element {
  const { t } = useTranslation();
  const { user, loaded } = useAuth();
  const navigate = useNavigate();

  // Check if authentication is disabled
  const authDisabled = import.meta.env.VITE_ENABLE_COGNITO_LOGIN !== 'true' && 
                      import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER !== 'true';
  /**
   * Redirect the user to the dashboard page if they are authenticated
   * so they don't see the home page.
   */
  useEffect(() => {
    if (authDisabled) {
      // If auth is disabled, go directly to dashboard
      navigate('/dashboard');
    } else if (loaded && user) {
      navigate('/dashboard');
    } else if (loaded && !user) {
      navigate('/auth/sign-up');
    }
  }, [loaded, user, authDisabled]);

  return (
    <></>
  );
}
