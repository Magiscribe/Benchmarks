import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/providers/AuthProvider';
import Container from '@/components/layouts/Container';
import Loading from '@/components/Loading';
import Input from '@/components/controls/Input';
import Button from '@/components/controls/Button';
import LinkStack from '@/components/common/LinkStack';
import PageHeader from '@/components/common/PageHeader';
import Banner from '@/components/common/BannerStatus';
import { useTranslation } from 'react-i18next';

export default function Page() {
  const { t } = useTranslation();
  const [signUpInput, setSignUpInput] = useState({
    username: '',
    given_name: '',
    family_name: '',
    password: '',
    options: { userAttributes: { given_name: '', family_name: '' } }
  });
  const [error, setError] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  const auth = useAuth();
  const navigate = useNavigate();

  // Read environment variable
  const enableCognitoLogin = import.meta.env.VITE_ENABLE_COGNITO_LOGIN === 'true';

  // Redirect if Cognito login is disabled
  useEffect(() => {
    if (!enableCognitoLogin) {
      navigate('/auth/sign-in');
    }
  }, [enableCognitoLogin, navigate]);

  const signUp = async (event: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      const result = await auth.signUp(signUpInput);
      if (result?.nextStep.signUpStep === 'CONFIRM_SIGN_UP') {
        navigate('/auth/confirm', {
          state: {
            username: signUpInput.username,
            password: signUpInput.password
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

  const authLinks = [
    {
      prefixText: t('auth.signUp.haveAccount'),
      linkText: t('auth.signUp.signIn'),
      to: '/auth/sign-in'
    }
  ];

  // Return null if Cognito login is disabled to prevent rendering
  if (!enableCognitoLogin) {
    return null;
  }

  return (
    <Container>
      <PageHeader title={t('auth.signUp.title')} subtitle={t('auth.signUp.subtitle')} />
      <Banner type="error" message={error} />
      <form className="w-full flex flex-col">
        <Input
          fullWidth
          type="text"
          placeholder={t('auth.signUp.firstName')}
          value={signUpInput.options?.userAttributes.given_name}
          onChange={(e) =>
            setSignUpInput({
              ...signUpInput,
              options: {
                userAttributes: {
                  ...signUpInput.options?.userAttributes,
                  given_name: e.target.value
                }
              }
            })
          }
        />
        <Input
          fullWidth
          type="text"
          placeholder={t('auth.signUp.lastName')}
          value={signUpInput.options?.userAttributes.family_name}
          onChange={(e) =>
            setSignUpInput({
              ...signUpInput,
              options: {
                userAttributes: {
                  ...signUpInput.options?.userAttributes,
                  family_name: e.target.value
                }
              }
            })
          }
        />
        <Input
          fullWidth
          type="text"
          placeholder={t('auth.signUp.email')}
          value={signUpInput.username}
          onChange={(e) => setSignUpInput({ ...signUpInput, username: e.target.value })}
        />
        <Input
          fullWidth
          type="password"
          placeholder={t('auth.signUp.password')}
          value={signUpInput.password}
          onChange={(e) => setSignUpInput({ ...signUpInput, password: e.target.value })}
        />
        <Button onClick={signUp} disabled={isLoading}>
          {isLoading ? <Loading /> : t('auth.signUp.buttonText')}
        </Button>
      </form>
      <LinkStack links={authLinks} />
    </Container>
  );
}
