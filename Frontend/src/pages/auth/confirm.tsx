import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
  const location = useLocation();
  const { username, password } = location.state || {};

  const [confirmSignUpInput, setConfirmSignUpInput] = useState({
    username: username || '',
    confirmationCode: ''
  });
  const [error, setError] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  const auth = useAuth();
  const navigate = useNavigate();

  const confirm = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      await auth.confirmSignUp(confirmSignUpInput);
      await auth.signIn({
        username: confirmSignUpInput.username,
        password: password || ''
      });
      navigate('/');
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
      prefixText: t('auth.confirm.alreadyVerified'),
      linkText: t('auth.confirm.signIn'),
      to: '/auth/sign-in'
    }
  ];

  return (
    <Container>
      <PageHeader title={t('auth.confirm.title')} subtitle={t('auth.confirm.subtitle')} />
      <Banner type="error" message={error} />
      <form className="w-full flex flex-col">
        <Input
          fullWidth
          type="text"
          placeholder={t('auth.confirm.email')}
          value={confirmSignUpInput.username}
          onChange={(e) =>
            setConfirmSignUpInput({ ...confirmSignUpInput, username: e.target.value })
          }
          disabled={!!username}
        />
        <Input
          fullWidth
          type="text"
          placeholder={t('auth.confirm.code')}
          value={confirmSignUpInput.confirmationCode}
          onChange={(e) =>
            setConfirmSignUpInput({ ...confirmSignUpInput, confirmationCode: e.target.value })
          }
        />
        <Button onClick={confirm} disabled={isLoading}>
          {isLoading ? <Loading /> : t('auth.confirm.buttonText')}
        </Button>
      </form>
      <LinkStack links={authLinks} />
    </Container>
  );
}
