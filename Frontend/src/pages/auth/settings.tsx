import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/providers/AuthProvider'; // Auth provider now includes isFederatedLogin
import Container from '@/components/layouts/Container';
import Loading from '@/components/Loading';
import Button from '@/components/controls/Button';
import Input from '@/components/controls/Input';
import PageHeader from '@/components/common/PageHeader';
import Banner from '@/components/common/BannerStatus';
import Section from '@/components/Section';
import { useTranslation } from 'react-i18next';
import * as Auth from 'aws-amplify/auth';

/**
 * User Settings Page component
 * Allows users to manage their account settings including:
 * - Update personal information (first name, last name)
 * - Change password
 * - Delete account
 */
export default function UserSettingsPage() {
  const { t } = useTranslation();
  const auth = useAuth(); // Use the updated auth context
  const navigate = useNavigate();

  // State for personal info form
  const [personalInfo, setPersonalInfo] = useState({
    firstName: '',
    lastName: ''
  });

  // State for password change form
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [successMessage, setSuccessMessage] = useState<string | undefined>();

  // Confirmation state for dangerous actions
  const [confirmDelete, setConfirmDelete] = useState(false);

  // Load user data when component mounts
  useEffect(() => {
    if (auth.userAttributes) {
      setPersonalInfo({
        firstName: auth.userAttributes.given_name || '',
        lastName: auth.userAttributes.family_name || ''
      });
      // No need to calculate isFederatedLogin here anymore
    }
  }, [auth.userAttributes]);

  /**
   * Update user's personal information (first name, last name)
   */
  const updatePersonalInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(undefined);
    setSuccessMessage(undefined);

    try {
      await auth.updateUserAttributes({
        given_name: personalInfo.firstName,
        family_name: personalInfo.lastName
      });
      setSuccessMessage(t('settings.personalInfo.success'));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Change user's password
   */
  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(undefined);
    setSuccessMessage(undefined);

    // Validate matching passwords
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError(t('settings.password.mismatch'));
      setIsLoading(false);
      return;
    }

    try {
      await Auth.updatePassword({
        oldPassword: passwordData.oldPassword,
        newPassword: passwordData.newPassword
      });
      setSuccessMessage(t('settings.password.success'));
      setPasswordData({
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Delete user's account
   */
  const deleteAccount = async () => {
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }

    setIsLoading(true);
    setError(undefined);

    try {
      await Auth.deleteUser();
      await auth.signOut();
      navigate('/auth/sign-in', { state: { message: t('settings.delete.success') } });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setIsLoading(false);
      setConfirmDelete(false);
    }
  };

  // If not authenticated, redirect to login
  useEffect(() => {
    if (auth.loaded && !auth.user) {
      navigate('/auth/sign-in');
    }
  }, [auth.loaded, auth.user, navigate]);

  if (!auth.loaded || !auth.user) {
    return <Loading />;
  }

  return (
    <Container>
      <PageHeader title={t('settings.title')} subtitle={t('settings.subtitle')} />

      {error && <Banner type="error" message={error} showSupport={true} />}
      {successMessage && <Banner type="success" message={successMessage} />}

      {/* Add informational banner for federated users */}
      {auth.isFederatedLogin && ( 
        <Banner 
          type="info" 
          message={t('settings.federatedInfo.banner')} 
        />
      )}

      {/* Personal Information Section - Conditionally render */}
      {!auth.isFederatedLogin && (
        <Section
          title={t('settings.personalInfo.title')}
          subtitle={t('settings.personalInfo.subtitle')}
        >
          <form onSubmit={updatePersonalInfo} className="space-y-4">
            <div>
              <Input
                fullWidth
                type="text"
                label={t('settings.personalInfo.firstName')}
                value={personalInfo.firstName}
                onChange={(e) => setPersonalInfo({ ...personalInfo, firstName: e.target.value })}
              />
            </div>

            <div>
              <Input
                fullWidth
                type="text"
                label={t('settings.personalInfo.lastName')}
                value={personalInfo.lastName}
                onChange={(e) => setPersonalInfo({ ...personalInfo, lastName: e.target.value })}
              />
            </div>

            <Button type="submit" disabled={isLoading}>
              {isLoading ? <Loading /> : t('settings.personalInfo.save')}
            </Button>
          </form>
        </Section>
      )}

      {/* Password Change Section - Conditionally render */}
      {!auth.isFederatedLogin && (
        <Section title={t('settings.password.title')} subtitle={t('settings.password.subtitle')}>
          <form onSubmit={changePassword} className="space-y-4">
            <Input
              fullWidth
              type="password"
              label={t('settings.password.current')}
              value={passwordData.oldPassword}
              onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
            />

            <Input
              fullWidth
              type="password"
              label={t('settings.password.new')}
              value={passwordData.newPassword}
              onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
            />

            <Input
              fullWidth
              type="password"
              label={t('settings.password.confirm')}
              value={passwordData.confirmPassword}
              onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
            />

            <Button
              type="submit"
              disabled={
                isLoading ||
                !passwordData.oldPassword ||
                !passwordData.newPassword ||
                !passwordData.confirmPassword
              }
            >
              {isLoading ? <Loading /> : t('settings.password.save')}
            </Button>
          </form>
        </Section>
      )}

      {/* Display user information for federated users */}
      {auth.isFederatedLogin && (
        <Section title={t('settings.federatedInfo.title')} subtitle={t('settings.federatedInfo.subtitle')}>
          <div className="space-y-2">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="font-medium">{t('settings.federatedInfo.nameLabel')}</span>
              <span>{personalInfo.firstName} {personalInfo.lastName}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="font-medium">{t('settings.federatedInfo.emailLabel')}</span>
              <span>{auth.userAttributes?.email || t('settings.federatedInfo.noEmail')}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="font-medium">{t('settings.federatedInfo.providerLabel')}</span>
              {/* Use VITE_CUSTOM_PROVIDER_NAME for display */}
              <span>{import.meta.env.VITE_CUSTOM_PROVIDER_NAME || t('settings.federatedInfo.defaultProvider')}</span> 
            </div>
          </div>
        </Section>
      )}

      {/* Danger Zone Section */}
      <Section title={t('settings.danger.title')} subtitle={t('settings.danger.warning')}>
        {confirmDelete ? (
          <div className="space-y-2">
            <p className="font-bold text-red-600">{t('settings.delete.confirm')}</p>
            <div className="flex space-x-3">
              <Button
                onClick={deleteAccount}
                disabled={isLoading}
                className="bg-red-600 hover:bg-red-700"
              >
                {isLoading ? <Loading /> : t('settings.delete.yes')}
              </Button>
              <Button
                onClick={() => setConfirmDelete(false)}
                className="bg-gray-500 hover:bg-gray-600" // Adjusted color from slate to gray
              >
                {t('settings.delete.no')}
              </Button>
            </div>
          </div>
        ) : (
          <Button onClick={deleteAccount} className="bg-red-600 hover:bg-red-700">
            {t('settings.delete.button')}
          </Button>
        )}
      </Section>
    </Container>
  );
}
