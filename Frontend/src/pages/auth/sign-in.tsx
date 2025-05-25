import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/providers/AuthProvider';
import Container from '@/components/layouts/Container';
import Loading from '@/components/Loading';
import Button from '@/components/controls/Button';
import Input from '@/components/controls/Input';
import LinkStack from '@/components/common/LinkStack';
import PageHeader from '@/components/common/PageHeader';
import Banner from '@/components/common/BannerStatus';
import { useTranslation } from 'react-i18next';

export default function Page() {
  const { t } = useTranslation();
  const [input, setInput] = useState({ username: '', password: '' });
  const [error, setError] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  const auth = useAuth();
  const navigate = useNavigate();

  // Read environment variables
  const enableCustomProvider = import.meta.env.VITE_ENABLE_CUSTOM_PROVIDER === 'true';
  const enableCognitoLogin = import.meta.env.VITE_ENABLE_COGNITO_LOGIN === 'true';
  const customProviderName = import.meta.env.VITE_CUSTOM_PROVIDER_NAME || 'Magiscribe';

  const signIn = async (event: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      const result = await auth.signIn(input);
      if (result?.nextStep.signInStep === 'CONFIRM_SIGN_UP') {
        navigate('/auth/confirm', {
          state: {
            username: input.username,
            password: input.password
          }
        });
      } else {
        navigate('/');
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
      console.error('err: ', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Add handler for custom provider sign-in
  const signInWithCustomProvider = async (event: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      // Pass empty object or specific provider info if needed by your AuthProvider logic
      await auth.signIn({} as any); 
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
      console.error('err: ', err);
      setIsLoading(false); // Ensure loading state is reset on error
    } 
    // No finally block needed here as redirect will happen on success
  };

  // Update authLinks based on enabled features
  const authLinks = [
    ...(enableCognitoLogin ? [{
      prefixText: t('auth.signIn.newUser'),
      linkText: t('auth.signIn.createAccount'),
      to: '/auth/sign-up'
    }] : []),
    ...(enableCognitoLogin ? [{
      prefixText: t('auth.signIn.forgotPassword'),
      linkText: t('auth.signIn.requestReset'),
      to: '/auth/request-reset'
    }] : [])
  ];

  // Handle case where no auth method is configured
  if (!enableCustomProvider && !enableCognitoLogin) {
    return (
      <Container>
        <PageHeader title={t('auth.signIn.title')} subtitle={t('auth.signIn.subtitle')} />
        <Banner type="error" message={t('auth.signIn.noAuthMethod')} />
      </Container>
    );
  }

  return (
    <Container>
      <PageHeader title={t('auth.signIn.title')} subtitle={t('auth.signIn.subtitle')} />
      <Banner type="error" message={error} />
      
      <form className="w-full flex flex-col">
        {/* Conditionally render Cognito login fields */}
        {enableCognitoLogin && (
          <>
            <Input
              fullWidth
              type="text"
              placeholder={t('auth.common.email')}
              onChange={(e) => setInput({ ...input, username: e.target.value })}
            />
            <Input
              fullWidth
              type="password"
              placeholder={t('auth.common.password')}
              onChange={(e) => setInput({ ...input, password: e.target.value })}
            />
            <Button onClick={signIn} disabled={isLoading}>
              {isLoading ? <Loading /> : t('auth.signIn.buttonText')}
            </Button>
          </>
        )}
        
        {/* Conditionally render Custom Provider button */}
        {enableCustomProvider && (
          <Button 
            onClick={signInWithCustomProvider} 
            disabled={isLoading}
            // Add margin-top if both buttons are potentially visible
            className={enableCognitoLogin ? "mt-4" : ""} 
          >
            {isLoading ? <Loading /> : t('auth.signIn.ssoButtonText', { provider: customProviderName })}
          </Button>
        )}
      </form>
      
      {/* Conditionally render links */}
      {authLinks.length > 0 && <LinkStack links={authLinks} />}
    </Container>
  );
}
