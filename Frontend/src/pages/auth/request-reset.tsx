import { useState } from 'react';
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
  const [requestInput, setRequestInput] = useState({ username: '' });
  const [error, setError] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  const auth = useAuth();
  const navigate = useNavigate();

  const requestReset = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      await auth.resetPassword(requestInput);
      navigate(`/auth/reset?username=${requestInput.username}`);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
      console.error(JSON.stringify(err));
    } finally {
      setIsLoading(false);
    }
  };

  const authLinks = [
    {
      linkText: t('auth.requestReset.backToSignIn'),
      to: '/auth/sign-in'
    },
    {
      prefixText: t('auth.requestReset.noAccount'),
      linkText: t('auth.requestReset.signUp'),
      to: '/auth/sign-up'
    }
  ];

  return (
    <Container>
      <PageHeader title={t('auth.requestReset.title')} subtitle={t('auth.requestReset.subtitle')} />
      <Banner type="error" message={error} />
      <form className="w-full flex flex-col">
        <Input
          fullWidth
          type="email"
          placeholder={t('auth.requestReset.email')}
          onChange={(e) => setRequestInput({ ...requestInput, username: e.target.value })}
        />
        <Button onClick={requestReset} disabled={isLoading}>
          {isLoading ? <Loading /> : t('auth.requestReset.buttonText')}
        </Button>
      </form>
      <LinkStack links={authLinks} />
    </Container>
  );
}
